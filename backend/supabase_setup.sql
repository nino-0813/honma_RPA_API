-- ============================================
-- 農家向けデータ可視化ダッシュボード用SupabaseセットアップSQL
-- このファイル1つで完全なセットアップが可能です
-- ============================================

-- ============================================
-- 1. テーブル作成
-- ============================================

-- customers テーブル（顧客情報）
CREATE TABLE IF NOT EXISTS customers (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT,
  phone TEXT,
  postal_code TEXT,
  address TEXT,
  platform TEXT, -- プラットフォーム名（base, shopify, rakuten, furusato, tabechoku）
  user_id TEXT, -- ユーザーID（RLS用）
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- orders テーブル（注文情報）
CREATE TABLE IF NOT EXISTS orders (
  id TEXT PRIMARY KEY,
  order_number TEXT,
  platform TEXT NOT NULL, -- プラットフォーム名（base, shopify, rakuten, furusato, tabechoku）
  customer_id TEXT REFERENCES customers(id) ON DELETE SET NULL,
  order_date TIMESTAMP WITH TIME ZONE NOT NULL,
  status TEXT DEFAULT '未処理', -- ステータス（未処理、処理中、処理済）
  total_amount DECIMAL(10, 2) NOT NULL DEFAULT 0,
  payment_method TEXT,
  shipping_fee DECIMAL(10, 2) DEFAULT 0,
  tax DECIMAL(10, 2) DEFAULT 0,
  user_id TEXT, -- ユーザーID（RLS用）
  job_id TEXT, -- RPA実行ジョブID
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- order_items テーブル（注文商品情報）
CREATE TABLE IF NOT EXISTS order_items (
  id TEXT PRIMARY KEY,
  order_id TEXT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  product_id TEXT,
  product_name TEXT NOT NULL,
  quantity DECIMAL(10, 2) NOT NULL DEFAULT 1,
  unit TEXT DEFAULT 'kg', -- 単位（kg, 個, 箱など）
  price DECIMAL(10, 2) NOT NULL,
  subtotal DECIMAL(10, 2) NOT NULL,
  sku TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- 2. インデックスの作成（パフォーマンス向上）
-- ============================================

CREATE INDEX IF NOT EXISTS idx_customers_user_id ON customers(user_id);
CREATE INDEX IF NOT EXISTS idx_customers_platform ON customers(platform);
CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);

CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_platform ON orders(platform);
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_order_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_job_id ON orders(job_id);

CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product_name ON order_items(product_name);

-- ============================================
-- 3. トリガー関数（updated_at自動更新）
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- トリガーの作成
DROP TRIGGER IF EXISTS update_customers_updated_at ON customers;
CREATE TRIGGER update_customers_updated_at
    BEFORE UPDATE ON customers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_orders_updated_at ON orders;
CREATE TRIGGER update_orders_updated_at
    BEFORE UPDATE ON orders
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_order_items_updated_at ON order_items;
CREATE TRIGGER update_order_items_updated_at
    BEFORE UPDATE ON order_items
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 4. Row Level Security (RLS) ポリシー
-- ============================================

-- RLSを有効化
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE order_items ENABLE ROW LEVEL SECURITY;

-- 既存のポリシーを削除（再実行時のため）
DROP POLICY IF EXISTS "Users can view their own customers" ON customers;
DROP POLICY IF EXISTS "Users can insert their own customers" ON customers;
DROP POLICY IF EXISTS "Users can update their own customers" ON customers;
DROP POLICY IF EXISTS "Users can delete their own customers" ON customers;

DROP POLICY IF EXISTS "Users can view their own orders" ON orders;
DROP POLICY IF EXISTS "Users can insert their own orders" ON orders;
DROP POLICY IF EXISTS "Users can update their own orders" ON orders;
DROP POLICY IF EXISTS "Users can delete their own orders" ON orders;

DROP POLICY IF EXISTS "Users can view their own order items" ON order_items;
DROP POLICY IF EXISTS "Users can insert their own order items" ON order_items;
DROP POLICY IF EXISTS "Users can update their own order items" ON order_items;
DROP POLICY IF EXISTS "Users can delete their own order items" ON order_items;

-- customers テーブルのRLSポリシー
CREATE POLICY "Users can view their own customers"
    ON customers FOR SELECT
    USING (auth.uid()::text = user_id OR user_id IS NULL);

CREATE POLICY "Users can insert their own customers"
    ON customers FOR INSERT
    WITH CHECK (auth.uid()::text = user_id OR user_id IS NULL);

CREATE POLICY "Users can update their own customers"
    ON customers FOR UPDATE
    USING (auth.uid()::text = user_id OR user_id IS NULL);

CREATE POLICY "Users can delete their own customers"
    ON customers FOR DELETE
    USING (auth.uid()::text = user_id OR user_id IS NULL);

-- orders テーブルのRLSポリシー
CREATE POLICY "Users can view their own orders"
    ON orders FOR SELECT
    USING (auth.uid()::text = user_id OR user_id IS NULL);

CREATE POLICY "Users can insert their own orders"
    ON orders FOR INSERT
    WITH CHECK (auth.uid()::text = user_id OR user_id IS NULL);

CREATE POLICY "Users can update their own orders"
    ON orders FOR UPDATE
    USING (auth.uid()::text = user_id OR user_id IS NULL);

CREATE POLICY "Users can delete their own orders"
    ON orders FOR DELETE
    USING (auth.uid()::text = user_id OR user_id IS NULL);

-- order_items テーブルのRLSポリシー
CREATE POLICY "Users can view their own order items"
    ON order_items FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM orders
            WHERE orders.id = order_items.order_id
            AND (orders.user_id = auth.uid()::text OR orders.user_id IS NULL)
        )
    );

