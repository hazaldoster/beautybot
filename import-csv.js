#!/usr/bin/env node

// This is a simple script to import CSV data into Supabase
const fs = require('fs');
const { createClient } = require('@supabase/supabase-js');

// Hardcoded values from supabase status
const supabaseUrl = 'http://127.0.0.1:54321';
const supabaseServiceKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU';
const csvFilePath = './all_categories_20250207_031918.csv';

// Create Supabase client
const supabase = createClient(supabaseUrl, supabaseServiceKey);

// Simple CSV parser
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

async function importCSV() {
  try {
    console.log(`Reading CSV file from ${csvFilePath}...`);
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
      
      const { error } = await supabase
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
    
  } catch (error) {
    console.error('Error importing CSV:', error);
  }
}

// Run the import function
importCSV(); 