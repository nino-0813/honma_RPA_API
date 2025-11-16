"""
設定読み込みモジュール
"""
import os
from dotenv import load_dotenv
from typing import Optional, Dict, Any


# 環境変数を読み込み
load_dotenv()


def get_supabase_config() -> Dict[str, Optional[str]]:
    """
    Supabaseの設定を取得
    
    Returns:
        Dict[str, Optional[str]]: SupabaseのURLとキー
    """
    return {
        "url": os.getenv("SUPABASE_URL"),
        "key": os.getenv("SUPABASE_KEY")
    }


def get_credentials(user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    ユーザーの認証情報を取得（将来的にSupabaseから取得可能）
    
    Args:
        user_id: ユーザーID（現在は未使用、将来の拡張用）
    
    Returns:
        Dict[str, Any]: 認証情報（email, passwordなど）
    """
    # 現在は環境変数から取得（将来的にSupabaseから取得）
    # TODO: Supabaseからユーザーごとの認証情報を取得する実装を追加
    return {
        "email": os.getenv("BASE_EMAIL"),
        "password": os.getenv("BASE_PASSWORD")
    }


def validate_config() -> bool:
    """
    設定が正しく読み込まれているか検証
    
    Returns:
        bool: 設定が有効な場合True
    """
    supabase_config = get_supabase_config()
    if not supabase_config["url"] or not supabase_config["key"]:
        print("[Config] 警告: Supabaseの設定が見つかりません。")
        print("[Config] .envファイルにSUPABASE_URLとSUPABASE_KEYを設定してください。")
        return False
    return True

