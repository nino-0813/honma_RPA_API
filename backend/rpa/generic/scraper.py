"""
汎用RPAスクレイパー（Selenium）
"""
import time
import json
import re
from typing import Optional, Dict, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

from rpa.core.browser import create_driver


class GenericScraper:
    """汎用スクレイパー"""
    
    def __init__(self, headless: bool = False):
        """
        初期化
        
        Args:
            headless: ヘッドレスモードで実行するか
        """
        self.headless = headless
        self.driver: Optional[webdriver.Chrome] = None
    
    def start(self) -> None:
        """ブラウザを起動"""
        print("[Generic Scraper] ChromeDriverを起動しています...")
        self.driver = create_driver(headless=self.headless)
        print("[Generic Scraper] ChromeDriverの起動に成功しました")
    
    def navigate_to_login(self, login_url: str, wait_time: int = 120) -> bool:
        """
        ログイン後のURLに移動し、ユーザーがログインするまで待機
        ログインが完了したら自動的に次のステップに進む
        
        Args:
            login_url: ログイン後のURL
            wait_time: 最大ログイン待機時間（秒、デフォルト120秒）
        
        Returns:
            bool: 移動成功時True
        """
        if not self.driver:
            raise RuntimeError("ブラウザが起動していません。start()を先に呼び出してください。")
        
        try:
            print("\n" + "="*60)
            print("【ステップ1】ログイン後URLに移動します")
            print("="*60)
            print(f"[Generic Scraper] ログイン後URLに移動しています... ({login_url})")
            
            # ブラウザを前面に表示（macOS用）
            try:
                self.driver.execute_script("window.focus();")
            except:
                pass
            
            self.driver.get(login_url)
            print("[Generic Scraper] ページの読み込みを待機しています...")
            time.sleep(3)
            
            # ページが読み込まれたか確認
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            initial_url = self.driver.current_url
            print(f"[Generic Scraper] ✓ ログイン後URLへの移動が完了しました")
            print(f"[Generic Scraper] 現在のURL: {initial_url}")
            
            # ログインページかどうかを判定（BASEの場合）
            lower_initial = initial_url.lower()
            is_login_page = "/users/login" in lower_initial or "/login" in lower_initial
            
            # すでに管理画面（/shop_admin や /dashboard）にいる場合は即座に次へ
            if "shop_admin" in lower_initial or "/dashboard" in lower_initial:
                print("[Generic Scraper] ✓ すでに管理画面にいるため、ログイン完了とみなして次のステップに進みます...")
                return True
            
            print("\n" + "="*60)
            print("【重要】ブラウザが開きました。")
            print("以下の手順でログインしてください：")
            print("1. ブラウザでログインしてください")
            print("2. ログインが完了すると、自動的に次のステップに進みます")
            print(f"3. 最大{wait_time}秒待機します（ログイン完了を検知したら即座に進みます）")
            print("="*60 + "\n")
            
            # ログイン完了を検知するまで待機
            check_interval = 1  # 1秒ごとにチェック
            waited_time = 0
            login_detected = False
            
            while waited_time < wait_time:
                try:
                    current_url = self.driver.current_url
                    lower_url = current_url.lower()
                    
                    # 2段階認証の確認画面（メール認証など）は「ログイン完了」とみなさない
                    is_two_factor = "verify_two_factor" in lower_url or "two_factor" in lower_url
                    
                    # 管理画面のURLかどうか（BASEの例: /shop_admin, /dashboard）
                    is_admin_area = "shop_admin" in lower_url or "/dashboard" in lower_url
                    
                    # ログインページから管理画面に遷移したらログイン完了とみなす
                    if is_admin_area:
                        login_detected = True
                        print(f"\n[Generic Scraper] ✓ ログイン完了を検知しました！（{waited_time}秒後）")
                        print(f"[Generic Scraper] 現在のURL: {current_url}")
                        break
                    
                    # ログインフォームが消えたかチェック（BASEの場合）
                    try:
                        # ログインフォームの要素を探す
                        login_form = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="password"], input[name*="password"], form[action*="login"]')
                        if not login_form and is_admin_area and not is_two_factor:
                            # ログインフォームがなく、かつ管理画面にいる場合はログイン完了とみなす
                            login_detected = True
                            print(f"\n[Generic Scraper] ✓ ログイン完了を検知しました！（{waited_time}秒後）")
                            print(f"[Generic Scraper] 現在のURL: {current_url}")
                            break
                    except:
                        pass
                    
                    # 5秒ごとに進捗を表示
                    if waited_time % 5 == 0 and waited_time > 0:
                        remaining = wait_time - waited_time
                        print(f"[Generic Scraper] ⏳ ログイン待機中... あと最大{remaining}秒（ログイン完了を検知したら即座に進みます）")
                    
                    time.sleep(check_interval)
                    waited_time += check_interval
                    
                except Exception as e:
                    # エラーが発生しても続行
                    time.sleep(check_interval)
                    waited_time += check_interval
            
            if not login_detected:
                print(f"\n[Generic Scraper] ⚠ {wait_time}秒経過しました。タイムアウトですが、次のステップに進みます...")
                print(f"[Generic Scraper] 現在のURL: {self.driver.current_url}")
            
            return True
        except Exception as e:
            print(f"[Generic Scraper] ✗ ログイン後URLへの移動エラー: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def navigate_to_target(self, target_url: str) -> bool:
        """
        ターゲットURLに移動（可視化のため、ブラウザで実際に移動する）
        
        Args:
            target_url: データ取得対象のURL
        
        Returns:
            bool: 移動成功時True
        """
        if not self.driver:
            raise RuntimeError("ブラウザが起動していません。start()を先に呼び出してください。")
        
        try:
            print("\n" + "="*60)
            print("【ステップ2】取得したいURLに移動します")
            print("="*60)
            print(f"[Generic Scraper] ターゲットURLに移動しています... ({target_url})")
            
            # ブラウザを前面に表示（macOS用）
            try:
                self.driver.execute_script("window.focus();")
            except:
                pass
            
            self.driver.get(target_url)
            print("[Generic Scraper] ページの読み込みを待機しています...")
            time.sleep(5)  # ページの読み込みを待つ（SPAの場合はJavaScriptの実行も待つ）
            
            # ページが読み込まれたか確認
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 追加の待機（SPAの場合はJavaScriptの実行を待つ）
            print("[Generic Scraper] ページのコンテンツ読み込みを待機中...")
            time.sleep(3)
            
            current_url = self.driver.current_url
            print(f"[Generic Scraper] ✓ ターゲットURLへの移動が完了しました")
            print(f"[Generic Scraper] 現在のURL: {current_url}")
            print("="*60 + "\n")
            return True
        except Exception as e:
            print(f"[Generic Scraper] ✗ ターゲットURLへの移動エラー: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_page_source(self) -> str:
        """
        現在のページのソースを取得
        
        Returns:
            str: ページのHTMLソース
        """
        if not self.driver:
            raise RuntimeError("ブラウザが起動していません。")
        return self.driver.page_source
    
    def get_current_url(self) -> str:
        """
        現在のURLを取得
        
        Returns:
            str: 現在のURL
        """
        if not self.driver:
            raise RuntimeError("ブラウザが起動していません。")
        return self.driver.current_url
    
    def execute_script(self, script: str) -> Any:
        """
        JavaScriptを実行
        
        Args:
            script: 実行するJavaScriptコード
        
        Returns:
            Any: 実行結果
        """
        if not self.driver:
            raise RuntimeError("ブラウザが起動していません。")
        return self.driver.execute_script(script)
    
    def wait_for_element(self, selector: str, timeout: int = 10) -> bool:
        """
        要素が表示されるまで待機
        
        Args:
            selector: CSSセレクタ
            timeout: タイムアウト（秒）
        
        Returns:
            bool: 要素が見つかった場合True
        """
        if not self.driver:
            raise RuntimeError("ブラウザが起動していません。")
        
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return True
        except:
            return False
    
    def extract_json_from_api(self, api_url: str) -> Optional[Dict[str, Any]]:
        """
        APIエンドポイントからJSONデータを取得（BASE用）
        
        Args:
            api_url: APIエンドポイントのURL
        
        Returns:
            Optional[Dict[str, Any]]: 取得したJSONデータ、失敗時はNone
        """
        if not self.driver:
            raise RuntimeError("ブラウザが起動していません。")
        
        try:
            print(f"[Generic Scraper] APIからJSONデータを取得しています... ({api_url})")
            
            # JavaScriptでfetch APIを使用してJSONを取得
            js_code = f"""
            return fetch('{api_url}', {{
                method: 'GET',
                credentials: 'include',
                headers: {{
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }}
            }})
            .then(response => {{
                if (!response.ok) {{
                    throw new Error('HTTP error! status: ' + response.status);
                }}
                return response.json();
            }})
            .then(data => {{
                return data;
            }})
            .catch(error => {{
                console.error('Fetch error:', error);
                return null;
            }});
            """
            
            # execute_async_scriptを使用してPromiseを待機
            json_data = self.driver.execute_async_script(f"""
                var callback = arguments[arguments.length - 1];
                ({js_code})()
                .then(result => callback(result))
                .catch(error => callback({{error: error.toString()}}));
            """)
            
            if json_data and 'error' not in json_data:
                print("[Generic Scraper] APIからJSONデータを取得しました")
                return json_data
            elif json_data and 'error' in json_data:
                print(f"[Generic Scraper] API取得エラー: {json_data['error']}")
                # フォールバック: 通常のGETリクエストを試みる
                return self._extract_json_from_api_fallback(api_url)
            else:
                print("[Generic Scraper] APIからJSONデータが取得できませんでした")
                # フォールバック: 通常のGETリクエストを試みる
                return self._extract_json_from_api_fallback(api_url)
                
        except Exception as e:
            print(f"[Generic Scraper] API取得エラー: {e}")
            # フォールバック: 通常のGETリクエストを試みる
            return self._extract_json_from_api_fallback(api_url)
    
    def _extract_json_from_api_fallback(self, api_url: str) -> Optional[Dict[str, Any]]:
        """
        APIエンドポイントからJSONデータを取得（フォールバック方法）
        
        Args:
            api_url: APIエンドポイントのURL
        
        Returns:
            Optional[Dict[str, Any]]: 取得したJSONデータ、失敗時はNone
        """
        try:
            print(f"[Generic Scraper] フォールバック方法でAPIからJSONデータを取得しています... ({api_url})")
            self.driver.get(api_url)
            time.sleep(3)  # ページの読み込みを待つ
            
            # ページのテキストを取得（JSONレスポンス）
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            # JSONをパース
            json_data = json.loads(page_text)
            print("[Generic Scraper] フォールバック方法でAPIからJSONデータを取得しました")
            return json_data
        except json.JSONDecodeError as e:
            print(f"[Generic Scraper] JSON解析エラー: {e}")
            print(f"[Generic Scraper] レスポンス（最初の500文字）: {page_text[:500] if 'page_text' in locals() else 'N/A'}")
            return None
        except Exception as e:
            print(f"[Generic Scraper] フォールバックAPI取得エラー: {e}")
            return None
    
    def extract_json_from_script_tags(self) -> Optional[Dict[str, Any]]:
        """
        ページ内のscriptタグからJSONデータを抽出（BASE用）
        
        Returns:
            Optional[Dict[str, Any]]: 抽出したJSONデータ、見つからない場合はNone
        """
        if not self.driver:
            raise RuntimeError("ブラウザが起動していません。")
        
        try:
            # 方法1: <script id="__NEXT_DATA__">を検索（Next.jsアプリ）
            try:
                next_data_script = self.driver.find_element(By.CSS_SELECTOR, 'script#__NEXT_DATA__')
                script_text = next_data_script.get_attribute("innerHTML")
                if script_text:
                    json_data = json.loads(script_text)
                    print("[Generic Scraper] __NEXT_DATA__からJSONを抽出しました")
                    return json_data
            except:
                pass
            
            # 方法2: <script data-json>を検索
            try:
                json_scripts = self.driver.find_elements(By.CSS_SELECTOR, 'script[data-json]')
                for script in json_scripts:
                    script_text = script.get_attribute("innerHTML") or script.get_attribute("data-json")
                    if script_text:
                        json_data = json.loads(script_text)
                        print("[Generic Scraper] data-json属性からJSONを抽出しました")
                        return json_data
            except:
                pass
            
            # 方法3: すべてのscriptタグを検索して、order_headerを含むものを探す
            scripts = self.driver.find_elements(By.TAG_NAME, "script")
            for script in scripts:
                script_text = script.get_attribute("innerHTML") or script.get_attribute("textContent")
                if not script_text:
                    continue
                
                # BASEのorder_header JSONを検索
                # パターン: "order_header": { ... } または order_header: { ... }
                match = re.search(r'["\']?order_header["\']?\s*:\s*({.+?})(?=,|\s*$|\s*})', script_text, re.DOTALL)
                if match:
                    try:
                        # マッチした部分をJSONとして解析
                        json_str = match.group(1)
                        # 不完全なJSONの可能性があるので、全体のコンテキストを確認
                        # より広い範囲でマッチングを試みる
                        wider_match = re.search(r'({.*?"order_header".*?})', script_text, re.DOTALL)
                        if wider_match:
                            json_str = wider_match.group(1)
                            json_data = json.loads(json_str)
                            print("[Generic Scraper] order_headerを含むJSONを抽出しました")
                            return json_data
                    except json.JSONDecodeError:
                        continue
                
                # パターン4: window.__INITIAL_STATE__ = {...}
                match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.+?});', script_text, re.DOTALL)
                if match:
                    try:
                        json_str = match.group(1)
                        json_data = json.loads(json_str)
                        print("[Generic Scraper] window.__INITIAL_STATE__からJSONを抽出しました")
                        return json_data
                    except json.JSONDecodeError:
                        continue
            
            # 方法4: JavaScriptで直接データを取得
            try:
                js_code = """
                if (window.__NEXT_DATA__) {
                    return window.__NEXT_DATA__;
                }
                if (window.__INITIAL_STATE__) {
                    return window.__INITIAL_STATE__;
                }
                if (window.orderData) {
                    return window.orderData;
                }
                // BASEの注文データを探す
                var scripts = document.querySelectorAll('script');
                for (var i = 0; i < scripts.length; i++) {
                    var text = scripts[i].innerHTML || scripts[i].textContent;
                    if (text && text.includes('order_header')) {
                        try {
                            var match = text.match(/order_header["\']?\\s*:\\s*({.+?})/);
                            if (match) {
                                return JSON.parse('{' + match[0] + '}');
                            }
                        } catch(e) {}
                    }
                }
                return null;
                """
                result = self.driver.execute_script(f"return ({js_code})();")
                if result:
                    print("[Generic Scraper] JavaScript実行でJSONを取得しました")
                    return result
            except Exception as e:
                print(f"[Generic Scraper] JavaScript実行エラー: {e}")
            
            print("[Generic Scraper] scriptタグからJSONデータが見つかりませんでした")
            return None
            
        except Exception as e:
            print(f"[Generic Scraper] JSON抽出エラー: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def extract_base_order_json(self, target_url: str) -> Optional[Dict[str, Any]]:
        """
        BASEの注文詳細ページからJSONデータを抽出
        
        Args:
            target_url: ターゲットURL
        
        Returns:
            Optional[Dict[str, Any]]: 抽出したJSONデータ
        """
        if not self.driver:
            raise RuntimeError("ブラウザが起動していません。")
        
        current_url = self.driver.current_url
        print(f"[Generic Scraper] 現在のURL: {current_url}")
        
        # 方法1: APIエンドポイントから直接取得を試みる
        # BASEの注文詳細URLからORDER_IDを抽出（数字または英数字のIDに対応）
        order_id_match = re.search(r'/orders/order/([A-Z0-9]+)', target_url, re.IGNORECASE)
        if not order_id_match:
            # 現在のURLからも抽出を試みる
            order_id_match = re.search(r'/orders/order/([A-Z0-9]+)', current_url, re.IGNORECASE)
        
        if order_id_match:
            order_id = order_id_match.group(1)
            api_url = f"https://admin.thebase.in/shop_admin/api/orders/view/order/{order_id}"
            print(f"[Generic Scraper] BASE APIエンドポイントを試みます: {api_url}")
            json_data = self.extract_json_from_api(api_url)
            if json_data:
                return json_data
        
        # 方法2: 注文一覧ページから最初の注文IDを取得してAPIにアクセス
        if '/orders/' in current_url and '/order/' not in current_url:
            print("[Generic Scraper] 注文一覧ページを検出しました。最初の注文IDを取得します...")
            try:
                # 注文一覧ページから最初の注文リンクを探す
                order_links = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/orders/order/"]')
                if order_links:
                    first_order_link = order_links[0]
                    order_href = first_order_link.get_attribute('href')
                    print(f"[Generic Scraper] 最初の注文リンクを発見: {order_href}")
                    
                    # リンクから注文IDを抽出
                    order_id_match = re.search(r'/orders/order/([A-Z0-9]+)', order_href, re.IGNORECASE)
                    if order_id_match:
                        order_id = order_id_match.group(1)
                        api_url = f"https://admin.thebase.in/shop_admin/api/orders/view/order/{order_id}"
                        print(f"[Generic Scraper] 注文ID {order_id} のAPIエンドポイントにアクセスします: {api_url}")
                        json_data = self.extract_json_from_api(api_url)
                        if json_data:
                            return json_data
            except Exception as e:
                print(f"[Generic Scraper] 注文一覧ページからの注文ID取得エラー: {e}")
        
        # 方法3: ページ内のscriptタグから抽出
        print("[Generic Scraper] ページ内のscriptタグからJSONを抽出します...")
        return self.extract_json_from_script_tags()
    
    def quit(self) -> None:
        """ブラウザを閉じる（close()のエイリアス）"""
        self.close()
    
    def close(self) -> None:
        """ブラウザを閉じる"""
        if self.driver:
            print("[Generic Scraper] ブラウザを閉じます...")
            self.driver.quit()
            self.driver = None

