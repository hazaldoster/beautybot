# BeautyBot Project

This project contains a Supabase database setup for a beauty products database, which can be used to power a beauty products recommendation chatbot.

## Setup

### Prerequisites

- Node.js (v14 or higher)
- Supabase CLI
- Docker

### Installation

1. Clone this repository
2. Install dependencies:
   ```
   npm install
   ```

### Database Setup

The project uses Supabase for the database. You can set up either a local development environment or use a remote Supabase project.

#### Local Development

1. Start Supabase:
   ```
   supabase start
   ```

2. This will apply the migrations and set up the `beauty_products` table.

3. Import data from the CSV file:
   ```
   node import-csv.js
   ```

#### Remote Supabase Setup

1. Create a project on [Supabase](https://app.supabase.com/)

2. Update the `.env` file with your Supabase URL and anonymous key:
   ```
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_ANON_KEY=your-anon-key
   ```

3. Create the `beauty_products` table in your remote Supabase project:
   - Go to the SQL Editor in the Supabase dashboard
   - Create a new query and paste the SQL from `supabase/migrations/20240701000000_add_beauty_products.sql`
   - Run the query to create the table

4. Run the migration script to import data:
   ```
   npm run migrate
   ```

5. Test the connection:
   ```
   npm test
   ```

### Database Structure

The main table is `beauty_products` with the following structure:

- `id`: UUID (primary key, auto-generated)
- `product_id`: String (unique identifier from the source)
- `name`: String (product name)
- `price`: String (product price)
- `rating`: String (product rating)
- `rating_score`: Number (numerical rating score)
- `subcategory`: String (product subcategory)
- `description`: Text (product description)
- `comments`: Text (user comments)
- `color`: String (product color)
- `url`: String (product URL)
- `created_at`: Timestamp (auto-generated)
- `updated_at`: Timestamp (auto-generated)

### Testing

To test the database connection and query functionality:

```
npm test
```

This will:
1. Connect to the Supabase database
2. Count the total number of products in the database
3. Display a sample of 5 products

## API Usage

The beauty products database can be queried using the Supabase JavaScript client:

```javascript
const { createClient } = require('@supabase/supabase-js');

// Use environment variables for connection details
const supabaseUrl = process.env.SUPABASE_URL;
const supabaseAnonKey = process.env.SUPABASE_ANON_KEY;
const supabase = createClient(supabaseUrl, supabaseAnonKey);

// Example: Search for products by keyword
async function searchProducts(keyword) {
  const { data, error } = await supabase
    .from('beauty_products')
    .select('*')
    .or(`name.ilike.%${keyword}%,description.ilike.%${keyword}%`)
    .limit(10);
  
  if (error) {
    console.error('Error searching products:', error);
    return [];
  }
  
  return data;
}
```

## Turkish Language Support

The beauty products database contains product information in Turkish. The project includes features to handle Turkish language queries:

### Turkish Category Mapping

The API includes mapping between English and Turkish category terms:

```javascript
const categoryMapping = {
  'mascara': 'kas_maskarasi',
  'lipstick': 'ruj',
  'foundation': 'fondoten',
  'eyeshadow': 'far',
  'blush': 'allık',
  'concealer': 'kapatıcı',
  'eyeliner': 'eyeliner'
};
```

### Turkish Character Normalization

To improve search results, the API normalizes Turkish characters:

```javascript
function normalizeSearchTerm(term) {
  return term
    .toLowerCase()
    .replace(/ı/g, 'i')
    .replace(/ğ/g, 'g')
    .replace(/ü/g, 'u')
    .replace(/ş/g, 's')
    .replace(/ö/g, 'o')
    .replace(/ç/g, 'c');
}
```

### Turkish Chat Example

The project includes a chat integration example in Turkish (`chat-integration-example.js`) that demonstrates how to handle Turkish user queries and provide responses in Turkish.

## Integration with Chat UI

This database can be integrated with a chat UI to create a beauty products recommendation chatbot. The chatbot can use the database to:

1. Search for products based on user queries
2. Provide product recommendations
3. Answer questions about specific products
4. Compare different products

## Available Scripts

- `beauty-api.js`: Core API for interacting with the beauty products database
- `migrate-to-remote.js`: Script to migrate data to a remote Supabase instance
- `test-remote.js`: Script to test the connection to the remote Supabase
- `chat-integration-example.js`: Example of integrating the API with a chat interface

## License

This project is licensed under the MIT License - see the LICENSE file for details.