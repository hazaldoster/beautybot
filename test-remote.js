#!/usr/bin/env node

/**
 * Test Remote Supabase Connection
 * 
 * This script tests the connection to the remote Supabase database
 * and retrieves a sample of beauty products.
 */

require('dotenv').config();
const { createClient } = require('@supabase/supabase-js');

// Remote Supabase connection details
const supabaseUrl = process.env.SUPABASE_URL || 'https://pivuohouzdzlngvtwehw.supabase.co';
const supabaseAnonKey = process.env.SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBpdnVvaG91emR6bG5ndnR3ZWh3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDA5Mjk0NjksImV4cCI6MjA1NjUwNTQ2OX0.WVJs7zs3sJANbzFZkb6JhauMREhtaU_qq7svHXKSGZ0';

// Create Supabase client
const supabase = createClient(supabaseUrl, supabaseAnonKey);

/**
 * Test the connection to the remote database
 */
async function testRemoteConnection() {
  try {
    console.log(`Testing connection to Supabase at ${supabaseUrl}...`);
    
    // Try to get the count of products
    const { count, error: countError } = await supabase
      .from('beauty_products')
      .select('*', { count: 'exact', head: true });
    
    if (countError) {
      console.error('Error connecting to database:', countError);
      return false;
    }
    
    console.log(`Connection successful! Found ${count || 0} products in the database.`);
    
    // Retrieve a sample of products
    const { data, error } = await supabase
      .from('beauty_products')
      .select('*')
      .limit(5);
    
    if (error) {
      console.error('Error retrieving products:', error);
      return false;
    }
    
    console.log('\nSample products:');
    data.forEach((product, index) => {
      console.log(`\nProduct ${index + 1}:`);
      console.log(`  ID: ${product.id}`);
      console.log(`  Name: ${product.name}`);
      console.log(`  Price: ${product.price}`);
      console.log(`  Category: ${product.description || 'N/A'}`);
    });
    
    return true;
  } catch (error) {
    console.error('Unexpected error testing connection:', error);
    return false;
  }
}

// Run the test
testRemoteConnection(); 