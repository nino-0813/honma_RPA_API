# 🏗 RPAアーキテクチャ設計書

## 📁 ディレクトリ構成

```
backend/
├── main.py                      # FastAPIエントリーポイント
├── rpa/                         # RPAモジュール（新構造）
│   ├── core/                    # 共通機能
│   │   ├── __init__.py
│   │   ├── browser.py          # Selenium起動・共通操作
│   │   ├── login.py            # 共通ログイン抽象クラス
│   │   └── scraper_base.py     # スクレイパー基底クラス
│   ├── platforms/              # プラットフォーム別RPA
│   │   ├── __init__.py
│   │   ├── base_rpa.py         # BASE専用RPA
│   │   ├── shopify_rpa.py      # Shopify専用RPA（今後実装）
│   │   ├── rakuten_rpa.py      # 楽天専用RPA（今後実装）
│   │   └── furusato_rpa.py     # ふるさと納税専用RPA（今後実装）
│   └── utils/                  # ユーティリティ
│       ├── __init__.py
│       ├── config_loader.py    # 設定読み込み
│       └── data_saver.py       # Supabase保存機能
└── rpa_scripts/                # 旧構造（後方互換性のため残す）
    └── ...
```

## 🎯 設計思想

### 1. **関心の分離（Separation of Concerns）**
- **core/**: すべてのプラットフォームで共通する機能
- **platforms/**: プラットフォーム固有の実装
- **utils/**: 共通ユーティリティ（設定、データ保存など）

### 2. **拡張性**
- 新しいプラットフォームを追加する際は、`platforms/`に新しいファイルを追加するだけ
- 既存のプラットフォームに影響を与えない

### 3. **保守性**
- 共通処理は`core/`に集約
- バグ修正が一箇所で済む

## 📝 各モジュールの役割

### `core/browser.py`
**役割**: Seleniumブラウザーの起動と基本設定

**主要関数**:
- `create_driver(headless, user_data_dir)`: ChromeDriverを起動

**特徴**:
- ヘッドレスモード対応
- ユーザーデータディレクトリ指定可能（セッション保持）
- 自動化検出回避オプション設定済み

### `core/login.py`
**役割**: ログイン処理の抽象化

**主要クラス**:
- `LoginBase`: 抽象基底クラス
  - `get_login_url()`: ログインページURLを返す
  - `login()`: ログイン処理を実行
  - `wait_for_manual_login()`: 手動ログイン待機（デフォルト実装）

**実装例**:
```python
class BaseLogin(LoginBase):
    def get_login_url(self) -> str:
        return "https://admin.thebase.com/login"
    
    def login(self, driver, credentials):
        # BASE専用のログイン処理
        pass
```

### `core/scraper_base.py`
**役割**: スクレイピング処理の抽象化

**主要クラス**:
- `ScraperBase`: 抽象基底クラス
  - `get_orders_url()`: 注文一覧ページURLを返す
  - `scrape_orders()`: 注文データをスクレイピング
  - `navigate_to_orders_page()`: 注文ページに遷移

**実装例**:
```python
class BaseScraper(ScraperBase):
    def get_orders_url(self) -> str:
        return "https://admin.thebase.com/shop_admin/orders/"
    
    def scrape_orders(self, max_orders):
        # BASE専用のスクレイピング処理
        pass
```

### `utils/config_loader.py`
**役割**: 設定の読み込みと検証

**主要関数**:
- `get_supabase_config()`: Supabase設定を取得
- `get_credentials(user_id)`: ユーザー認証情報を取得（将来はSupabaseから）
- `validate_config()`: 設定の検証

### `utils/data_saver.py`
**役割**: データのSupabaseへの保存

**主要関数**:
- `save_orders_to_supabase(orders, platform, user_id, job_id)`: 注文データを保存

### `platforms/base_rpa.py`
**役割**: BASE専用のRPA実装

**主要クラス**:
- `BaseLogin`: BASE専用ログイン処理
- `BaseScraper`: BASE専用スクレイパー

**主要関数**:
- `run_base_rpa(job_id, user_id, credentials)`: BASE RPAを実行

## 🔄 実行フロー

```
1. FastAPIエンドポイント (/run-rpa-simple)
   ↓
2. run_base_rpa() を呼び出し
   ↓
3. create_driver() でブラウザ起動
   ↓
4. BaseLogin().login() でログイン
   ↓
5. BaseScraper().navigate_to_orders_page() で注文ページへ
   ↓
6. BaseScraper().scrape_orders() でデータ取得
   ↓
7. save_orders_to_supabase() でSupabaseに保存
```

## 🚀 新しいプラットフォームを追加する方法

### 1. `platforms/`に新しいファイルを作成

例: `platforms/shopify_rpa.py`

```python
from rpa.core.login import LoginBase
from rpa.core.scraper_base import ScraperBase
from rpa.core.browser import create_driver
from rpa.utils.data_saver import save_orders_to_supabase

class ShopifyLogin(LoginBase):
    def get_login_url(self) -> str:
        return "https://admin.shopify.com/store/xxx/login"
    
    def login(self, driver, credentials):
        # Shopify専用のログイン処理
        pass

class ShopifyScraper(ScraperBase):
    def get_orders_url(self) -> str:
        return "https://admin.shopify.com/store/xxx/orders"
    
    def scrape_orders(self, max_orders):
        # Shopify専用のスクレイピング処理
        pass

def run_shopify_rpa(job_id, user_id, credentials):
    driver = create_driver()
    ShopifyLogin().login(driver, credentials)
    scraper = ShopifyScraper(driver)
    scraper.navigate_to_orders_page()
    orders = scraper.scrape_orders()
    save_orders_to_supabase(orders, "shopify", user_id, job_id)
```

### 2. `main.py`の`platform_rpa_map`に追加

```python
platform_rpa_map = {
    "base": "rpa.platforms.base_rpa",
    "shopify": "rpa.platforms.shopify_rpa",  # 追加
    # ...
}
```

## 🔧 現在の実装状況

- ✅ **core/browser.py**: 実装完了
- ✅ **core/login.py**: 実装完了
- ✅ **core/scraper_base.py**: 実装完了
- ✅ **utils/config_loader.py**: 実装完了
- ✅ **utils/data_saver.py**: 実装完了
- ✅ **platforms/base_rpa.py**: 実装完了
- ✅ **main.py**: 新しい構造に対応完了
- ⏳ **platforms/shopify_rpa.py**: 今後実装
- ⏳ **platforms/rakuten_rpa.py**: 今後実装
- ⏳ **platforms/furusato_rpa.py**: 今後実装

## 📌 注意事項

1. **BASEのログインURL**: `https://admin.thebase.com/login`（`.com`を使用）
2. **手動ログイン**: 現在は手動ログイン方式（120秒待機）
3. **ブラウザの保持**: RPA実行後、ブラウザは手動で閉じるまで開いたまま
4. **エラーハンドリング**: エラー時もブラウザを開いたままにして、ユーザーが確認できるように

## 🎯 今後の拡張

1. **自動ログイン**: 認証情報をSupabaseから取得して自動ログイン
2. **複数ユーザー対応**: ユーザーごとに異なる認証情報を使用
3. **スケジューリング**: 定期的なRPA実行
4. **ログ管理**: 実行ログのSupabaseへの保存
5. **エラー通知**: エラー発生時の通知機能

