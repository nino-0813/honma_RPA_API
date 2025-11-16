"""
汎用RPA Supabaseクライアント
"""
from typing import Dict, Any, List, Optional
from supabase import create_client, Client
from rpa.generic.config import GenericRPAConfig


class GenericSupabaseClient:
    """汎用Supabaseクライアント"""
    
    def __init__(self, config: GenericRPAConfig):
        """
        初期化
        
        Args:
            config: GenericRPAConfigインスタンス
        """
        self.config = config
        self.supabase: Client = create_client(config.supabase_url, config.supabase_key)
    
    def upsert_customer(self, customer_data: Dict[str, Any]) -> Optional[str]:
        """
        顧客情報をupsert（customersテーブル）
        
        Args:
            customer_data: 顧客データ
        
        Returns:
            Optional[str]: 顧客ID、失敗時はNone
        """
        try:
            # IDまたはemailが必要
            customer_id = customer_data.get("id")
            email = customer_data.get("email")
            
            if not customer_id and not email:
                print("[Supabase Client] 顧客IDまたはメールアドレスが必要です")
                return None
            
            # IDがない場合はemailをIDとして使用（emailが存在する場合）
            if not customer_id and email:
                customer_id = email
                print(f"[Supabase Client] 顧客IDがないため、emailをIDとして使用します: {email}")
            
            # upsert用のデータを準備
            upsert_data = {
                "id": customer_id,
                "name": customer_data.get("name"),
                "email": email,
                "phone": customer_data.get("phone"),
                "postal_code": customer_data.get("postal_code"),
                "address": customer_data.get("address"),
            }
            
            # None値を削除
            upsert_data = {k: v for k, v in upsert_data.items() if v is not None}
            
            print(f"[Supabase Client] 顧客情報を保存しています... (ID: {upsert_data.get('id')}, Email: {upsert_data.get('email')})")
            result = self.supabase.table("customers").upsert(upsert_data).execute()
            
            if result.data:
                customer_id = result.data[0].get("id") if isinstance(result.data, list) else result.data.get("id")
                print(f"[Supabase Client] 顧客情報の保存が完了しました (ID: {customer_id})")
                return customer_id
            else:
                print("[Supabase Client] 顧客情報の保存に失敗しました")
                return None
                
        except Exception as e:
            print(f"[Supabase Client] 顧客情報の保存エラー: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def upsert_order(self, order_data: Dict[str, Any], customer_id: Optional[str] = None, platform: Optional[str] = None, user_id: Optional[str] = None, job_id: Optional[str] = None) -> Optional[str]:
        """
        注文情報をupsert（ordersテーブル）
        
        Args:
            order_data: 注文データ
            customer_id: 顧客ID（オプション）
            platform: プラットフォーム名（base, shopify, rakuten, furusato, tabechoku）
            user_id: ユーザーID（RLS用）
            job_id: RPA実行ジョブID
        
        Returns:
            Optional[str]: 注文ID、失敗時はNone
        """
        try:
            if not order_data.get("order_id"):
                print("[Supabase Client] 注文IDが必要です")
                return None
            
            # upsert用のデータを準備
            upsert_data = {
                "id": order_data.get("order_id"),
                "order_number": order_data.get("order_number"),
                "platform": platform or order_data.get("platform"),
                "customer_id": customer_id,
                "order_date": order_data.get("order_date"),
                "status": order_data.get("status") or "未処理",
                "total_amount": order_data.get("total_amount"),
                "payment_method": order_data.get("payment_method"),
                "shipping_fee": order_data.get("shipping_fee") or 0,
                "tax": order_data.get("tax") or 0,
                "user_id": user_id or order_data.get("user_id"),
                "job_id": job_id or order_data.get("job_id"),
            }
            
            # None値を削除
            upsert_data = {k: v for k, v in upsert_data.items() if v is not None}
            
            print(f"[Supabase Client] 注文情報を保存しています... (Order ID: {upsert_data.get('id')})")
            result = self.supabase.table("orders").upsert(upsert_data).execute()
            
            if result.data:
                order_id = result.data[0].get("id") if isinstance(result.data, list) else result.data.get("id")
                print(f"[Supabase Client] 注文情報の保存が完了しました (ID: {order_id})")
                return order_id
            else:
                print("[Supabase Client] 注文情報の保存に失敗しました")
                return None
                
        except Exception as e:
            print(f"[Supabase Client] 注文情報の保存エラー: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def upsert_order_items(self, order_items: List[Dict[str, Any]], order_id: str) -> int:
        """
        注文商品情報をupsert（order_itemsテーブル）
        
        Args:
            order_items: 注文商品データのリスト
            order_id: 注文ID
        
        Returns:
            int: 保存した商品数
        """
        try:
            if not order_items:
                print("[Supabase Client] 注文商品がありません")
                return 0
            
            upsert_data_list = []
            for idx, item in enumerate(order_items):
                upsert_data = {
                    "id": f"{order_id}-{idx+1}",  # 複合キーとして使用
                    "order_id": order_id,
                    "product_id": item.get("product_id"),
                    "product_name": item.get("product_name"),
                    "quantity": item.get("quantity") or 1,
                    "unit": item.get("unit") or "kg",  # 単位（デフォルトはkg）
                    "price": item.get("price"),
                    "subtotal": item.get("subtotal"),
                    "sku": item.get("sku"),
                }
                
                # None値を削除
                upsert_data = {k: v for k, v in upsert_data.items() if v is not None}
                upsert_data_list.append(upsert_data)
            
            print(f"[Supabase Client] {len(upsert_data_list)}件の注文商品を保存しています...")
            result = self.supabase.table("order_items").upsert(upsert_data_list).execute()
            
            saved_count = len(result.data) if result.data else 0
            print(f"[Supabase Client] {saved_count}件の注文商品の保存が完了しました")
            return saved_count
            
        except Exception as e:
            print(f"[Supabase Client] 注文商品の保存エラー: {e}")
            import traceback
            traceback.print_exc()
            return 0
    
    def save_order_data(self, parsed_data: Dict[str, Any], platform: Optional[str] = None, user_id: Optional[str] = None, job_id: Optional[str] = None) -> Dict[str, int]:
        """
        解析済みの注文データをSupabaseに保存
        
        Args:
            parsed_data: parse_base_order_json()で解析されたデータ
            platform: プラットフォーム名（base, shopify, rakuten, furusato, tabechoku）
            user_id: ユーザーID（RLS用）
            job_id: RPA実行ジョブID
        
        Returns:
            Dict[str, int]: 保存レコード数 {customers: int, orders: int, items: int}
        """
        saved_records = {
            "customers": 0,
            "orders": 0,
            "items": 0
        }
        
        try:
            # 1. 顧客情報を保存
            customer_id = None
            if parsed_data.get("customer") and parsed_data["customer"]:
                customer_data = parsed_data["customer"].copy()
                customer_data["platform"] = platform
                customer_data["user_id"] = user_id
                customer_id = self.upsert_customer(customer_data)
                if customer_id:
                    saved_records["customers"] = 1
                    print(f"[Supabase Client] ✓ 顧客情報を保存しました (ID: {customer_id})")
                else:
                    print("[Supabase Client] ⚠ 顧客情報の保存をスキップしました")
            else:
                print("[Supabase Client] ⚠ 顧客情報がありません。スキップします")
            
            # 2. 注文情報を保存
            order_id = None
            if parsed_data.get("order") and parsed_data["order"]:
                order_id = self.upsert_order(parsed_data["order"], customer_id, platform, user_id, job_id)
                if order_id:
                    saved_records["orders"] = 1
                    print(f"[Supabase Client] ✓ 注文情報を保存しました (ID: {order_id})")
                else:
                    print("[Supabase Client] ⚠ 注文情報の保存をスキップしました")
            else:
                print("[Supabase Client] ⚠ 注文情報がありません。スキップします")
            
            # 3. 注文商品を保存
            if order_id and parsed_data.get("order_items") and parsed_data["order_items"]:
                item_count = self.upsert_order_items(parsed_data["order_items"], order_id)
                if item_count > 0:
                    saved_records["items"] = item_count
                    print(f"[Supabase Client] ✓ {item_count}件の注文商品を保存しました")
                else:
                    print("[Supabase Client] ⚠ 注文商品の保存をスキップしました")
            else:
                if not order_id:
                    print("[Supabase Client] ⚠ 注文IDがないため、注文商品をスキップします")
                elif not parsed_data.get("order_items"):
                    print("[Supabase Client] ⚠ 注文商品がありません。スキップします")
            
            total_saved = sum(saved_records.values())
            if total_saved > 0:
                print(f"\n[Supabase Client] ✓ 合計 {total_saved}件のデータをSupabaseに保存しました")
                print(f"[Supabase Client] 保存内訳: 顧客={saved_records['customers']}, 注文={saved_records['orders']}, 商品={saved_records['items']}")
            else:
                print("\n[Supabase Client] ⚠ 保存されたデータがありません")
                print("[Supabase Client] デバッグ情報:")
                print(f"  - 顧客データ: {parsed_data.get('customer', {})}")
                print(f"  - 注文データ: {parsed_data.get('order', {})}")
                print(f"  - 商品数: {len(parsed_data.get('order_items', []))}")
            
            return saved_records
            
        except Exception as e:
            print(f"[Supabase Client] データ保存エラー: {e}")
            import traceback
            traceback.print_exc()
            print("[Supabase Client] デバッグ情報:")
            print(f"  - 解析データ: {parsed_data}")
            return saved_records

