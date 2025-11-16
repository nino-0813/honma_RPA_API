"""
BASE専用RPAスクリプト
"""
import time
from typing import List, Dict, Any, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from rpa.core.browser import create_driver
from rpa.core.login import LoginBase
from rpa.core.scraper_base import ScraperBase
from rpa.utils.config_loader import get_credentials, validate_config
from rpa.utils.data_saver import save_orders_to_supabase


class BaseLogin(LoginBase):
    """BASE専用のログイン処理"""
    
    def get_login_url(self) -> str:
        """BASEのログインページURLを返す"""
        return "https://admin.thebase.in/login"
    
    def login(self, driver: webdriver.Chrome, credentials: Dict[str, Any]) -> bool:
        """
        BASEにログイン（手動ログイン方式）
        
        Args:
            driver: WebDriverインスタンス
            credentials: ログイン情報（現在は未使用、手動ログインのため）
        
        Returns:
            bool: ログイン成功時True
        """
        login_url = self.get_login_url()
        print(f"[BASE RPA] BASEログインページを開いています... ({login_url})")
        
        try:
            driver.get(login_url)
            print("[BASE RPA] ログインページの読み込みを待機しています...")
            time.sleep(3)
            
            # 手動ログインを待機
            return self.wait_for_manual_login(driver, wait_time=120)
        except Exception as e:
            print(f"[BASE RPA] ログインページの読み込みエラー: {e}")
            return False


class BaseScraper(ScraperBase):
    """BASE専用のスクレイパー"""
    
    def __init__(self, driver: webdriver.Chrome):
        super().__init__(driver, "base")
    
    def get_orders_url(self) -> str:
        """BASEの注文一覧ページURLを返す"""
        return "https://admin.thebase.in/shop_admin/orders/"
    
    def scrape_orders(self, max_orders: Optional[int] = 10) -> List[Dict[str, Any]]:
        """
        BASEの注文データをスクレイピング
        
        Args:
            max_orders: 取得する最大注文数
        
        Returns:
            List[Dict[str, Any]]: 注文データのリスト
        """
        orders = []
        
        try:
            print("[BASE RPA] 注文情報を取得しています...")
            
            # 注文行を検索（複数のセレクタを試す）
            order_selectors = [
                ".order-list-row",
                ".order-row",
                "[data-order-id]",
                "tr.order-row",
                ".order-item"
            ]
            
            order_rows = []
            for selector in order_selectors:
                try:
                    order_rows = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if order_rows:
                        print(f"[BASE RPA] セレクタ '{selector}' で {len(order_rows)}件の注文を検出しました")
                        break
                except:
                    continue
            
            if not order_rows:
                print("[BASE RPA] 注文が見つかりませんでした。ページの構造を確認してください。")
                return orders
            
            # 最大注文数まで取得
            target_orders = order_rows[:max_orders] if max_orders else order_rows
            print(f"[BASE RPA] {len(target_orders)}件の注文を取得します")
            
            for idx, row in enumerate(target_orders):
                try:
                    # 注文IDを取得
                    order_id = None
                    order_id_selectors = [".order-id", "[data-order-id]", ".order-number", "td:first-child"]
                    
                    for selector in order_id_selectors:
                        try:
                            if selector.startswith("td"):
                                order_id_elem = row.find_element(By.CSS_SELECTOR, selector)
                            else:
                                order_id_elem = row.find_element(By.CSS_SELECTOR, selector)
                            order_id = order_id_elem.text.strip()
                            if order_id:
                                break
                        except:
                            continue
                    
                    if not order_id:
                        order_id = f"BASE-{idx+1}-{int(time.time())}"
                    
                    # 顧客名を取得
                    customer = "取得不可"
                    customer_selectors = [".order-customer", ".customer-name", ".buyer-name", "td:nth-child(2)"]
                    for selector in customer_selectors:
                        try:
                            customer_elem = row.find_element(By.CSS_SELECTOR, selector)
                            customer = customer_elem.text.strip()
                            if customer:
                                break
                        except:
                            continue
                    
                    # 合計金額を取得
                    total = "取得不可"
                    total_selectors = [".order-total", ".total-price", ".amount", "td:last-child"]
                    for selector in total_selectors:
                        try:
                            total_elem = row.find_element(By.CSS_SELECTOR, selector)
                            total = total_elem.text.strip()
                            if total:
                                break
                        except:
                            continue
                    
                    orders.append({
                        "order_id": order_id,
                        "customer": customer,
                        "total": total,
                        "platform": "base"
                    })
                    
                except Exception as e:
                    print(f"[BASE RPA] 注文{idx+1}の取得でエラー: {e}")
                    continue
            
            print(f"[BASE RPA] {len(orders)}件の注文を取得しました")
            return orders
            
        except Exception as e:
            print(f"[BASE RPA] 注文取得エラー: {e}")
            import traceback
            traceback.print_exc()
            return orders


