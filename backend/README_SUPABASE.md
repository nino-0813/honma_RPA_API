# Supabaseデータベースセットアップガイド

## 概要

このガイドでは、農家向けデータ可視化ダッシュボード用のSupabaseデータベースをセットアップする方法を説明します。

## セットアップ手順

### 1. Supabaseプロジェクトの作成

1. [Supabase](https://supabase.com/)にアクセスしてアカウントを作成
2. 新しいプロジェクトを作成
3. プロジェクトの設定から以下を取得：
   - Project URL（`SUPABASE_URL`）
   - API Key（`SUPABASE_KEY`）

### 2. 環境変数の設定

`.env`ファイルに以下を設定：

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
```

### 3. テーブルの作成

SupabaseダッシュボードのSQL Editorで以下を実行：

1. `supabase_setup.sql`の内容をコピー＆ペースト
2. 「Run」ボタンをクリックして実行

これで、テーブル、インデックス、トリガー、RLSポリシー、ビューがすべて作成されます。

これで以下のテーブルが作成されます：
- `customers` - 顧客情報
- `orders` - 注文情報
- `order_items` - 注文商品情報

### 4. セットアップの確認

セットアップが正しく完了したか確認するには、`supabase_check.sql`を実行してください。

## テーブル構造

### customers テーブル

| カラム名 | 型 | 説明 |
|---------|-----|------|
| id | TEXT | 主キー（顧客ID） |
| name | TEXT | 顧客名 |
| email | TEXT | メールアドレス |
| phone | TEXT | 電話番号 |
| postal_code | TEXT | 郵便番号 |
| address | TEXT | 住所 |
| platform | TEXT | プラットフォーム名 |
| user_id | TEXT | ユーザーID（RLS用） |
| created_at | TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | 更新日時 |

### orders テーブル

| カラム名 | 型 | 説明 |
|---------|-----|------|
| id | TEXT | 主キー（注文ID） |
| order_number | TEXT | 注文番号 |
| platform | TEXT | プラットフォーム名（必須） |
| customer_id | TEXT | 顧客ID（外部キー） |
| order_date | TIMESTAMP | 注文日時 |
| status | TEXT | ステータス（未処理、処理中、処理済） |
| total_amount | DECIMAL(10,2) | 合計金額 |
| payment_method | TEXT | 支払い方法 |
| shipping_fee | DECIMAL(10,2) | 送料 |
| tax | DECIMAL(10,2) | 税金 |
| user_id | TEXT | ユーザーID（RLS用） |
| job_id | TEXT | RPA実行ジョブID |
| created_at | TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | 更新日時 |

### order_items テーブル

| カラム名 | 型 | 説明 |
|---------|-----|------|
| id | TEXT | 主キー |
| order_id | TEXT | 注文ID（外部キー） |
| product_id | TEXT | 商品ID |
| product_name | TEXT | 商品名 |
| quantity | DECIMAL(10,2) | 数量 |
| unit | TEXT | 単位（kg, 個, 箱など） |
| price | DECIMAL(10,2) | 単価 |
| subtotal | DECIMAL(10,2) | 小計 |
| sku | TEXT | SKU |
| created_at | TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | 更新日時 |

## ビュー

### order_summary

プラットフォームごとの注文サマリー（総注文数、総売上、総出荷量など）

### weekly_order_trend

週間注文推移（曜日別の注文数）

### product_order_ratio

商品別注文割合

### order_list_view

注文一覧（ダッシュボードのテーブル表示用）

## RLS（Row Level Security）

RLSは、ユーザーごとにデータを分離するために使用されます。

- ユーザーは自分の`user_id`のデータのみ閲覧・更新・削除可能
- `user_id IS NULL`のデータは全ユーザーが閲覧可能（開発用）

### 本番環境での注意事項

本番環境では、`user_id IS NULL`の条件を削除することを推奨します。

## データの保存

RPAで取得したデータは、以下の流れでSupabaseに保存されます：

1. **顧客情報** → `customers`テーブル
2. **注文情報** → `orders`テーブル
3. **注文商品** → `order_items`テーブル

各データには`platform`と`user_id`が設定され、プラットフォームごと、ユーザーごとにデータを管理できます。

## トラブルシューティング

### RLSエラーが発生する場合

1. Supabaseの認証設定を確認
2. `user_id`が正しく設定されているか確認
3. RLSポリシーが正しく設定されているか確認

### データが保存されない場合

1. `.env`ファイルの`SUPABASE_URL`と`SUPABASE_KEY`を確認
2. Supabaseのテーブル構造が正しいか確認
3. RLSポリシーがデータの挿入を許可しているか確認

## 参考資料

- [Supabase公式ドキュメント](https://supabase.com/docs)
- [Row Level Security](https://supabase.com/docs/guides/auth/row-level-security)

