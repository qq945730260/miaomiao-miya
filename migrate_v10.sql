-- V10: Reset ALL data - clean slate for testing
-- Run this in Supabase SQL Editor to completely reset the website

-- 1. Truncate all tables (cascade to handle foreign keys)
DELETE FROM orders;
DELETE FROM products;
DELETE FROM categories;
DELETE FROM settings;

-- 2. Reset sequences
SELECT setval('categories_id_seq', 1, false);
SELECT setval('products_id_seq', 1, false);
SELECT setval('orders_id_seq', 1, false);

-- 3. Insert default admin credentials
INSERT INTO settings (key, value) VALUES
  ('admin_username', 'xuxu'),
  ('admin_password', '5361172'),
  ('site_title', '喵喵咪丫'),
  ('shop_description', ''),
  ('wechat_pay_qr', ''),
  ('alipay_qr', ''),
  ('wechat_qr', ''),
  ('shop_logo', '');

-- 4. Insert default categories
INSERT INTO categories (name, sort_order) VALUES
  ('全部', 0),
  ('宠物用品', 1),
  ('金渐层猫', 2),
  ('银渐层猫', 3);

-- Verify
SELECT 'Categories:' as info;
SELECT * FROM categories ORDER BY sort_order;
SELECT 'Settings:' as info;
SELECT key, LEFT(value, 30) as val FROM settings;
SELECT 'Products count:' as info;
SELECT COUNT(*) as count FROM products;
