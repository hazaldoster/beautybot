-- Create extension if it doesn't exist
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Create a new table for beauty products
CREATE TABLE beauty_products (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  product_id TEXT,
  name TEXT NOT NULL,
  price TEXT,
  rating TEXT,
  rating_score NUMERIC,
  subcategory TEXT,
  description TEXT,
  comments TEXT,
  color TEXT,
  url TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add RLS policies
ALTER TABLE beauty_products ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all users to read beauty products
CREATE POLICY "Allow all users to read beauty products"
  ON beauty_products
  FOR SELECT
  USING (true);

-- Create index on name for faster searches
CREATE INDEX beauty_products_name_idx ON beauty_products USING GIN (name gin_trgm_ops);
CREATE INDEX beauty_products_subcategory_idx ON beauty_products USING GIN (subcategory gin_trgm_ops); 