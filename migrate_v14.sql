-- V14: Complete database fix
-- Run this in Supabase SQL Editor

-- 1. 删除所有分类数据
DELETE FROM categories;

-- 2. 重置序列到0（这样INSERT会自动分配ID）
SELECT setval('categories_id_seq', 0, false);

-- 3. 插入默认分类（不指定ID，让BIGSERIAL自动生成）
INSERT INTO categories (name, sort_order) VALUES
  ('全部', 0),
  ('宠物用品', 1),
  ('金渐层猫', 2),
  ('银渐层猫', 3);

-- 4. 验证数据
SELECT id, name, sort_order FROM categories ORDER BY sort_order;

-- 5. 检查是否有重复ID
SELECT id, COUNT(*) as cnt FROM categories GROUP BY id HAVING COUNT(*) > 1;
-- 应该返回0行

-- 6. 检查RLS策略
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual, with_check
FROM pg_policies
WHERE tablename = 'categories';

-- 如果没有策略，执行以下创建：
-- INSERT INTO policies (relname, policyname, permissive, policy, roles, cmd, qual, with_check)
-- VALUES ('categories', 'Allow all', 'OFF', '*', 'ALL', '*', 'TRUE', 'TRUE');
