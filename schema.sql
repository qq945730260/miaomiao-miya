-- V6 Database Schema for Supabase
-- Run this in Supabase SQL Editor

-- Products table
CREATE TABLE IF NOT EXISTS products (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  title TEXT,
  category TEXT NOT NULL,
  price DECIMAL(10,2) NOT NULL,
  stock INTEGER NOT NULL DEFAULT 0,
  image TEXT,
  detail_image TEXT,
  description TEXT,
  wechat TEXT,
  qq TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Categories table
CREATE TABLE IF NOT EXISTS categories (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  sort_order INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
  id BIGSERIAL PRIMARY KEY,
  order_number TEXT NOT NULL,
  email TEXT NOT NULL,
  password TEXT NOT NULL,
  product_id BIGINT NOT NULL REFERENCES products(id),
  qty INTEGER NOT NULL,
  total DECIMAL(10,2) NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Settings table (key-value)
CREATE TABLE IF NOT EXISTS settings (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Admin credentials
INSERT INTO settings (key, value) VALUES ('admin_username', 'xuxu') ON CONFLICT (key) DO NOTHING;
INSERT INTO settings (key, value) VALUES ('admin_password', '5361172') ON CONFLICT (key) DO NOTHING;

-- Insert default categories if empty (no hardcoded IDs - let BIGSERIAL assign)
-- Use INSERT...WHERE NOT EXISTS to avoid conflicts with existing data
INSERT INTO categories (name, sort_order)
SELECT '全部', 0
WHERE NOT EXISTS (SELECT 1 FROM categories WHERE name = '全部');

INSERT INTO categories (name, sort_order)
SELECT '宠物用品', 1
WHERE NOT EXISTS (SELECT 1 FROM categories WHERE name = '宠物用品');

INSERT INTO categories (name, sort_order)
SELECT '金渐层猫', 2
WHERE NOT EXISTS (SELECT 1 FROM categories WHERE name = '金渐层猫');

INSERT INTO categories (name, sort_order)
SELECT '银渐层猫', 3
WHERE NOT EXISTS (SELECT 1 FROM categories WHERE name = '银渐层猫');

-- Deduplicate categories: keep lowest id for each name, delete duplicates
DELETE FROM categories
WHERE id NOT IN (
  SELECT MIN(id) FROM categories GROUP BY name
);
