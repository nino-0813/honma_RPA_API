"""
共通ログイン処理の抽象クラス
"""
from abc import ABC, abstractmethod
from selenium import webdriver
from typing import Dict, Any


class LoginBase(ABC):
    """
    プラットフォームごとのログイン処理を定義する抽象基底クラス
    """
    
    @abstractmethod
    def get_login_url(self) -> str:
        """
        ログインページのURLを返す
        
        Returns:
            str: ログインページのURL
        """
        pass
    
    @abstractmethod
    def login(self, driver: webdriver.Chrome, credentials: Dict[str, Any]) -> bool:
        """
        ログイン処理を実行
        
        Args:
            driver: WebDriverインスタンス
            credentials: ログイン情報（email, passwordなど）
        
        Returns:
            bool: ログイン成功時True
        """
        pass
    
    def wait_for_manual_login(self, driver: webdriver.Chrome, wait_time: int = 120) -> bool:
        """
        手動ログインを待機（デフォルト実装）
        
        Args:
            driver: WebDriverインスタンス
            wait_time: 待機時間（秒）
        
        Returns:
            bool: ログイン成功時True
        """
        import time
        
        print("\n" + "="*60)
        print("【重要】ログインページを開きました。")
        print("以下の手順でログインしてください：")
        print("1. ブラウザでログインしてください")
        print("2. ログインが完了するまで、このままお待ちください")
        print(f"3. {wait_time}秒後に自動的に続行します")
        print("="*60 + "\n")
        
        check_interval = 5
        for waited_time in range(0, wait_time, check_interval):
            remaining = wait_time - waited_time
            if remaining > 0:
                print(f"[RPA] 待機中... あと{remaining}秒")
            time.sleep(check_interval)
        
        print(f"[RPA] {wait_time}秒経過しました。自動的に続行します...")
        return True

