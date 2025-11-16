"""
Seleniumブラウザー起動・共通操作モジュール
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from typing import Optional


def create_driver(headless: bool = False, user_data_dir: Optional[str] = None) -> webdriver.Chrome:
    """
    ChromeDriverを起動してWebDriverインスタンスを返す
    
    Args:
        headless: ヘッドレスモードで起動するか（デフォルト: False）
        user_data_dir: ユーザーデータディレクトリのパス（セッション保持用）
    
    Returns:
        webdriver.Chrome: ChromeDriverインスタンス
    """
    chrome_options = Options()
    
    # ヘッドレスモード設定
    if headless:
        chrome_options.add_argument("--headless=new")
    
    # 基本オプション
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # ユーザーデータディレクトリを設定（セッション保持用）
    if user_data_dir:
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
    
    # ウィンドウサイズ設定
    chrome_options.add_argument("--window-size=1920,1080")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.maximize_window()
        return driver
    except Exception as e:
        raise Exception(f"ChromeDriverの起動に失敗しました: {e}")


def wait_for_page_load(driver: webdriver.Chrome, timeout: int = 10):
    """
    ページの読み込み完了を待機
    
    Args:
        driver: WebDriverインスタンス
        timeout: タイムアウト時間（秒）
    """
    import time
    time.sleep(2)  # 基本的な読み込み待機
    # 必要に応じて、より高度な待機処理を追加可能

