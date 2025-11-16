# RPA実行システム

各プラットフォーム（BASE、Shopify、楽天市場、ふるさと納税、食べチョク）のRPAを実行して注文データを取得し、Supabaseに保存するシステムです。

## 🎯 特徴

- **手動ログイン方式**: 認証情報をサーバーに保存せず、ユーザーが自分でログイン
- **安全**: パスワードなどの機密情報を一切保存しない
- **5つのプラットフォーム対応**: BASE、Shopify、楽天市場、ふるさと納税、食べチョク
- **汎用RPA機能**: URLを指定するだけで任意のECサイトからデータを取得可能
- **プラットフォーム固有RPA**: 各プラットフォーム専用の最適化されたRPAスクリプト
- **モジュール化されたアーキテクチャ**: 保守性と拡張性を重視した設計

## 📁 プロジェクト構成

```
本間RPA_API/
├── backend/
│   ├── main.py                    # FastAPIサーバー（エントリーポイント）
│   ├── requirements.txt            # Python依存関係
│   ├── start_server.sh            # サーバー起動スクリプト
│   ├── supabase_setup.sql         # SupabaseセットアップSQL（メイン）
│   ├── supabase_check.sql         # Supabaseセットアップ確認SQL
│   ├── README_SUPABASE.md         # Supabaseセットアップガイド
│   ├── QUICKSTART.md              # クイックスタートガイド
│   └── rpa/
│       ├── core/                  # RPAコアモジュール
│       │   ├── browser.py         # ブラウザ管理
│       │   ├── login.py           # ログイン処理（抽象基底クラス）
│       │   └── scraper_base.py    # スクレイピング処理（抽象基底クラス）
│       ├── platforms/             # プラットフォーム固有RPA
│       │   ├── base_rpa.py        # BASE用RPA
│       │   ├── shopify_rpa.py     # Shopify用RPA
│       │   ├── rakuten_rpa.py     # 楽天市場用RPA
│       │   ├── furusato_rpa.py    # ふるさと納税用RPA
│       │   └── tabechoku_rpa.py   # 食べチョク用RPA
│       ├── generic/               # 汎用RPAモジュール
│       │   ├── main.py            # 汎用RPA実行エントリーポイント
│       │   ├── config.py          # 設定管理
│       │   ├── scraper.py         # Seleniumでデータ取得
│       │   ├── parser.py          # HTML/JSON解析
│       │   └── supabase_client.py # Supabase保存
│       └── utils/                 # ユーティリティ
│           ├── config_loader.py   # 設定読み込み
│           └── data_saver.py      # データ保存（レガシー）
```

## 🚀 セットアップ

### 1. バックエンドのセットアップ

```bash
cd backend

# 仮想環境を作成（推奨）
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係をインストール
pip install --upgrade pip
pip install -r requirements.txt

# 環境変数を設定
cp .env.example .env
# .envファイルを編集してSupabaseのURLとキーを設定
```

### 2. ChromeDriverのインストール

Seleniumを使用するため、ChromeDriverが必要です。

```bash
# macOS (Homebrew)
brew install chromedriver

# または、ChromeDriverを手動でダウンロード
# https://chromedriver.chromium.org/downloads
```

### 3. Supabaseデータベースのセットアップ

詳細は `backend/README_SUPABASE.md` を参照してください。

**簡単な手順：**

