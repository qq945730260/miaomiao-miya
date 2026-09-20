-- V12: Complete fix for categories, settings, and image upload
-- Run this in Supabase SQL Editor

-- 1. Clean ALL data
DELETE FROM orders;
DELETE FROM products;
DELETE FROM categories;
DELETE FROM settings;

-- 2. Reset sequences
SELECT setval('categories_id_seq', 1, false);
SELECT setval('products_id_seq', 1, false);
SELECT setval('orders_id_seq', 1, false);

-- 3. Insert defaults
INSERT INTO settings (key, value) VALUES
  ('admin_username', 'xuxu'),
  ('admin_password', '5361172'),
  ('site_title', '喵喵咪丫'),
  ('shop_description', ''),
  ('wechat_pay_qr', ''),
  ('alipay_qr', ''),
  ('wechat_qr', ''),
  ('shop_logo', '');

INSERT INTO categories (name, sort_order) VALUES
  ('全部', 0),
  ('宠物用品', 1),
  ('金渐层猫', 2),
  ('银渐层猫', 3);

-- 4. Fix Storage bucket policies
-- Enable storage if not already enabled
ALTER DATABASE postgres SET search_path TO extensions, public;

-- Create storage schema if not exists
CREATE SCHEMA IF NOT EXISTS storage;

-- Grant access to miaomiao-miya bucket
INSERT INTO storage.buckets (id, name, public)
VALUES ('miaomiao-miya', 'miaomiao-miya', true)
ON CONFLICT (id) DO NOTHING;

-- Drop existing policies and recreate
DROP POLICY IF EXISTS "Allow public read" ON storage.objects;
DROP POLICY IF EXISTS "Allow authenticated insert" ON storage.objects;
DROP POLICY IF EXISTS "Allow service role full access" ON storage.objects;

-- Public read policy
CREATE POLICY "Allow public read" ON storage.objects
  FOR SELECT USING (bucket_id = 'miaomiao-miya');

-- Authenticated insert/upload policy
CREATE POLICY "Allow authenticated insert" ON storage.objects
  FOR INSERT WITH CHECK (bucket_id = 'miaomiao-miya' AND auth.role() = 'authenticated');

-- Service role full access (for server-side uploads)
CREATE POLICY "Allow service role full access" ON storage.objects
  FOR ALL USING (bucket_id = 'miaomiao-miya');

-- 5. Verify
SELECT 'Categories:' as info;
SELECT id, name, sort_order FROM categories ORDER BY sort_order;
SELECT 'Settings:' as info;
SELECT key, LEFT(value, 30) as val FROM settings;
SELECT 'Storage buckets:' as info;
SELECT id, name, public FROM storage.buckets;
