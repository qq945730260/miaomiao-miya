-- V15: Fixed database cleanup script
-- Run this in Supabase SQL Editor

-- 1. 删除所有分类
DELETE FROM categories;

-- 2. 重置序列（使用1而不是0）
SELECT setval('categories_id_seq', 1, false);

-- 3. 插入默认分类
INSERT INTO categories (name, sort_order) VALUES
  ('全部', 0),
  ('宠物用品', 1),
  ('金渐层猫', 2),
  ('银渐层猫', 3);

-- 4. 验证
SELECT id, name, sort_order FROM categories ORDER BY sort_order;