1. [Supabase](https://supabase.com/)でプロジェクトを作成
2. `.env`ファイルに`SUPABASE_URL`と`SUPABASE_KEY`を設定
3. SupabaseダッシュボードのSQL Editorで`backend/supabase_setup.sql`を実行
4. セットアップ確認: `backend/supabase_check.sql`を実行（オプション）

## 🏃 実行方法

### 1. バックエンドサーバーを起動

```bash
cd backend
source venv/bin/activate  # 仮想環境をアクティベート

# 方法1: 直接起動
uvicorn main:app --reload --port 8000 --host 0.0.0.0

# 方法2: 起動スクリプトを使用
./start_server.sh
```

サーバーは `http://localhost:8000` で起動します。

### 2. APIエンドポイント

#### プラットフォーム固有RPAの実行

```bash
POST http://localhost:8000/run-rpa
Content-Type: application/json

{
  "platform": "base",  # base, shopify, rakuten, furusato, tabechoku
  "user_id": "optional-user-id"
}
```

#### 汎用RPAの実行

```bash
POST http://localhost:8000/run-generic-rpa
Content-Type: application/json

{
  "login_url": "https://admin.thebase.in/shop_admin",
  "target_url": "https://admin.thebase.in/shop_admin/orders/order/12345",
  "headless": false,
  "platform": "base",  # オプション
  "user_id": "optional-user-id"  # オプション
}
```

### 3. フロントエンド（ダッシュボード）

フロントエンドは別プロジェクト（`farm-rpa-dashboard`）として管理されています。

```bash
cd ../farm-rpa-dashboard
npm install
npm run dev
```

ダッシュボードは `http://localhost:5500` で起動します。

## 📝 使い方

### プラットフォーム固有RPA

1. ダッシュボードでプラットフォームを選択
2. 「個別実行」ボタンをクリック
3. 自動でブラウザが開き、ログインページが表示される
4. 自分のアカウントでログイン（120秒の待機時間）
5. RPAが自動で注文データを取得し、Supabaseに保存

### 汎用RPA

1. ダッシュボードでプラットフォームを選択
2. 「ログイン後URL」と「取得したいURL」を入力
3. 「個別実行」ボタンをクリック
4. 自動でブラウザが開き、ログイン後URLに移動
5. ターゲットURLからJSONデータを抽出してSupabaseに保存

### 複数プラットフォームの並列実行

1. ダッシュボードで複数のプラットフォームにチェックを入れる
2. 「選択したプラットフォームを実行」ボタンをクリック
3. 選択されたプラットフォームが並列で実行される

## 🔧 設定

### 環境変数（`.env`ファイル）

```env
# Supabase設定（必須）
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
```

### Supabaseテーブル構造

`backend/supabase_setup.sql`を実行すると、以下のテーブルが作成されます：

- **customers** - 顧客情報テーブル
- **orders** - 注文情報テーブル
- **order_items** - 注文商品情報テーブル

また、以下のビューも作成されます：

- **order_summary** - 注文サマリー（総注文数、総売上、総出荷量）
- **weekly_order_trend** - 週間注文推移
- **product_order_ratio** - 商品別注文割合
- **order_list_view** - 注文一覧（ダッシュボード表示用）

詳細は `backend/README_SUPABASE.md` を参照してください。

## 🏗️ アーキテクチャ

### RPAコアモジュール

- **browser.py**: Seleniumブラウザの作成と管理
- **login.py**: ログイン処理の抽象基底クラス（手動ログイン対応）
- **scraper_base.py**: スクレイピング処理の抽象基底クラス

### プラットフォーム固有RPA

各プラットフォーム専用のRPAスクリプト：
- `base_rpa.py` - BASE
- `shopify_rpa.py` - Shopify
- `rakuten_rpa.py` - 楽天市場
- `furusato_rpa.py` - ふるさと納税
- `tabechoku_rpa.py` - 食べチョク

### 汎用RPA

URLを指定するだけで任意のECサイトからデータを取得：
- ログイン後URLとターゲットURLを指定
- ページからJSONデータを自動抽出
- BASEの注文詳細JSON形式に対応（拡張可能）

## 🔒 セキュリティ

- **認証情報の非保存**: ID/パスワードは一切サーバーに保存されません
- **手動ログイン**: ユーザーが自分でログインするため、安全です
- **RLS（Row Level Security）**: Supabaseでユーザーごとにデータを分離
- **HTTPS通信**: 本番環境ではHTTPS通信を推奨

## 📌 注意事項

- RPAスクリプトのセレクタは、実際のサイトのHTML構造に合わせて調整が必要です
- 各プラットフォームのURLは実際のURLに置き換えてください
- ChromeDriverのバージョンは、使用しているChromeのバージョンと一致させる必要があります
- 汎用RPAは、ページにJSONデータが含まれている必要があります
- ログイン後のセッション有効期限に注意してください

## 🐛 トラブルシューティング

### ChromeDriverが見つからない

```bash
# ChromeDriverのパスを確認
which chromedriver

# パスが通っていない場合は、PATHに追加
export PATH=$PATH:/path/to/chromedriver
```

### RPAスクリプトが実行されない

- バックエンドサーバーが起動しているか確認（`http://localhost:8000/health`）
- ログを確認してエラーメッセージをチェック
- ChromeDriverが正しくインストールされているか確認

### Supabaseへの保存が失敗する

- `.env`ファイルの`SUPABASE_URL`と`SUPABASE_KEY`が正しいか確認
- `backend/supabase_setup.sql`が実行されているか確認
- SupabaseのRLSポリシーを確認

### 汎用RPAでJSONデータが取得できない

- ターゲットURLにJSONデータが含まれているか確認
- ブラウザの開発者ツールでページソースを確認
- `debug_json/`ディレクトリに保存されたJSONファイルを確認

## 📚 関連ドキュメント

- `backend/README_SUPABASE.md` - Supabaseセットアップガイド
- `backend/QUICKSTART.md` - クイックスタートガイド
- `backend/RPA_ARCHITECTURE.md` - RPAアーキテクチャの詳細
- `backend/TABLE_USAGE_ANALYSIS.md` - テーブル使用状況の分析

## 📄 ライセンス

このプロジェクトは内部使用を目的としています。
