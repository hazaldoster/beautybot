#!/usr/bin/env node

// This is a simple script to test querying the beauty_products table
const { createClient } = require('@supabase/supabase-js');

// Hardcoded values from supabase status
const supabaseUrl = 'http://127.0.0.1:54321';
const supabaseServiceKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU';

// Create Supabase client
const supabase = createClient(supabaseUrl, supabaseServiceKey);

async function testQuery() {
  try {
    console.log('Connecting to Supabase at', supabaseUrl);
    
    // Test query - count total products
    const { count, error: countError } = await supabase
      .from('beauty_products')
      .select('*', { count: 'exact' });
    
    if (countError) {
      console.error('Error counting products:', countError);
      return;
    }
    
    console.log(`Total products in database: ${count}`);
    
    // Get a sample of products
    const { data: products, error } = await supabase
      .from('beauty_products')
      .select('*')
      .limit(5);
    
    if (error) {
      console.error('Error fetching products:', error);
      return;
    }
    
    console.log('Sample products:');
    products.forEach((product, index) => {
      console.log(`\nProduct ${index + 1}:`);
      console.log(`ID: ${product.id}`);
      console.log(`Product ID: ${product.product_id}`);
      console.log(`Name: ${product.name}`);
      console.log(`Price: ${product.price}`);
      console.log(`Rating: ${product.rating}`);
      console.log(`Rating Score: ${product.rating_score}`);
    });
    
    // Test search functionality
    const searchTerm = 'mascara';
    console.log(`\nSearching for products containing "${searchTerm}"...`);
    
    const { data: searchResults, error: searchError } = await supabase
      .from('beauty_products')
      .select('*')
      .or(`name.ilike.%${searchTerm}%,description.ilike.%${searchTerm}%`)
      .limit(3);
    
    if (searchError) {
      console.error('Error searching products:', searchError);
      return;
    }
    
    console.log(`Found ${searchResults.length} products matching "${searchTerm}":`);
    searchResults.forEach((product, index) => {
      console.log(`\nSearch Result ${index + 1}:`);
      console.log(`Name: ${product.name}`);
      console.log(`Description: ${product.description}`);
    });
    
  } catch (error) {
    console.error('Unexpected error:', error);
  }
}

// Run the test query
testQuery(); 