# RPA API クイックスタートガイド

## 🚀 簡単な起動手順

### 1. 仮想環境の作成と依存関係のインストール

```bash
cd backend

# 仮想環境を作成
python3 -m venv venv

# 仮想環境をアクティベート
source venv/bin/activate  # macOS/Linux
# または
# venv\Scripts\activate  # Windows

# 依存関係をインストール
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env`ファイルを`backend`ディレクトリに作成し、以下の内容を設定してください：

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
```

**注意**: SupabaseのURLとキーは実際の値に置き換えてください。

### 3. ChromeDriverのインストール（必要な場合）

```bash
# macOS (Homebrew)
brew install chromedriver

# または、手動でダウンロード
# https://chromedriver.chromium.org/downloads
```

### 4. FastAPIサーバーの起動

```bash
# 仮想環境がアクティベートされていることを確認
source venv/bin/activate  # macOS/Linux

# サーバーを起動
uvicorn main:app --reload --port 8000
```

または、起動スクリプトを使用：

```bash
bash start_server.sh
```

### 5. サーバーの確認

ブラウザで以下のURLにアクセス：

- **APIサーバー**: http://localhost:8000
- **APIドキュメント**: http://localhost:8000/docs
- **ヘルスチェック**: http://localhost:8000/health

### 6. RPAの実行

#### 方法1: APIエンドポイントを直接呼び出す

```bash
# シンプルなRPA実行（パラメータ不要）
curl -X POST http://localhost:8000/run-rpa-simple
```

#### 方法2: ダッシュボードから実行

Next.jsダッシュボード（http://localhost:5500）の「RPA実行」ボタンをクリック

#### 方法3: APIドキュメントから実行

http://localhost:8000/docs にアクセスして、`/run-rpa-simple`エンドポイントを実行

## 📝 実行時の動作

1. RPA実行APIを呼び出すと、`base_rpa.py`が実行されます
2. Chromeブラウザが自動的に開きます
3. BASEのログインページが表示されます
4. **手動でログイン**してください（120秒の待機時間があります）
5. ログイン後、自動的に注文データを取得します
6. 取得したデータはSupabaseに保存されます

## 🔧 トラブルシューティング

### ChromeDriverが見つからない

```bash
# ChromeDriverのパスを確認
which chromedriver

# パスが通っていない場合は、PATHに追加
export PATH=$PATH:/path/to/chromedriver
```

### 仮想環境がアクティベートされない

```bash
# 仮想環境を再作成
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### ポート8000が既に使用されている

```bash
# 別のポートで起動
uvicorn main:app --reload --port 8001
```

## 📌 注意事項

- RPAスクリプトは手動ログイン方式のため、ブラウザが開いたら自分でログインする必要があります
- ログイン後、120秒の待機時間があります
- Supabaseの設定が正しくない場合、データの保存に失敗します
- ChromeDriverのバージョンは、使用しているChromeのバージョンと一致させる必要があります

