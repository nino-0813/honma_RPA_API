"""
スクレイパーの基底クラス
"""
from abc import ABC, abstractmethod
from selenium import webdriver
from typing import List, Dict, Any, Optional


class ScraperBase(ABC):
    """
    プラットフォームごとのスクレイピング処理を定義する抽象基底クラス
    """
    
    def __init__(self, driver: webdriver.Chrome, platform: str):
        """
        初期化
        
        Args:
            driver: WebDriverインスタンス
            platform: プラットフォーム名（base, shopify, rakuten, furusatoなど）
        """
        self.driver = driver
        self.platform = platform
    
    @abstractmethod
    def get_orders_url(self) -> str:
        """
        注文一覧ページのURLを返す
        
        Returns:
            str: 注文一覧ページのURL
        """
        pass
    
    @abstractmethod
    def scrape_orders(self, max_orders: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        注文データをスクレイピング
        
        Args:
            max_orders: 取得する最大注文数（Noneの場合はすべて）
        
        Returns:
            List[Dict[str, Any]]: 注文データのリスト
        """
        pass
    
    def navigate_to_orders_page(self) -> bool:
        """
        注文ページに遷移
        
        Returns:
            bool: 遷移成功時True
        """
        import time
        from selenium.webdriver.common.by import By
        
        orders_url = self.get_orders_url()
        print(f"[{self.platform.upper()} RPA] 注文ページに遷移しています... ({orders_url})")
        
        try:
            current_url = self.driver.current_url
            print(f"[{self.platform.upper()} RPA] 現在のURL: {current_url}")
            
            # URLで直接遷移
            self.driver.get(orders_url)
            print(f"[{self.platform.upper()} RPA] ページの読み込みを待機しています...")
            time.sleep(5)
            
            # 遷移後のURLを確認
            new_url = self.driver.current_url
            print(f"[{self.platform.upper()} RPA] 最終的なURL: {new_url}")
            
            # ログインページにリダイレクトされていないか確認
            if "login" in new_url.lower():
                print(f"[{self.platform.upper()} RPA] 警告: ログインページにリダイレクトされました。")
                print(f"[{self.platform.upper()} RPA] ログインが完了していない可能性があります。")
                return False
            
            return True
        except Exception as e:
            print(f"[{self.platform.upper()} RPA] 注文ページへの遷移でエラーが発生しました: {e}")
            return False