def run_base_rpa(
    job_id: Optional[str] = None,
    user_id: Optional[str] = None,
    credentials: Optional[Dict[str, Any]] = None
) -> bool:
    """
    BASE RPAを実行
    
    Args:
        job_id: ジョブID
        user_id: ユーザーID
        credentials: ログイン情報（未指定の場合は環境変数から取得）
    
    Returns:
        bool: 実行成功時True
    """
    print(f"[BASE RPA] ジョブ開始: {job_id}")
    
    # 設定の検証
    if not validate_config():
        print("[BASE RPA] 設定の検証に失敗しました。")
        return False
    
    # 認証情報の取得
    if not credentials:
        credentials = get_credentials(user_id)
    
    driver = None
    try:
        # ChromeDriverを起動
        print("[BASE RPA] ChromeDriverを起動しています...")
        driver = create_driver(headless=False)
        print("[BASE RPA] ChromeDriverの起動に成功しました")
        
        # ログイン処理
        login_handler = BaseLogin()
        if not login_handler.login(driver, credentials):
            print("[BASE RPA] ログインに失敗しました。")
            return False
        
        # 注文ページに遷移
        scraper = BaseScraper(driver)
        if not scraper.navigate_to_orders_page():
            print("[BASE RPA] 注文ページへの遷移に失敗しました。")
            return False
        
        # 注文データをスクレイピング
        orders = scraper.scrape_orders(max_orders=10)
        
        # Supabaseに保存
        if orders:
            save_orders_to_supabase(
                orders=orders,
                platform="base",
                user_id=user_id,
                job_id=job_id
            )
        else:
            print("[BASE RPA] 取得できる注文がありませんでした")
        
        print("\n[BASE RPA] RPA実行が完了しました")
        print("[BASE RPA] ブラウザを開いたままにします。結果を確認してから、ブラウザを手動で閉じてください。")
        
        # ブラウザが閉じられるまで待機（最大5分）
        try:
            for i in range(300):
                try:
                    driver.current_url
                    time.sleep(1)
                except:
                    print("[BASE RPA] ブラウザが閉じられました。")
                    break
        except:
            pass
        
        return True
        
    except KeyboardInterrupt:
        print("\n[BASE RPA] ユーザーによって中断されました。")
        if driver:
            print("[BASE RPA] ブラウザを開いたままにします。手動で閉じてください。")
        return False
        
    except Exception as e:
        print(f"\n[BASE RPA] エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        if driver:
            print("[BASE RPA] ブラウザを開いたままにします。手動で閉じてください。")
        return False


if __name__ == "__main__":
    import sys
    
    # コマンドライン引数からjob_idとuser_idを取得
    job_id = None
    user_id = None
    
    if len(sys.argv) > 1:
        for i, arg in enumerate(sys.argv):
            if arg == "--job-id" and i + 1 < len(sys.argv):
                job_id = sys.argv[i + 1]
            elif arg == "--user-id" and i + 1 < len(sys.argv):
                user_id = sys.argv[i + 1]
    
    run_base_rpa(job_id=job_id, user_id=user_id)

