-- V9: Complete database cleanup - run in Supabase SQL Editor
-- This will fix ALL category and image issues

-- Step 1: Delete ALL categories and recreate clean
DELETE FROM categories;
INSERT INTO categories (name, sort_order) VALUES
  ('全部', 0),
  ('宠物用品', 1),
  ('金渐层猫', 2),
  ('银渐层猫', 3);
SELECT setval('categories_id_seq', 4);

-- Step 2: Fix all product images - clear invalid filenames
-- Images that don't exist in storage will show broken
UPDATE products SET image = NULL WHERE image IS NOT NULL AND image != '';
UPDATE products SET detail_image = NULL WHERE detail_image IS NOT NULL AND detail_image != '';

-- Step 3: Clear broken settings (will reload from defaults)
DELETE FROM settings WHERE key IN ('shop_logo', 'wechat_qr', 'wechat_pay_qr', 'alipay_qr');

-- Verify
SELECT 'Categories:' as info;
SELECT id, name, sort_order FROM categories ORDER BY sort_order;
SELECT 'Products with images:' as info;
SELECT id, name, image FROM products;
SELECT 'Settings:' as info;
SELECT key, LEFT(value, 50) as value_preview FROM settings;
