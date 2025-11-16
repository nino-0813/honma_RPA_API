-- ============================================
-- Supabaseセットアップ確認用SQL
-- セットアップが正しく完了しているか確認します
-- ============================================

-- 1. テーブル構造の確認
SELECT 
    'customers' as table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'customers'
ORDER BY ordinal_position;

SELECT 
    'orders' as table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'orders'
ORDER BY ordinal_position;

SELECT 
    'order_items' as table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'order_items'
ORDER BY ordinal_position;

-- 2. 必須カラムの存在確認
SELECT 
    'customers' as table_name,
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'customers' AND column_name = 'user_id') THEN '✓' ELSE '✗' END as user_id,
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'customers' AND column_name = 'platform') THEN '✓' ELSE '✗' END as platform
UNION ALL
SELECT 
    'orders' as table_name,
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'orders' AND column_name = 'user_id') THEN '✓' ELSE '✗' END,
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'orders' AND column_name = 'platform') THEN '✓' ELSE '✗' END
UNION ALL
SELECT 
    'order_items' as table_name,
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'order_items' AND column_name = 'unit') THEN '✓' ELSE '✗' END,
    'N/A'::text;

-- 3. RLSの有効化確認
SELECT 
    tablename,
    CASE WHEN rowsecurity THEN '✓ Enabled' ELSE '✗ Disabled' END as rls_status
FROM pg_tables
WHERE schemaname = 'public'
AND tablename IN ('customers', 'orders', 'order_items')
ORDER BY tablename;

-- 4. RLSポリシーの確認
SELECT 
    tablename,
    COUNT(*) as policy_count
FROM pg_policies
WHERE schemaname = 'public'
AND tablename IN ('customers', 'orders', 'order_items')
GROUP BY tablename
ORDER BY tablename;

-- 5. ビューの確認
SELECT 
    table_name as view_name,
    CASE WHEN table_name IN ('order_summary', 'weekly_order_trend', 'product_order_ratio', 'order_list_view') THEN '✓' ELSE '✗' END as status
FROM information_schema.views
WHERE table_schema = 'public'
ORDER BY table_name;

-- 6. トリガーの確認
SELECT 
    trigger_name,
    event_object_table,
    event_manipulation
FROM information_schema.triggers
WHERE trigger_schema = 'public'
AND event_object_table IN ('customers', 'orders', 'order_items')
ORDER BY event_object_table, trigger_name;

