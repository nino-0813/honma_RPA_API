"""
汎用RPA設定管理
"""
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()


class GenericRPAConfig:
    """汎用RPAの設定クラス"""
    
    def __init__(
        self,
        login_url: str,
        target_url: str,
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None,
        platform: Optional[str] = None,
        headless: bool = False,
        user_id: Optional[str] = None
    ):
        """
        初期化
        
        Args:
            login_url: ログイン後のURL（クッキーが有効な状態）
            target_url: データ取得対象のURL
            supabase_url: Supabase URL（未指定の場合は環境変数から取得）
            supabase_key: Supabase Key（未指定の場合は環境変数から取得）
            platform: プラットフォーム名（base, shopify, rakuten, furusato, tabechoku）
            headless: ヘッドレスモードで実行するか
            user_id: ユーザーID（RLS用）
        """
        self.login_url = login_url
        self.target_url = target_url
        self.platform = platform
        self.headless = headless
        self.user_id = user_id
        self.supabase_url = supabase_url or os.getenv("SUPABASE_URL")
        self.supabase_key = supabase_key or os.getenv("SUPABASE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabaseの設定が見つかりません。環境変数または引数で指定してください。")
    
    def validate(self) -> bool:
        """
        設定の検証
        
        Returns:
            bool: 設定が有効な場合True
        """
        if not self.login_url or not self.target_url:
            return False
        if not self.supabase_url or not self.supabase_key:
            return False
        return True

