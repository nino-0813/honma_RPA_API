# 汎用RPAスクリプト

## 概要

どんなECサイトでもログイン後に任意のページからデータをスクレイピングしてSupabaseに保存する汎用RPAスクリプトです。

## 構成

```
rpa/generic/
├── config.py           # 設定管理（URL、Supabaseキー）
├── scraper.py          # Seleniumでデータ取得
├── parser.py           # HTML/JSON解析
├── supabase_client.py  # Supabase保存
└── main.py             # RPA実行エントリーポイント
```

## 使用方法

### 1. コマンドラインから実行

```bash
cd /Volumes/BackupSSD/本間農業案件/本間RPA_API/backend
source venv/bin/activate

# 通常モード（ブラウザを表示）
python -m rpa.generic.main \
  "https://admin.thebase.in/shop_admin" \
  "https://admin.thebase.in/shop_admin/orders/order/12345"

# ヘッドレスモード（ブラウザを非表示）
python -m rpa.generic.main \
  "https://admin.thebase.in/shop_admin" \
  "https://admin.thebase.in/shop_admin/orders/order/12345" \
  --headless
```

### 2. FastAPIエンドポイントから実行

```bash
curl -X POST "http://localhost:8000/run-generic-rpa" \
  -H "Content-Type: application/json" \
  -d '{
    "login_url": "https://admin.thebase.in/shop_admin",
    "target_url": "https://admin.thebase.in/shop_admin/orders/order/12345",
    "headless": false
  }'
```

### 3. Pythonコードから実行

```python
from rpa.generic.main import run_generic_rpa

success = run_generic_rpa(
    login_url="https://admin.thebase.in/shop_admin",
    target_url="https://admin.thebase.in/shop_admin/orders/order/12345",
    headless=False
)
```

## パラメータ説明

### LOGIN_URL（ログイン後URL）

- **説明**: ログイン済みの状態でアクセスできるURL
- **例**: `https://admin.thebase.in/shop_admin`
- **注意**: このURLにアクセスした時点で、すでにログイン済みの状態である必要があります

### TARGET_URL（ターゲットURL）

- **説明**: データを取得したいページのURL
- **例**: `https://admin.thebase.in/shop_admin/orders/order/12345`
- **注意**: このページにJSONデータが含まれている必要があります

## Supabaseテーブル構造

以下の3つのテーブルが必要です：

### customers テーブル

```sql
CREATE TABLE customers (
  id TEXT PRIMARY KEY,
  name TEXT,
  email TEXT,
  phone TEXT,
  postal_code TEXT,
  address TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### orders テーブル

```sql
CREATE TABLE orders (
  id TEXT PRIMARY KEY,
  order_number TEXT,
  customer_id TEXT REFERENCES customers(id),
  order_date TIMESTAMP,
  status TEXT,
  total_amount DECIMAL,
  payment_method TEXT,
  shipping_fee DECIMAL DEFAULT 0,
  tax DECIMAL DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### order_items テーブル

```sql
CREATE TABLE order_items (
  id TEXT PRIMARY KEY,
  order_id TEXT REFERENCES orders(id),
  product_id TEXT,
  product_name TEXT,
  quantity INTEGER,
  price DECIMAL,
  subtotal DECIMAL,
  sku TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

## BASEの注文詳細JSON構造

BASEの注文詳細ページから取得するJSONは以下の構造を想定しています：

```json
{
  "crm_customer": {
    "id": "customer_id",
    "name": "顧客名",
    "email": "email@example.com",
    "phone": "090-1234-5678",
    "postal_code": "123-4567",
    "address": "住所"
  },
  "order_header": {
    "order_id": "order_id",
    "order_number": "ORDER-12345",
    "order_date": "2024-01-01T00:00:00Z",
    "status": "completed",
    "total_amount": 10000,
    "payment_method": "credit_card",
    "shipping_fee": 500,
    "tax": 1000
  },
  "orders": [
    {
      "product_id": "product_id",
      "product_name": "商品名",
      "quantity": 2,
      "price": 4500,
      "subtotal": 9000,
      "sku": "SKU-123"
    }
  ],
  "buyer": {
    "id": "buyer_id",
    "name": "購入者名",
    "email": "buyer@example.com"
  }
}
```

## カスタマイズ

### JSON抽出方法のカスタマイズ

`parser.py`の`extract_json_from_page()`メソッドを編集して、対象サイトのJSON構造に合わせてください。

### データ解析のカスタマイズ

`parser.py`の`parse_base_order_json()`メソッドを編集して、対象サイトのJSON構造に合わせてください。

## トラブルシューティング

### JSONデータが取得できない場合

1. `debug_page_source.html`ファイルを確認してください（自動生成されます）
2. ページのソースコードを確認して、JSONデータの場所を特定してください
3. `parser.py`の`extract_json_from_page()`メソッドを編集してください

### Supabaseへの保存が失敗する場合

1. `.env`ファイルに`SUPABASE_URL`と`SUPABASE_KEY`が設定されているか確認してください
2. Supabaseのテーブル構造が正しいか確認してください
3. SupabaseのRLS（Row Level Security）設定を確認してください

## Supabaseテーブルの作成

Supabaseにテーブルを作成するには、`create_tables.sql`ファイルを使用してください：

1. Supabaseのダッシュボードにログイン
2. SQL Editorを開く
3. `rpa/generic/create_tables.sql`の内容をコピー＆ペースト
4. 実行ボタンをクリック

これで、`customers`、`orders`、`order_items`の3つのテーブルが作成されます。

## 注意事項

- ログイン後のURLは、すでにログイン済みの状態でアクセスできる必要があります
- クッキーは自動的に保持されますが、セッションの有効期限に注意してください
- JSONデータは`debug_json/`ディレクトリに自動保存されます（デバッグ用）
- ページソースは`debug_page_source.html`に自動保存されます（JSONが見つからない場合）
- ヘッドレスモードでは、一部のサイトで動作しない場合があります

