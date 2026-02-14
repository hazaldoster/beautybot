#!/usr/bin/env node

/**
 * Migrate Beauty Products to Remote Supabase
 * 
 * This script creates the beauty_products table in the remote Supabase database
 * and migrates the data from the local database to the remote database.
 */

require('dotenv').config();
const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');

// Remote Supabase connection details
const remoteSupabaseUrl = process.env.SUPABASE_URL || 'https://pivuohouzdzlngvtwehw.supabase.co';
const remoteSupabaseKey = process.env.SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBpdnVvaG91emR6bG5ndnR3ZWh3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDA5Mjk0NjksImV4cCI6MjA1NjUwNTQ2OX0.WVJs7zs3sJANbzFZkb6JhauMREhtaU_qq7svHXKSGZ0';

// Create Supabase client for remote database
const remoteSupabase = createClient(remoteSupabaseUrl, remoteSupabaseKey);

// Read the migration SQL file
const migrationSQL = fs.readFileSync('./supabase/migrations/20240701000000_add_beauty_products.sql', 'utf-8');

/**
 * Create the beauty_products table in the remote database
 * This function uses the service role key to execute SQL directly
 */
async function createRemoteTable() {
  try {
    console.log('Checking if beauty_products table exists...');
    
    // Try to query the table to see if it exists
    const { error: queryError } = await remoteSupabase
      .from('beauty_products')
      .select('*', { count: 'exact', head: true });
    
    // If no error, table exists
    if (!queryError) {
      console.log('Table already exists, proceeding with data migration...');
      return true;
    }
    
    console.log('Table does not exist. Attempting to create it...');
    
    // Execute the SQL directly using the service role key
    const { error } = await remoteSupabase.rpc('exec_sql', { 
      query: migrationSQL 
    });
    
    if (error) {
      console.error('Error creating table:', error);
      
      console.log('\n⚠️ Could not create the table automatically.');
      console.log('\nTo create the table manually, please:');
      console.log('1. Go to the Supabase dashboard: https://app.supabase.com/');
      console.log('2. Select your project');
      console.log('3. Go to SQL Editor');
      console.log('4. Create a new query and paste the following SQL:');
      console.log('\n```sql');
      console.log(migrationSQL);
      console.log('```');
      console.log('\n5. Run the query to create the table');
      console.log('6. Then run this migration script again');
      
      return false;
    }
    
    console.log('Table created successfully!');
    return true;
  } catch (error) {
    console.error('Error checking/creating table:', error);
    return false;
  }
}

/**
 * Import data from CSV file to remote Supabase
 */
async function importCSVToRemote() {
  try {
    const csvFilePath = './all_categories_20250207_031918.csv';
    console.log(`Reading CSV file from ${csvFilePath}...`);
    
    if (!fs.existsSync(csvFilePath)) {
      console.error(`CSV file not found: ${csvFilePath}`);
      return false;
    }
    
    const csvContent = fs.readFileSync(csvFilePath, 'utf-8');
    
    console.log('Parsing CSV data...');
    const { headers, rows } = parseCSV(csvContent);
    
    console.log(`Found ${rows.length} rows with ${headers.length} columns`);
    
    // Map CSV columns to database columns
    const products = rows.map(row => {
      const product = {};
      
      headers.forEach((header, index) => {
        // Map CSV headers to database columns
        switch(header.toLowerCase()) {
          case 'product_id':
            product.product_id = row[index];
            break;
          case 'name':
            product.name = row[index] || 'Unknown Product';
            break;
          case 'price':
            product.price = row[index];
            break;
          case 'rating':
            product.rating = row[index];
            break;
          case 'rating_score':
            product.rating_score = parseFloat(row[index]) || null;
            break;
          case 'subcategory':
            product.subcategory = row[index];
            break;
          case 'description':
            product.description = row[index];
            break;
          case 'comments':
            product.comments = row[index];
            break;
          case 'color':
            product.color = row[index];
            break;
          case 'url':
            product.url = row[index];
            break;
        }
      });
      
      return product;
    });
    
    // Insert data in batches to avoid hitting request size limits
    const batchSize = 100;
    let successCount = 0;
    
    console.log(`Inserting ${products.length} products in batches of ${batchSize}...`);
    
    for (let i = 0; i < products.length; i += batchSize) {
      const batch = products.slice(i, i + batchSize);
      
      const { error } = await remoteSupabase
        .from('beauty_products')
        .insert(batch);
      
      if (error) {
        console.error(`Error inserting batch ${Math.floor(i / batchSize) + 1}:`, error);
      } else {
        successCount += batch.length;
        console.log(`Inserted batch ${Math.floor(i / batchSize) + 1} (${successCount}/${products.length} products)`);
      }
    }
    
    console.log(`Import completed. Inserted ${successCount} out of ${products.length} products.`);
    return successCount > 0;
  } catch (error) {
    console.error('Error importing CSV:', error);
    return false;
  }
}

/**
 * Simple CSV parser
 */
function parseCSV(csvText) {
  const lines = csvText.split('\n');
  if (lines.length === 0) return { headers: [], rows: [] };

  // Detect delimiter (comma, semicolon, tab)
  const firstLine = lines[0];
  let delimiter = ',';
  if (firstLine.includes(';')) delimiter = ';';
  if (firstLine.includes('\t')) delimiter = '\t';

  // Parse headers
  const headers = firstLine.split(delimiter).map(h => h.trim());

  // Parse rows
  const rows = lines
    .slice(1)
    .filter(line => line.trim() !== '')
    .map(line => line.split(delimiter).map(cell => cell.trim()));

  return { headers, rows };
}

/**
 * Test the connection to the remote database
 */
async function testRemoteConnection() {
  try {
    console.log('Testing connection to remote Supabase...');
    
    const { count, error } = await remoteSupabase
      .from('beauty_products')
      .select('*', { count: 'exact', head: true });
    
    if (error) {
      console.error('Error connecting to remote database:', error);
      return false;
    }
    
    console.log(`Connection successful! Found ${count || 0} products in the remote database.`);
    return true;
  } catch (error) {
    console.error('Unexpected error testing connection:', error);
    return false;
  }
}

/**
 * Main migration function
 */
async function migrateToRemote() {
  console.log('Starting migration to remote Supabase...');
  
  // Test connection
  const connectionSuccessful = await testRemoteConnection();
  if (!connectionSuccessful) {
    // Try to create the table
    const tableCreated = await createRemoteTable();
    if (!tableCreated) {
      console.error('Failed to create table. Migration aborted.');
      return;
    }
  }
  
  // Import data
  const importSuccessful = await importCSVToRemote();
  if (!importSuccessful) {
    console.error('Failed to import data. Migration aborted.');
    return;
  }
  
  console.log('Migration completed successfully!');
}

// Run the migration
migrateToRemote(); 