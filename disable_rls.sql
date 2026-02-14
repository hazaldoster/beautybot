-- Disable Row-Level Security for the beauty_products table
ALTER TABLE beauty_products DISABLE ROW LEVEL SECURITY;

-- Verify RLS status
SELECT tablename, rowsecurity FROM pg_tables WHERE tablename = 'beauty_products'; 