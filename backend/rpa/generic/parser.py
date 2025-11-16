"""
汎用RPAパーサー（JSON/HTML解析）
"""
import json
import re
import time
from typing import Dict, Any, List, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By


class GenericParser:
    """汎用パーサー（BASEの注文詳細JSONに対応）"""
    
    def __init__(self, driver: webdriver.Chrome):
        """
        初期化
        
        Args:
            driver: WebDriverインスタンス
        """
        self.driver = driver
    
    def extract_json_from_page(self, platform: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        ページからJSONデータを抽出（BASEの注文詳細ページ対応）
        
        Args:
            platform: プラットフォーム名（baseの場合はBASE専用ロジックを使用）
        
        Returns:
            Optional[Dict[str, Any]]: 抽出したJSONデータ、見つからない場合はNone
        """
        try:
            # BASEの場合は専用の抽出ロジックを使用
            if platform == "base":
                current_url = self.driver.current_url
                return self._extract_base_json(current_url)
            
            # 汎用の抽出ロジック
            # 方法1: <script id="__NEXT_DATA__">を検索（Next.jsアプリ）
            try:
                next_data_script = self.driver.find_element(By.CSS_SELECTOR, 'script#__NEXT_DATA__')
                script_text = next_data_script.get_attribute("innerHTML")
                if script_text:
                    json_data = json.loads(script_text)
                    print("[Generic Parser] __NEXT_DATA__からJSONを抽出しました")
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
                        print("[Generic Parser] data-json属性からJSONを抽出しました")
                        return json_data
            except:
                pass
            
            # 方法3: すべてのscriptタグを検索
            scripts = self.driver.find_elements(By.TAG_NAME, "script")
            for script in scripts:
                script_text = script.get_attribute("innerHTML") or script.get_attribute("textContent")
                if not script_text:
                    continue
                
                # パターン1: window.__INITIAL_STATE__ = {...}
                match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.+?});', script_text, re.DOTALL)
                if match:
                    try:
                        json_str = match.group(1)
                        data = json.loads(json_str)
                        print("[Generic Parser] window.__INITIAL_STATE__からJSONを抽出しました")
                        return data
                    except json.JSONDecodeError:
                        continue
                
                # パターン2: var orderData = {...}
                match = re.search(r'var\s+orderData\s*=\s*({.+?});', script_text, re.DOTALL)
                if match:
                    try:
                        json_str = match.group(1)
                        data = json.loads(json_str)
                        print("[Generic Parser] orderDataからJSONを抽出しました")
                        return data
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
                return null;
                """
                result = self.driver.execute_script(f"return ({js_code})();")
                if result:
                    print("[Generic Parser] JavaScript実行でJSONを取得しました")
                    return result
            except Exception as e:
                print(f"[Generic Parser] JavaScript実行エラー: {e}")
            
            # 方法5: ページ内のJSON-LDを検索
            json_ld_elements = self.driver.find_elements(By.CSS_SELECTOR, 'script[type="application/ld+json"]')
            for element in json_ld_elements:
                try:
                    json_text = element.get_attribute("innerHTML")
                    data = json.loads(json_text)
                    print("[Generic Parser] JSON-LDからJSONを抽出しました")
                    return data
                except json.JSONDecodeError:
                    continue
            
            print("[Generic Parser] ページからJSONデータが見つかりませんでした")
            return None
            
        except Exception as e:
            print(f"[Generic Parser] JSON抽出エラー: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _extract_base_json(self, target_url: str) -> Optional[Dict[str, Any]]:
        """
        BASEの注文詳細ページからJSONデータを抽出（専用ロジック）
        
        Args:
            target_url: ターゲットURL
        
        Returns:
            Optional[Dict[str, Any]]: 抽出したJSONデータ
        """
        try:
            # 方法1: APIエンドポイントから直接取得を試みる
            order_id_match = re.search(r'/orders/order/(\d+)', target_url)
            if order_id_match:
                order_id = order_id_match.group(1)
                api_url = f"https://admin.thebase.in/shop_admin/api/orders/view/order/{order_id}"
                print(f"[Generic Parser] BASE APIエンドポイントを試みます: {api_url}")
                
                try:
                    self.driver.get(api_url)
                    time.sleep(2)
                    page_text = self.driver.find_element(By.TAG_NAME, "body").text
                    json_data = json.loads(page_text)
                    print("[Generic Parser] BASE APIからJSONを取得しました")
                    return json_data
                except Exception as e:
                    print(f"[Generic Parser] BASE API取得エラー: {e}")
                    # 元のページに戻る
                    self.driver.get(target_url)
                    time.sleep(2)
            
            # 方法2: ページ内のscriptタグから抽出
            print("[Generic Parser] ページ内のscriptタグからJSONを抽出します...")
            
            # <script id="__NEXT_DATA__">を検索
            try:
                next_data_script = self.driver.find_element(By.CSS_SELECTOR, 'script#__NEXT_DATA__')
                script_text = next_data_script.get_attribute("innerHTML")
                if script_text:
                    json_data = json.loads(script_text)
                    print("[Generic Parser] __NEXT_DATA__からJSONを抽出しました")
                    # BASEの場合は、props.pagePropsなどの階層を確認
                    if "props" in json_data and "pageProps" in json_data["props"]:
                        page_props = json_data["props"]["pageProps"]
                        if "order" in page_props or "order_header" in page_props:
                            return page_props
                    return json_data
            except:
                pass
            
            # すべてのscriptタグを検索して、order_headerを含むものを探す
            scripts = self.driver.find_elements(By.TAG_NAME, "script")
            for script in scripts:
                script_text = script.get_attribute("innerHTML") or script.get_attribute("textContent")
                if not script_text or "order_header" not in script_text:
                    continue
                
                # BASEのorder_header JSONを検索
                # より広い範囲でマッチング
                patterns = [
                    r'({[^{}]*"order_header"[^{}]*{[^{}]*})',  # シンプルなパターン
                    r'({.*?"order_header"\s*:\s*{.*?})',  # より広いパターン
                    r'order_header["\']?\s*:\s*({.+?})(?=\s*[,}])',  # order_headerの値のみ
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, script_text, re.DOTALL)
                    if match:
                        try:
                            json_str = match.group(1)
                            # 完全なJSONオブジェクトにする
                            if not json_str.strip().startswith('{'):
                                json_str = '{' + json_str
                            if not json_str.strip().endswith('}'):
                                json_str = json_str + '}'
                            
                            json_data = json.loads(json_str)
                            print("[Generic Parser] order_headerを含むJSONを抽出しました")
                            return json_data
                        except json.JSONDecodeError:
                            continue
            
            print("[Generic Parser] BASEのJSONデータが見つかりませんでした")
            return None
            
        except Exception as e:
            print(f"[Generic Parser] BASE JSON抽出エラー: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def parse_base_order_json(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        BASEの注文詳細JSONを解析して標準形式に変換
        
        Args:
            json_data: BASEの注文詳細JSONデータ（APIレスポンス形式: {"status": 200, "order_header": {...}}）
        
        Returns:
            Dict[str, Any]: 標準形式の注文データ
        """
        try:
            # BASEのAPIレスポンス構造: {"status": 200, "order_header": {...}}
            # order_headerを取得
            if "order_header" in json_data:
                order_header = json_data["order_header"]
            elif "status" in json_data and json_data.get("status") == 200:
                # statusが200でorder_headerがない場合は、json_data自体がorder_header
                order_header = json_data
            else:
                # その他の構造の場合は、json_data自体をorder_headerとして扱う
                order_header = json_data
            
            # 顧客情報（BASEのJSON構造に対応）
            customer_data = {}
            
            # パターン1: order_header.crm_customer（BASEの標準構造）
            if "crm_customer" in order_header:
                customer = order_header["crm_customer"]
                # buyer情報も取得（住所情報がある）
                buyer = order_header.get("buyer", {})
                buyer_address = buyer.get("address", {})
                
                customer_data = {
                    "id": str(customer.get("customer_id") or customer.get("id") or ""),
                    "name": customer.get("name") or "",
                    "email": customer.get("mail_address") or customer.get("email") or buyer.get("mail_address") or "",
                    "phone": customer.get("tel") or customer.get("phone") or buyer.get("tel") or "",
                    "postal_code": buyer_address.get("zip_code") or buyer_address.get("postal_code") or "",
                    "address": self._format_address(buyer_address) if buyer_address else "",
                }
            # パターン2: order_header.buyer（crm_customerがない場合）
            elif "buyer" in order_header:
                buyer = order_header["buyer"]
                buyer_address = buyer.get("address", {})
                customer_data = {
                    "id": str(buyer.get("id") or buyer.get("buyer_id") or ""),
                    "name": f"{buyer.get('last_name', '')} {buyer.get('first_name', '')}".strip() or "",
                    "email": buyer.get("mail_address") or buyer.get("email") or "",
                    "phone": buyer.get("tel") or buyer.get("phone") or "",
                    "postal_code": buyer_address.get("zip_code") or buyer_address.get("postal_code") or "",
                    "address": self._format_address(buyer_address) if buyer_address else "",
                }
            
            # 注文情報（BASEのJSON構造に対応）
            order_data = {}
            
            # order_headerから注文情報を抽出
            time_info = order_header.get("time_info", {})
            price_info = order_header.get("price_info", {})
            
            # 注文ID: unique_keyを使用
            order_id = order_header.get("unique_key") or order_header.get("order_id") or order_header.get("id") or ""
            
            # ステータス: orders配列の最初のアイテムのstatusを確認
            status = "未処理"
            if "orders" in order_header and isinstance(order_header["orders"], list) and len(order_header["orders"]) > 0:
                first_order_status = order_header["orders"][0].get("status", "")
                status_map = {
                    "unpaid": "入金待ち",
                    "pending": "未対応",
                    "dealing": "対応中",
                    "dispatched": "対応済",
                    "cancelled": "キャンセル",
                }
                status = status_map.get(first_order_status, first_order_status or "未処理")
            
            # 決済方法のマッピング
            payment_method = order_header.get("payment", "")
            payment_map = {
                "base_bt": "BASE銀行振込",
                "creditcard": "クレジットカード",
                "cvs": "コンビニ決済",
                "bnpl": "BNPL",
                "carrier": "キャリア決済",
                "paypal": "PayPal",
                "amazon_pay": "AmazonPay",
            }
            payment_method_name = payment_map.get(payment_method, payment_method)
            
            order_data = {
                "order_id": str(order_id),
                "order_number": order_header.get("unique_key") or order_id,
                "order_date": time_info.get("ordered") or order_header.get("order_date") or "",
                "status": status,
                "total_amount": float(price_info.get("total") or order_header.get("total_amount") or 0),
                "payment_method": payment_method_name,
                "shipping_fee": float(price_info.get("shipping_fee") or order_header.get("shipping_fee") or 0),
                "tax": float(price_info.get("tax") or order_header.get("tax_amount") or 0),
            }
            
            # 商品情報
            order_items = []
            # BASEのJSON構造: order_header.orders配列
            if "orders" in order_header and isinstance(order_header["orders"], list):
                for item in order_header["orders"]:
                    # 数量: amountフィールドを使用
                    quantity = float(item.get("amount") or item.get("quantity") or 1)
                    # 単価: priceフィールドを使用
                    price = float(item.get("price") or item.get("unit_price") or 0)
                    # 小計: 単価 × 数量
                    subtotal = float(item.get("subtotal") or item.get("price_total") or (price * quantity))
                    
                    order_items.append({
                        "product_id": str(item.get("item_id") or item.get("id") or ""),
                        "product_name": item.get("name") or "商品名不明",
                        "quantity": quantity,
                        "unit": item.get("unit") or "個",  # BASEのデフォルト単位
                        "price": price,
                        "subtotal": subtotal,
                        "sku": item.get("variation_id") or item.get("item_identifier") or item.get("barcode") or "",
                    })
            # フォールバック: items配列
            elif "items" in order_header and isinstance(order_header["items"], list):
                for item in order_header["items"]:
                    quantity = float(item.get("amount") or item.get("quantity") or 1)
                    price = float(item.get("price") or item.get("unit_price") or 0)
                    subtotal = float(item.get("subtotal") or item.get("price_total") or (price * quantity))
                    
                    order_items.append({
                        "product_id": str(item.get("item_id") or item.get("id") or ""),
                        "product_name": item.get("name") or "商品名不明",
                        "quantity": quantity,
                        "unit": item.get("unit") or "個",
                        "price": price,
                        "subtotal": subtotal,
                        "sku": item.get("variation_id") or item.get("item_identifier") or "",
                    })
            
            result = {
                "customer": customer_data,
                "order": order_data,
                "order_items": order_items,
                "raw_data": json_data,  # 元のJSONデータも保持
            }
            
            # デバッグ情報を出力
            print(f"[Generic Parser] 解析結果:")
            print(f"  - 顧客ID: {customer_data.get('id')}")
            print(f"  - 顧客名: {customer_data.get('name')}")
            print(f"  - メール: {customer_data.get('email')}")
            print(f"  - 注文ID: {order_data.get('order_id')}")
            print(f"  - 注文日時: {order_data.get('order_date')}")
            print(f"  - 合計金額: {order_data.get('total_amount')}")
            print(f"  - 商品数: {len(order_items)}")
            
            return result
            
        except Exception as e:
            print(f"[Generic Parser] JSON解析エラー: {e}")
            import traceback
            traceback.print_exc()
            print(f"[Generic Parser] JSONデータ構造: {list(json_data.keys()) if isinstance(json_data, dict) else 'Not a dict'}")
            return {
                "customer": {},
                "order": {},
                "order_items": [],
                "raw_data": json_data,
            }
    
    def _format_address(self, address: Dict[str, Any]) -> str:
        """
        住所情報を文字列にフォーマット
        
        Args:
            address: 住所情報の辞書
        
        Returns:
            str: フォーマットされた住所文字列
        """
        parts = []
        if address.get("prefecture"):
            parts.append(address["prefecture"])
        if address.get("address_1"):
            parts.append(address["address_1"])
        if address.get("address_2"):
            parts.append(address["address_2"])
        return " ".join(parts) if parts else ""

