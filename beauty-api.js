#!/usr/bin/env node

/**
 * Beauty Products API
 * 
 * This module provides functions to interact with the beauty products database.
 * It can be used to integrate with a chat UI for a beauty products recommendation chatbot.
 */

require('dotenv').config();
const { createClient } = require('@supabase/supabase-js');

// Supabase connection details from environment variables
const supabaseUrl = process.env.SUPABASE_URL || 'https://pivuohouzdzlngvtwehw.supabase.co';
const supabaseAnonKey = process.env.SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBpdnVvaG91emR6bG5ndnR3ZWh3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDA5Mjk0NjksImV4cCI6MjA1NjUwNTQ2OX0.WVJs7zs3sJANbzFZkb6JhauMREhtaU_qq7svHXKSGZ0';

// Create Supabase client
const supabase = createClient(supabaseUrl, supabaseAnonKey);

/**
 * Search for beauty products by keyword
 * @param {string} keyword - The search keyword
 * @param {number} limit - Maximum number of results to return (default: 10)
 * @returns {Promise<Array>} - Array of matching products
 */
async function searchProducts(keyword, limit = 10) {
  try {
    // Normalize Turkish characters for better search
    const normalizedKeyword = normalizeSearchTerm(keyword);
    
    // Split the search term into words for better matching
    const searchTerms = normalizedKeyword.split(/\s+/).filter(term => term.length > 2);
    
    // Build the search query
    let query = '';
    searchTerms.forEach((term, index) => {
      if (index > 0) query += ',';
      query += `name.ilike.%${term}%`;
    });
    
    // Add description search
    searchTerms.forEach(term => {
      query += `,description.ilike.%${term}%`;
    });
    
    const { data, error } = await supabase
      .from('beauty_products')
      .select('*')
      .or(query)
      .limit(limit);
    
    if (error) {
      console.error('Error searching products:', error);
      return [];
    }
    
    return data;
  } catch (error) {
    console.error('Unexpected error in searchProducts:', error);
    return [];
  }
}

/**
 * Normalize search terms for better matching with Turkish text
 * @param {string} term - The search term to normalize
 * @returns {string} - Normalized search term
 */
function normalizeSearchTerm(term) {
  // Convert Turkish characters to their non-accented versions for better matching
  return term
    .toLowerCase()
    .replace(/ı/g, 'i')
    .replace(/ğ/g, 'g')
    .replace(/ü/g, 'u')
    .replace(/ş/g, 's')
    .replace(/ö/g, 'o')
    .replace(/ç/g, 'c');
}

/**
 * Get product details by product ID
 * @param {string} productId - The product ID
 * @returns {Promise<Object|null>} - Product details or null if not found
 */
async function getProductById(productId) {
  try {
    const { data, error } = await supabase
      .from('beauty_products')
      .select('*')
      .eq('product_id', productId)
      .single();
    
    if (error) {
      console.error('Error fetching product:', error);
      return null;
    }
    
    return data;
  } catch (error) {
    console.error('Unexpected error in getProductById:', error);
    return null;
  }
}

/**
 * Get products by category
 * @param {string} category - The product category
 * @param {number} limit - Maximum number of results to return (default: 10)
 * @returns {Promise<Array>} - Array of matching products
 */
async function getProductsByCategory(category, limit = 10) {
  try {
    // Map English category terms to Turkish terms found in the database
    const categoryMapping = {
      'mascara': 'kas_maskarasi',
      'lipstick': 'ruj',
      'foundation': 'fondoten',
      'eyeshadow': 'far',
      'blush': 'allık',
      'concealer': 'kapatıcı',
      'eyeliner': 'eyeliner'
    };
    
    const searchTerm = categoryMapping[category.toLowerCase()] || category;
    
    const { data, error } = await supabase
      .from('beauty_products')
      .select('*')
      .or(`subcategory.ilike.%${searchTerm}%,description.ilike.%${searchTerm}%`)
      .limit(limit);
    
    if (error) {
      console.error('Error fetching products by category:', error);
      return [];
    }
    
    return data;
  } catch (error) {
    console.error('Unexpected error in getProductsByCategory:', error);
    return [];
  }
}

/**
 * Get top-rated products
 * @param {number} limit - Maximum number of results to return (default: 10)
 * @returns {Promise<Array>} - Array of top-rated products
 */
async function getTopRatedProducts(limit = 10) {
  try {
    const { data, error } = await supabase
      .from('beauty_products')
      .select('*')
      .not('rating_score', 'is', null)
      .order('rating_score', { ascending: false })
      .limit(limit);
    
    if (error) {
      console.error('Error fetching top-rated products:', error);
      return [];
    }
    
    return data;
  } catch (error) {
    console.error('Unexpected error in getTopRatedProducts:', error);
    return [];
  }
}

/**
 * Get product recommendations based on a product ID
 * @param {string} productId - The product ID to base recommendations on
 * @param {number} limit - Maximum number of results to return (default: 5)
 * @returns {Promise<Array>} - Array of recommended products
 */
