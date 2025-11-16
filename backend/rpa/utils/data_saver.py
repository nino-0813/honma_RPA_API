"""
データ保存モジュール（Supabase）
"""
from typing import List, Dict, Any, Optional
from supabase import create_client, Client
from rpa.utils.config_loader import get_supabase_config


def save_orders_to_supabase(
    orders: List[Dict[str, Any]],
    platform: str,
    user_id: Optional[str] = None,
    job_id: Optional[str] = None
) -> bool:
    """
    注文データをSupabaseに保存
    
    Args:
        orders: 注文データのリスト
        platform: プラットフォーム名（base, shopify, rakuten, furusatoなど）
        user_id: ユーザーID（オプション）
        job_id: ジョブID（オプション）
    
    Returns:
        bool: 保存成功時True
    """
    if not orders:
        print(f"[DataSaver] 保存する注文データがありません。")
        return False
    
    try:
        config = get_supabase_config()
        if not config["url"] or not config["key"]:
            print("[DataSaver] Supabaseの設定が見つかりません。環境変数を確認してください。")
            print(f"[DataSaver] 取得した注文データ: {orders}")
            return False
        
        supabase: Client = create_client(config["url"], config["key"])
        
        print(f"[DataSaver] {len(orders)}件の注文をSupabaseに保存しています...")
        
        for order in orders:
            order_data = {
                "user_id": user_id,
                "platform": platform,
                "order_id": order.get("order_id", ""),
                "customer_name": order.get("customer", ""),
                "total": order.get("total", ""),
                "job_id": job_id
            }
            
            # 追加のフィールドがあれば含める
            if "order_date" in order:
                order_data["order_date"] = order["order_date"]
            if "status" in order:
                order_data["status"] = order["status"]
            
            supabase.table("orders").insert(order_data).execute()
        
        print(f"[DataSaver] Supabaseへの保存が完了しました")
        return True
        
    except Exception as e:
        print(f"[DataSaver] Supabase保存エラー: {e}")
        import traceback
        traceback.print_exc()
        print(f"[DataSaver] 取得した注文データ: {orders}")
        return False

