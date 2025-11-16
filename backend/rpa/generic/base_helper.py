"""
BASE専用の補助ロジック
汎用RPAでplatform="base"の場合に使用されるヘルパー関数
"""
from typing import Dict, Any, Optional
from rpa.platforms.base_rpa import BaseLogin, BaseScraper


def get_base_login_handler() -> BaseLogin:
    """
    BASE専用のログインハンドラーを取得
    
    Returns:
        BaseLogin: BASEログインハンドラー
    """
    return BaseLogin()


def get_base_scraper_helper() -> Optional[Dict[str, Any]]:
    """
    BASE専用のスクレイパーヘルパー情報を取得
    
    Returns:
        Optional[Dict[str, Any]]: BASEスクレイパーの補助情報
    """
    return {
        "login_url": "https://admin.thebase.in/login",
        "orders_url": "https://admin.thebase.in/shop_admin/orders/",
        "api_base_url": "https://admin.thebase.in/shop_admin/api/orders/view/order/"
    }