CREATE POLICY "Users can insert their own order items"
    ON order_items FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM orders
            WHERE orders.id = order_items.order_id
            AND (orders.user_id = auth.uid()::text OR orders.user_id IS NULL)
        )
    );

CREATE POLICY "Users can update their own order items"
    ON order_items FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM orders
            WHERE orders.id = order_items.order_id
            AND (orders.user_id = auth.uid()::text OR orders.user_id IS NULL)
        )
    );

CREATE POLICY "Users can delete their own order items"
    ON order_items FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM orders
            WHERE orders.id = order_items.order_id
            AND (orders.user_id = auth.uid()::text OR orders.user_id IS NULL)
        )
    );

-- ============================================
-- 5. ビュー（ダッシュボード用の集計ビュー）
-- ============================================

-- 注文サマリービュー（総注文数、総売上、総出荷量を計算）
CREATE OR REPLACE VIEW order_summary AS
SELECT 
    o.user_id,
    o.platform,
    COUNT(DISTINCT o.id) as total_orders,
    COALESCE(SUM(o.total_amount), 0) as total_sales,
    COALESCE(SUM(oi.quantity), 0) as total_quantity_kg,
    COUNT(DISTINCT o.customer_id) as total_customers
FROM orders o
LEFT JOIN order_items oi ON o.id = oi.order_id
GROUP BY o.user_id, o.platform;

-- 週間注文推移ビュー（曜日別の注文数）
CREATE OR REPLACE VIEW weekly_order_trend AS
SELECT 
    o.user_id,
    o.platform,
    EXTRACT(DOW FROM o.order_date) as day_of_week, -- 0=日曜日, 1=月曜日, ...
    CASE EXTRACT(DOW FROM o.order_date)
        WHEN 0 THEN '日'
        WHEN 1 THEN '月'
        WHEN 2 THEN '火'
        WHEN 3 THEN '水'
        WHEN 4 THEN '木'
        WHEN 5 THEN '金'
        WHEN 6 THEN '土'
    END as day_name,
    COUNT(*) as order_count
FROM orders o
WHERE o.order_date >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY o.user_id, o.platform, EXTRACT(DOW FROM o.order_date)
ORDER BY day_of_week;

-- 商品別注文割合ビュー
CREATE OR REPLACE VIEW product_order_ratio AS
SELECT 
    o.user_id,
    o.platform,
    oi.product_name,
    COUNT(DISTINCT o.id) as order_count,
    SUM(oi.quantity) as total_quantity,
    SUM(oi.subtotal) as total_amount,
    ROUND(
        COUNT(DISTINCT o.id) * 100.0 / NULLIF(
            (SELECT COUNT(DISTINCT o2.id) FROM orders o2 WHERE o2.user_id = o.user_id AND o2.platform = o.platform),
            0
        ),
        2
    ) as percentage
FROM orders o
JOIN order_items oi ON o.id = oi.order_id
GROUP BY o.user_id, o.platform, oi.product_name;

-- 注文一覧ビュー（ダッシュボードのテーブル表示用）
CREATE OR REPLACE VIEW order_list_view AS
SELECT 
    o.id as order_id,
    o.order_number,
    o.order_date,
    o.platform,
    c.name as customer_name,
    oi.product_name,
    oi.quantity,
    oi.unit,
    o.total_amount,
    o.status,
    o.user_id
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.id
LEFT JOIN order_items oi ON o.id = oi.order_id
ORDER BY o.order_date DESC, o.id;

-- ============================================
-- 6. コメント（テーブル・カラムの説明）
-- ============================================

COMMENT ON TABLE customers IS '顧客情報テーブル。プラットフォームごとの顧客を管理';
COMMENT ON TABLE orders IS '注文情報テーブル。プラットフォームごとの注文を管理';
COMMENT ON TABLE order_items IS '注文商品情報テーブル。各注文の商品詳細を管理';

COMMENT ON COLUMN customers.platform IS 'プラットフォーム名（base, shopify, rakuten, furusato, tabechoku）';
COMMENT ON COLUMN customers.user_id IS 'ユーザーID。RLSでデータを分離するために使用';

COMMENT ON COLUMN orders.platform IS 'プラットフォーム名（base, shopify, rakuten, furusato, tabechoku）';
COMMENT ON COLUMN orders.status IS '注文ステータス（未処理、処理中、処理済）';
COMMENT ON COLUMN orders.user_id IS 'ユーザーID。RLSでデータを分離するために使用';
COMMENT ON COLUMN orders.job_id IS 'RPA実行ジョブID。どのRPA実行で取得されたデータかを追跡';

COMMENT ON COLUMN order_items.unit IS '数量の単位（kg, 個, 箱など）';
COMMENT ON COLUMN order_items.quantity IS '数量（DECIMAL型で小数点も対応）';