async function getProductRecommendations(productId, limit = 5) {
  try {
    // First get the product details
    const product = await getProductById(productId);
    
    if (!product) {
      return [];
    }
    
    // Then find similar products based on subcategory
    const { data, error } = await supabase
      .from('beauty_products')
      .select('*')
      .neq('product_id', productId) // Exclude the current product
      .ilike('subcategory', `%${product.subcategory || ''}%`)
      .limit(limit);
    
    if (error) {
      console.error('Error fetching product recommendations:', error);
      return [];
    }
    
    return data;
  } catch (error) {
    console.error('Unexpected error in getProductRecommendations:', error);
    return [];
  }
}

/**
 * Format product data for display in chat
 * @param {Object} product - The product data
 * @returns {string} - Formatted product information
 */
function formatProductForChat(product) {
  if (!product) return 'Ürün bulunamadı';
  
  return `
📦 **${product.name}**
💰 Fiyat: ${product.price}
⭐ Puan: ${product.rating}
${product.rating_score ? `📊 Puan Skoru: ${product.rating_score}` : ''}
${product.description ? `📝 Açıklama: ${product.description}` : ''}
${product.url ? `🔗 [Ürünü Görüntüle](${product.url})` : ''}
  `.trim();
}

/**
 * Process a user query and return relevant product information
 * @param {string} query - The user's query
 * @returns {Promise<string>} - Response to the user
 */
async function processUserQuery(query) {
  query = query.toLowerCase();
  
  // Check if query is asking for top products
  if (query.includes('en iyi') || query.includes('en yüksek') || query.includes('en çok puan')) {
    const products = await getTopRatedProducts(5);
    
    if (products.length === 0) {
      return "Şu anda en yüksek puanlı ürünleri bulamadım.";
    }
    
    let response = "İşte en yüksek puanlı güzellik ürünleri:\n\n";
    products.forEach((product, index) => {
      response += `${index + 1}. ${product.name} - Puan: ${product.rating_score || 'Belirtilmemiş'}\n`;
    });
    
    return response;
  }
  
  // Check if query is about a specific category
  const turkishCategories = {
    'rimel': 'kas_maskarasi',
    'maskara': 'kas_maskarasi',
    'ruj': 'ruj',
    'fondöten': 'fondoten',
    'far': 'far',
    'allık': 'allık',
    'kapatıcı': 'kapatıcı',
    'eyeliner': 'eyeliner',
    'kaş': 'kas'
  };
  
  for (const [category, dbTerm] of Object.entries(turkishCategories)) {
    if (query.includes(category)) {
      const products = await getProductsByCategory(dbTerm, 5);
      
      if (products.length === 0) {
        return `Şu anda ${category} ürünlerini bulamadım.`;
      }
      
      let response = `İşte beğenebileceğiniz ${category} ürünleri:\n\n`;
      products.forEach((product, index) => {
        response += `${index + 1}. ${product.name} - Fiyat: ${product.price}\n`;
      });
      
      return response;
    }
  }
  
  // Check for common beauty product related queries
  if (query.includes('makyaj') || query.includes('kozmetik') || query.includes('güzellik')) {
    const randomCategories = Object.keys(turkishCategories);
    const randomCategory = randomCategories[Math.floor(Math.random() * randomCategories.length)];
    const products = await getProductsByCategory(turkishCategories[randomCategory], 5);
    
    if (products.length > 0) {
      let response = `Sizin için bazı popüler ${randomCategory} ürünleri buldum:\n\n`;
      products.forEach((product, index) => {
        response += `${index + 1}. ${product.name} - Fiyat: ${product.price}\n`;
      });
      return response;
    }
  }
  
  // Default to general search
  const products = await searchProducts(query, 5);
  
  if (products.length === 0) {
    return `"${query}" ile eşleşen güzellik ürünleri bulamadım. Farklı bir arama terimi deneyin veya en yüksek puanlı ürünleri sorun.`;
  }
  
  let response = `"${query}" ile eşleşen güzellik ürünleri:\n\n`;
  products.forEach((product, index) => {
    response += `${index + 1}. ${product.name} - Fiyat: ${product.price}\n`;
  });
  
  return response;
}

// Export the functions for use in other modules
module.exports = {
  searchProducts,
  getProductById,
  getProductsByCategory,
  getTopRatedProducts,
  getProductRecommendations,
  formatProductForChat,
  processUserQuery
};

// If this script is run directly, demonstrate some functionality
if (require.main === module) {
  async function demonstrateAPI() {
    console.log('Beauty Products API Demo');
    console.log('------------------------');
    
    // Demo search
    const searchTerm = 'mascara';
    console.log(`\nSearching for "${searchTerm}"...`);
    const searchResults = await searchProducts(searchTerm, 3);
    console.log(`Found ${searchResults.length} results:`);
    searchResults.forEach((product, index) => {
      console.log(`\n${index + 1}. ${product.name}`);
      console.log(`   Price: ${product.price}`);
    });
    
    // Demo top-rated products
    console.log('\nGetting top-rated products...');
    const topProducts = await getTopRatedProducts(3);
    console.log(`Found ${topProducts.length} top-rated products:`);
    topProducts.forEach((product, index) => {
      console.log(`\n${index + 1}. ${product.name}`);
      console.log(`   Rating Score: ${product.rating_score}`);
    });
    
    // Demo user query processing
    const userQuery = "I'm looking for a good mascara";
    console.log(`\nProcessing user query: "${userQuery}"`);
    const response = await processUserQuery(userQuery);
    console.log('\nResponse:');
    console.log(response);
  }
  
  demonstrateAPI();
} 