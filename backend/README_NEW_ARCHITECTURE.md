# 🏗 新しいRPAアーキテクチャ - クイックガイド

## ✨ 新しい構造の特徴

### 🎯 **プロレベルの設計**
- **関心の分離**: 共通処理とプラットフォーム固有処理を明確に分離
- **拡張性**: 新しいプラットフォームを簡単に追加可能
- **保守性**: バグ修正が一箇所で済む
- **スケーラビリティ**: 複数ユーザー・複数プラットフォームに対応

## 📁 ディレクトリ構成

```
backend/
├── main.py                      # FastAPIエントリーポイント
└── rpa/                         # RPAモジュール（新構造）
    ├── core/                    # 共通機能
    │   ├── browser.py          # Selenium起動・共通操作
    │   ├── login.py            # 共通ログイン抽象クラス
    │   └── scraper_base.py     # スクレイパー基底クラス
    ├── platforms/              # プラットフォーム別RPA
    │   └── base_rpa.py         # BASE専用RPA
    └── utils/                  # ユーティリティ
        ├── config_loader.py    # 設定読み込み
        └── data_saver.py       # Supabase保存機能
```

## 🚀 使い方

### 1. FastAPIサーバーを起動

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

### 2. RPAを実行

#### 方法1: ダッシュボードから実行
- http://localhost:5500/dashboard にアクセス
- 「RPA実行」ボタンをクリック

#### 方法2: APIエンドポイントを直接呼び出す
```bash
curl -X POST http://localhost:8000/run-rpa-simple
```

### 3. 実行フロー

```
1. FastAPIエンドポイント (/run-rpa-simple)
   ↓
2. run_base_rpa() を呼び出し
   ↓
3. create_driver() でブラウザ起動
   ↓
4. BaseLogin().login() でログインページを開く
   ↓
5. 手動でログイン（120秒待機）
   ↓
6. BaseScraper().navigate_to_orders_page() で注文ページへ
   ↓
7. BaseScraper().scrape_orders() でデータ取得
   ↓
8. save_orders_to_supabase() でSupabaseに保存
```

## 🔧 新しいプラットフォームを追加する方法

### ステップ1: `platforms/`に新しいファイルを作成

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

### ステップ2: `main.py`の`platform_rpa_map`に追加

```python
platform_rpa_map = {
    "base": "rpa.platforms.base_rpa",
    "shopify": "rpa.platforms.shopify_rpa",  # 追加
}
```

## 📌 重要な修正点

### BASEのログインURL
- **修正前**: `https://admin.thebase.in/login` ❌
- **修正後**: `https://admin.thebase.com/login` ✅

### BASEの注文ページURL
- **修正前**: `https://admin.thebase.com/orders/` ❌
- **修正後**: `https://admin.thebase.com/shop_admin/orders/` ✅

## 🎯 メリット

### ✅ 1. プラットフォームごとにファイルを分離
→ BASEの処理を触っても、Shopifyには影響しない

### ✅ 2. 共通処理を再利用
→ ログイン、ブラウザ起動、データ保存が共通化

### ✅ 3. 農家ごとのログイン情報を動的に読み込み可能
→ `config_loader.py`でSupabaseから取得（今後実装）

### ✅ 4. 本番環境への移行が簡単
→ 構造が明確で、スケールしやすい

## 🔍 トラブルシューティング

### インポートエラーが出る場合

```bash
cd backend
source venv/bin/activate
python3 -c "from rpa.platforms.base_rpa import run_base_rpa; print('OK')"
```

### BASEのログインページに到達しない場合

1. `rpa/platforms/base_rpa.py`の`get_login_url()`を確認
2. URLが正しいか確認（`https://admin.thebase.com/login`）
3. ブラウザが正しく起動しているか確認

### 注文データが取得できない場合

1. `rpa/platforms/base_rpa.py`の`scrape_orders()`のセレクタを確認
2. BASEのHTML構造が変更されていないか確認
3. ログインが完了しているか確認

## 📚 詳細ドキュメント

- **アーキテクチャ設計書**: `RPA_ARCHITECTURE.md`
- **クイックスタート**: `QUICKSTART.md`

