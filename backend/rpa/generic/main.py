"""
汎用RPA実行スクリプト
"""
import sys
import time
import json
import os
from typing import Optional, Dict, Any
from rpa.generic.config import GenericRPAConfig
from rpa.generic.scraper import GenericScraper
from rpa.generic.parser import GenericParser
from rpa.generic.supabase_client import GenericSupabaseClient


def run_generic_rpa(
    login_url: str,
    target_url: str,
    headless: bool = False,
    supabase_url: Optional[str] = None,
    supabase_key: Optional[str] = None,
    platform: Optional[str] = None,
    user_id: Optional[str] = None,
    job_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    汎用RPAを実行
    
    Args:
        login_url: ログイン後のURL（クッキーが有効な状態）
        target_url: データ取得対象のURL
        headless: ヘッドレスモードで実行するか
        supabase_url: Supabase URL（未指定の場合は環境変数から取得）
        supabase_key: Supabase Key（未指定の場合は環境変数から取得）
        platform: プラットフォーム名（base, shopify, rakuten, furusato, tabechoku）
        user_id: ユーザーID（RLS用）
        job_id: RPA実行ジョブID
    
    Returns:
        Dict[str, Any]: 実行結果 {success: bool, saved_records: Dict[str, int], message: str}
    """
    print("="*60)
    print("汎用RPAを開始します")
    print("="*60)
    print(f"ログイン後URL: {login_url}")
    print(f"ターゲットURL: {target_url}")
    print(f"ヘッドレスモード: {headless}")
    print("="*60)
    
    scraper = None
    try:
        # 1. 設定の初期化
        config = GenericRPAConfig(
            login_url=login_url,
            target_url=target_url,
            supabase_url=supabase_url,
            supabase_key=supabase_key,
            platform=platform,
            headless=headless,
            user_id=user_id
        )
        
        if not config.validate():
            print("[Generic RPA] 設定の検証に失敗しました")
            return {
                "success": False,
                "saved_records": {"customers": 0, "orders": 0, "items": 0},
                "message": "設定の検証に失敗しました"
            }
        
        # 2. スクレイパーの起動（可視化のため、ヘッドレスモードは強制的にfalse）
        # ユーザーがブラウザの動作を見られるようにする
        actual_headless = False  # 可視化のため、常にfalseにする
        if headless:
            print("[Generic RPA] ⚠ ヘッドレスモードが指定されましたが、可視化のためブラウザを表示します")
        
        scraper = GenericScraper(headless=actual_headless)
        scraper.start()
        
        print("\n" + "="*60)
        print("【RPA実行開始】ブラウザが開きました")
        print("="*60)
        print("以下のステップで実行されます：")
        print("1. ログイン後URLに移動")
        print("2. 取得したいURLに移動")
        print("3. データを取得してSupabaseに保存")
        print("="*60 + "\n")
        
        # 3. ログイン後URLに移動し、ユーザーがログインするまで待機（120秒）
        if not scraper.navigate_to_login(config.login_url, wait_time=120):
            print("[Generic RPA] ✗ ログイン後URLへの移動に失敗しました")
            return {
                "success": False,
                "saved_records": {"customers": 0, "orders": 0, "items": 0},
                "message": "ログイン後URLへの移動に失敗しました"
            }
        
        # 4. ターゲットURLに移動
        if not scraper.navigate_to_target(config.target_url):
            print("[Generic RPA] ✗ ターゲットURLへの移動に失敗しました")
            return {
                "success": False,
                "saved_records": {"customers": 0, "orders": 0, "items": 0},
                "message": "ターゲットURLへの移動に失敗しました"
            }
        
        # 5. JSONデータを抽出（プラットフォームに応じた抽出方法を使用）
        print("\n" + "="*60)
        print("【ステップ3】データを取得します")
        print("="*60)
        
        parser = GenericParser(scraper.driver)
        
        # BASEの場合は専用の抽出ロジックを使用
        if platform == "base":
            json_data = scraper.extract_base_order_json(config.target_url)
        else:
            json_data = parser.extract_json_from_page(platform=platform)
        
        if not json_data:
            print("[Generic RPA] ページからJSONデータを取得できませんでした")
            print("[Generic RPA] ページのソースを確認してください")
            # デバッグ用にページソースを保存
            with open("debug_page_source.html", "w", encoding="utf-8") as f:
                f.write(scraper.get_page_source())
            print("[Generic RPA] ページソースを debug_page_source.html に保存しました")
            return {
                "success": False,
                "saved_records": {"customers": 0, "orders": 0, "items": 0},
                "message": "ページからJSONデータを取得できませんでした"
            }
        
        print("[Generic RPA] JSONデータの抽出が完了しました")
        print(f"[Generic RPA] 取得したJSONデータ（最初の500文字）: {str(json_data)[:500]}")
        
        # デバッグ用にJSONデータをファイルに保存
        debug_dir = "debug_json"
        os.makedirs(debug_dir, exist_ok=True)
        debug_file = os.path.join(debug_dir, f"order_data_{int(time.time())}.json")
        with open(debug_file, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        print(f"[Generic RPA] JSONデータを {debug_file} に保存しました")
        
        # 6. JSONデータを解析
        parsed_data = parser.parse_base_order_json(json_data)
        print("[Generic RPA] JSONデータの解析が完了しました")
        print(f"[Generic RPA] 解析結果:")
        print(f"  - 顧客情報: {parsed_data.get('customer', {})}")
        print(f"  - 注文情報: {parsed_data.get('order', {})}")
        print(f"  - 商品数: {len(parsed_data.get('order_items', []))}")
        
        # 7. Supabaseに保存
        print("\n" + "="*60)
        print("【ステップ4】Supabaseに保存します")
        print("="*60)
        
        supabase_client = GenericSupabaseClient(config)
        print(f"[Generic RPA] Platform: {platform}, User ID: {user_id}, Job ID: {job_id}")
        saved_records = supabase_client.save_order_data(parsed_data, platform=platform, user_id=user_id, job_id=job_id)
        
        total_saved = sum(saved_records.values())
        if total_saved > 0:
            print("\n" + "="*60)
            print("【完了】汎用RPAの実行が正常に完了しました")
            print("="*60)
            print(f"✓ 保存レコード:")
            print(f"  - 顧客: {saved_records['customers']}件")
            print(f"  - 注文: {saved_records['orders']}件")
            print(f"  - 商品: {saved_records['items']}件")
            print("="*60)
            print("ブラウザは開いたままです。結果を確認してから、手動で閉じてください。")
            print("="*60 + "\n")
            return {
                "success": True,
                "saved_records": saved_records,
                "message": f"RPA実行が完了しました。保存レコード: 顧客={saved_records['customers']}, 注文={saved_records['orders']}, 商品={saved_records['items']}"
            }
        else:
            print("\n" + "="*60)
            print("【エラー】汎用RPAの実行中にエラーが発生しました（データが保存されませんでした）")
            print("="*60)
            print("ブラウザは開いたままです。ページを確認して、問題を特定してください。")
            print("="*60 + "\n")
            return {
                "success": False,
                "saved_records": saved_records,
                "message": "データが保存されませんでした"
            }
        
    except KeyboardInterrupt:
        print("\n[Generic RPA] ユーザーによって中断されました")
        return {
            "success": False,
            "saved_records": {"customers": 0, "orders": 0, "items": 0},
            "message": "ユーザーによって中断されました"
        }
        
    except Exception as e:
        print(f"\n[Generic RPA] エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "saved_records": {"customers": 0, "orders": 0, "items": 0},
            "message": f"エラーが発生しました: {str(e)}"
        }
        
    finally:
        if scraper and scraper.driver:
            # 可視化のため、常にブラウザを開いたままにする
            print("\n" + "="*60)
            print("【ブラウザの状態】")
            print("="*60)
            print("ブラウザは開いたままです。")
            print("結果を確認してから、手動でブラウザを閉じてください。")
            print("="*60 + "\n")
            
            # ブラウザが閉じられるまで待機（最大10分）
            try:
                print("[Generic RPA] ブラウザが閉じられるまで待機します（最大10分）...")
                for i in range(600):
                    try:
                        scraper.driver.current_url
                        if i % 60 == 0 and i > 0:  # 1分ごとに表示
                            remaining_minutes = (600 - i) // 60
                            print(f"[Generic RPA] ブラウザは開いています... あと約{remaining_minutes}分待機します")
                        time.sleep(1)
                    except:
                        print("[Generic RPA] ✓ ブラウザが閉じられました。")
                        break
            except:
                pass


if __name__ == "__main__":
    # コマンドライン引数からパラメータを取得
    login_url = None
    target_url = None
    headless = False
    
    if len(sys.argv) < 3:
        print("使用方法:")
        print("  python main.py <LOGIN_URL> <TARGET_URL> [--headless]")
        print("")
        print("例:")
        print("  python main.py 'https://admin.thebase.in/shop_admin' 'https://admin.thebase.in/shop_admin/orders/order/12345'")
        print("  python main.py 'https://admin.thebase.in/shop_admin' 'https://admin.thebase.in/shop_admin/orders/order/12345' --headless")
        sys.exit(1)
    
    login_url = sys.argv[1]
    target_url = sys.argv[2]
    
    if "--headless" in sys.argv:
        headless = True
    
    success = run_generic_rpa(
        login_url=login_url,
        target_url=target_url,
        headless=headless
    )
    
    sys.exit(0 if success else 1)

