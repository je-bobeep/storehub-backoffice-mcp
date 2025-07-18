# StoreHub BackOffice MCP Server

A Model Context Protocol (MCP) server that provides intelligent access to StoreHub BackOffice APIs, enabling natural language queries for business insights, inventory management, sales analytics, and customer insights.

## 🚀 Features

### 📦 Inventory Management
- **Real-time stock checking** by product name or SKU
- **Low stock alerts** with threshold monitoring
- **Reorder recommendations** based on minimum stock levels
- **Stock level health indicators**

### 💰 Sales Analytics
- **Revenue summaries** with period analysis (today, week, month, custom ranges)
- **Order metrics** including average order value and daily trends
- **Top performing products** analysis
- **Performance insights** and recommendations

### 📋 Order Analysis
- **Order status breakdown** with completion rates
- **Order value analysis** and patterns
- **Trend analysis** for operational insights
- **Peak time identification**

### 🛍️ Product Performance
- **Category performance** analysis
- **Top sellers identification**
- **Low stock monitoring**
- **Product overview** with stock summaries

### 👥 Customer Insights
- **Customer base metrics** and loyalty analysis
- **Lifetime value** calculations
- **Repeat purchase patterns**
- **Spending behavior** analysis

### 👥 Employee Management
- **Complete Employee Directory**: View all employees with full contact details
- **Employee Information Tracking**: Names, emails, phone numbers, and IDs
- **Modification Monitoring**: Track when employee records were created or updated
- **Filtered Employee Search**: Find employees modified since specific dates
- **Contact Information Management**: Access comprehensive employee contact data

### ⏰ Timesheet Tracking & Management
- **Real-Time Timesheet Records**: Access all employee clock-in/out data
- **Employee-Specific Tracking**: Filter timesheets by individual employees
- **Store-Based Filtering**: View timesheets for specific store locations
- **Date Range Analysis**: Search timesheet records across custom date ranges
- **Automatic Hours Calculation**: Calculate total hours worked per employee
- **Active Status Detection**: Identify employees currently clocked in
- **Duration Analytics**: View shift lengths and working time patterns

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- StoreHub API credentials (API key and Account ID)

### Quick Setup

1. **Clone and setup the project:**
   ```bash
   git clone <repository-url>
   cd storehub-backoffice-mcp
   chmod +x setup.sh
   ./setup.sh
   ```

2. **Configure your API credentials:**
   ```bash
   # Edit the environment file
   nano storehub-mcp-server/.env
   
   # Add your credentials:
   STOREHUB_API_KEY=your_actual_api_key
   STOREHUB_ACCOUNT_ID=your_actual_account_id
   ```

3. **Test the server:**
   ```bash
   cd storehub-mcp-server
   source venv/bin/activate
   python main.py
   ```

### Claude Integration

Configure Claude to use this MCP server by adding the configuration to your Claude settings:

```json
{
  "mcpServers": {
    "storehub": {
      "command": "/path/to/your/storehub-backoffice-mcp/storehub-mcp-server/venv/bin/python3",
      "args": ["/path/to/your/storehub-backoffice-mcp/storehub-mcp-server/main.py"],
      "cwd": "/path/to/your/storehub-backoffice-mcp/storehub-mcp-server",
      "env": {
        "PYTHONPATH": "/path/to/your/storehub-backoffice-mcp/storehub-mcp-server",
        "STOREHUB_API_KEY": "your_actual_api_key_here",
        "STOREHUB_ACCOUNT_ID": "your_actual_account_id_here"
      }
    }
  }
}
```

**Note:** The configuration above shows the correct format but uses placeholder paths. Your actual `claude-config.json` file should use your real paths and credentials (which are kept local and not committed to version control).

## 🎯 Usage Examples

Once integrated with Claude, you can ask natural language questions like:

### Inventory Management
- "Show me current inventory levels and stock alerts"
- "Which products are out of stock or running low?"
- "Get inventory summary with reorder recommendations"

### Product Catalog
- "Show me all products in the catalog with complete details"
- "Find products with 'iPhone' in the name or barcode"
- "Display product details with pricing, costs, and profit margins"
- "Show me all parent products with their variant options"
- "Get product information including barcodes and subcategories"
- "Calculate profit margins for products with cost data"

### Sales Analytics
- "Get sales analytics for the past week with promotion analysis"
- "Show me revenue and transaction data with payment method breakdown"
- "Analyze sales performance by channel with delivery method insights"
- "Get comprehensive analytics including returns and service charges"

### Online Order Management
- "Create an online transaction for Shopee with delivery to customer address"
- "Process a Lazada order with pickup option"
- "Create custom channel order for dine-in with table service"
- "Cancel an online transaction due to inventory issues"
- "Process TikTok Shop order with delivery and tracking information"

### Customer Management
- "Create a new customer with complete contact information"
- "Update customer details including address and membership info"
- "Get detailed customer information by ID including loyalty data"
- "Search customers by first name, last name, email, or phone"
- "Add customer tags for segmentation and marketing"

### Transaction Management
- "Create a new sales transaction with items and payment method"
- "Process a return transaction with reason tracking"
- "Cancel a transaction and record the cancellation details"
- "Create transaction with customer association and employee tracking"

### Advanced Product Search
- "Find products in Electronics category with price between $100-$500"
- "Show me only products with stock tracking enabled"
- "Get products with cost data to analyze profit margins"
- "Find parent products that have variants in the Clothing category"

### Customer Information
- "Show me our customer database"
- "Search for customers with email containing '@gmail.com'"
- "Display customer information including loyalty data"

### Store Management
- "Get store information and configuration"
- "Show me store details and contact information"
- "Display store locations and addresses"

### Employee Management
- "Show me all employees in the system"
- "Get employee information with contact details"
- "Find employees modified since last week"

### Timesheet Management
- "Show me all timesheet records"
- "Get timesheets for a specific employee"
- "Search timesheets for a date range"
- "Calculate total hours worked by employee"

## 🛍️ Enhanced Product Catalog

The MCP server now provides **comprehensive product information** aligned with the complete StoreHub API Product Schema:

### ✅ Complete Product Information Display
- **Basic Info**: Product ID, name, SKU, barcode, category, subcategory
- **Pricing**: Unit price, cost, calculated profit margins
- **Product Types**: Fixed vs Variable pricing, stock tracking status
- **Variant Details**: 
  - **Parent Products**: Full variant groups with all available options
  - **Child Products**: Variant values and parent product relationships
- **Tags**: All product tags and classifications
- **Enhanced Search**: Now includes barcode filtering

### 📊 Comprehensive Statistics
- Total products in catalog
- Stock tracked products
- Parent products (with variants)
- Child products (variants)
- Products with barcodes
- Products with cost data
- Variable pricing products
- Category breakdown

### 🎯 Key Business Intelligence Features
- **💰 Profit Margin Calculation**: Automatically calculates and displays margins when both price and cost are available
- **🔄 Complete Variant Support**: 
  - Shows variant groups and options for parent products
  - Displays variant values and parent relationships for child products
- **🔍 Enhanced Search**: Search now works across names, SKUs, AND barcodes
- **📈 Better Business Insights**: Cost data and margins provide valuable business intelligence

## ✅ Complete StoreHub API Integration

The MCP server now provides **comprehensive StoreHub API coverage** with both read and write operations! Features include:

### 🔌 Live Data Sources (Read Operations)
- **Inventory API** (`/inventory/{storeId}`) - Real-time stock levels and alerts
- **Products API** (`/products`) - Comprehensive product catalog with complete schema: IDs, barcodes, costs, margins, variants, and tags
- **Transactions API** (`/transactions`) - Advanced sales analytics with promotions, returns, payment methods, and delivery insights
- **Customers API** (`/customers`) - Enhanced customer search with firstName, lastName, email, and phone filters
- **Stores API** (`/stores`) - Store configuration details
- **Employees API** (`/employees`) - Employee information and management
- **Timesheets API** (`/timesheets`) - Timesheet records and tracking

### ✍️ Business Operations (Write Operations)
- **Online Transactions API** (`/onlineTransactions`) - Create and cancel e-commerce orders across LAZADA, SHOPEE, ZALORA, WOOCOMMERCE, SHOPIFY, MAGENTO, TIK_TOK_SHOP, and CUSTOM channels
- **Customer Management API** (`/customers`) - Create, update, and manage customer records with complete contact information
- **Transaction Management API** (`/transactions`) - Process sales, returns, and cancellations with full audit trails
- **Advanced Product Lookup** (`/products/{id}`) - Individual product details and analysis

### 🛡️ Authentication & Security
- **Basic HTTP Authentication** using Store ID and API Key
- **Secure credential management** via environment variables
- **Rate limiting compliance** (max 3 calls/second)
- **Error handling** with detailed logging

### 📊 Comprehensive Business Management Features
**Read Operations:**
- Live inventory levels with stock alerts and reorder recommendations
- **Advanced sales analytics** with promotions, returns, payment methods, and delivery insights
- **Enhanced customer search** with firstName, lastName, email, and phone filters
- **Complete product catalog** with pricing, costs, margins, barcodes, variants, and business intelligence
- Store configuration and multi-location details
- Complete employee directory with contact information and modification tracking
- Real-time timesheet tracking with hours calculation and shift analysis

**Write Operations:**
- **E-commerce order processing** across major platforms (LAZADA, SHOPEE, ZALORA, WOOCOMMERCE, SHOPIFY, MAGENTO, TIK_TOK_SHOP)
- **Complete customer lifecycle management** - create, update, and manage customer records
- **Full transaction processing** - sales, returns, cancellations with audit trails
- **Advanced filtering and search** across all data types

**Business Intelligence:**
- Profit margin analysis and cost tracking
- Promotion effectiveness and usage analytics
- Return analysis with reason tracking
- Payment method performance insights
- Delivery and fulfillment method analysis
- Multi-channel performance comparison

All operations are performed directly with your StoreHub BackOffice in real-time with enterprise-grade security and rate limiting.



## 🏗️ Architecture

```
storehub-backoffice-mcp/
├── storehub-mcp-server/        # Main MCP server
│   ├── main.py                 # Server implementation
│   ├── requirements.txt        # Python dependencies
│   ├── .env.template          # Environment template
│   └── venv/                  # Virtual environment
├── setup.sh                   # Setup script
├── claude-config.json         # Claude configuration (local only)
└── README.md                  # Documentation
```

### Key Components

- **MCP Protocol Compliance**: Strict adherence to MCP standards
- **Async Architecture**: High-performance async/await implementation
- **Error Handling**: Comprehensive error handling and logging
- **Employee & Timesheet Management**: Complete HR and time tracking integration
- **Rich Analytics**: Detailed insights with actionable recommendations
- **Real-Time Data Processing**: Live synchronization with StoreHub systems

## 🔑 Available Tools

### `get_inventory`
Get current inventory levels for all products with stock alerts and recommendations.

**Parameters:** None required - returns all inventory data

### `get_products`
Get comprehensive product catalog with complete details including IDs, names, SKUs, barcodes, categories, subcategories, pricing, costs, margins, stock tracking, variant information, and tags.

**Parameters:**
- `search_term` (string, optional): Filter products by name, SKU, or barcode
- `category` (string, optional): Filter by specific category
- `min_price` / `max_price` (number, optional): Price range filters
- `stock_tracked_only` (boolean, optional): Show only products with stock tracking
- `has_variants` (boolean, optional): Show only parent products with variants
- `has_cost_data` (boolean, optional): Show only products with cost information

**Enhanced Features:**
- Complete StoreHub API Product Schema alignment
- Advanced filtering and search capabilities
- Profit margin calculation when cost data available
- Full variant group details for parent products
- Variant value relationships for child products
- Comprehensive business intelligence statistics

### `get_product_by_id`
Get detailed information for a specific product by ID including complete variant information, pricing, and stock details.

**Parameters:**
- `productId` (string, required): Product ID to retrieve detailed information for

### `get_sales_analytics`
Get comprehensive sales analytics and transaction data with advanced insights including promotions, returns, payment methods, and delivery analysis.

**Parameters:**
- `from_date` (string, optional): Start date (YYYY-MM-DD, defaults to 7 days ago)
- `to_date` (string, optional): End date (YYYY-MM-DD, defaults to today)
- `include_online` (boolean, optional): Include online orders (defaults to true)

**Enhanced Analytics:**
- Promotion effectiveness and usage analysis
- Service charge and shipping fee breakdown
- Delivery and fulfillment method performance
- Return analysis with reason tracking
- Payment method distribution and insights
- Channel-specific performance comparison

### `get_customers`
Get customer information with enhanced search and filtering capabilities using StoreHub API parameters.

**Parameters:**
- `search_term` (string, optional): General search by name, email, or phone
- `firstName` (string, optional): Search by first name (begins with)
- `lastName` (string, optional): Search by last name (begins with)
- `email` (string, optional): Search by email (contains)
- `phone` (string, optional): Search by phone (contains)
- `limit` (integer, optional): Max customers to return (default: 10, max: 100)

### `get_stores`
Get store information and configuration details.

**Parameters:** None required - returns all store data

### `get_employees`
Get all employees with their details including names, email, phone, and modification dates.

**Parameters:**
- `modified_since` (string, optional): Date in YYYY-MM-DD format to get employees modified since this date

### `search_timesheets`
Search timesheet records for employees with filtering options for store, employee, and date range.

**Parameters:**
- `store_id` (string, optional): Store ID to filter timesheets by specific store
- `employee_id` (string, optional): Employee ID to filter timesheets for specific employee
- `from_date` (string, optional): Start date in YYYY-MM-DD format to search clock-in records after this time
- `to_date` (string, optional): End date in YYYY-MM-DD format to search clock-in records before this time

## 🛒 Online Order Management Tools

### `create_online_transaction`
Create online transactions for e-commerce platforms with multi-channel support.

**Parameters:**
- `refId` (string, required): Unique marketplace identifier
- `storeId` (string, required): Store ID for this transaction
- `channel` (string, required): Platform - LAZADA, SHOPEE, ZALORA, WOOCOMMERCE, SHOPIFY, TIK_TOK_SHOP, MAGENTO, CUSTOM
- `shippingType` (string, required): Shipping method - delivery, pickup, dineIn, takeaway
- `total` / `subTotal` (number, required): Transaction amounts
- `items` (array, required): Order items with product details
- `customerRefId` (string, optional): Customer reference ID
- `deliveryAddress` (object, optional): Delivery address for delivery orders

### `cancel_online_transaction`
Cancel online transactions with proper audit trail.

**Parameters:**
- `refId` (string, required): Reference ID of transaction to cancel
- `cancelledTime` (string, optional): Cancellation timestamp (defaults to current time)

## 👥 Customer Management Tools

### `create_customer`
Create new customers with complete contact details and membership information.

**Parameters:**
- `refId` (string, required): Unique customer reference ID (UUID)
- `firstName` / `lastName` (string, required): Customer name
- `email` / `phone` (string, optional): Contact information
- `address1` / `city` / `state` / `postalCode` (string, optional): Address details
- `memberId` (string, optional): Member ID for loyalty program
- `tags` (array, optional): Customer tags for segmentation

### `update_customer`
Update existing customer information with validation.

**Parameters:**
- `refId` (string, required): Customer reference ID to update
- `firstName` / `lastName` (string, required): Updated name
- All optional fields from create_customer for updates

### `get_customer_by_id`
Get detailed information for a specific customer including loyalty data.

**Parameters:**
- `refId` (string, required): Customer reference ID to retrieve

## 💳 Transaction Management Tools

### `create_transaction`
Create new sales or return transactions with complete item and payment details.

**Parameters:**
- `refId` (string, required): Unique transaction reference ID
- `storeId` (string, required): Store ID for this transaction
- `transactionType` (string, required): Sale or Return
- `total` / `subTotal` (number, required): Transaction amounts
- `paymentMethod` (string, required): Cash or CreditCard
- `items` (array, required): Transaction items with product details
- `customerRefId` / `employeeId` (string, optional): Association IDs

### `cancel_transaction`
Cancel existing sales transactions with proper audit trail.

**Parameters:**
- `refId` (string, required): Reference ID of transaction to cancel
- `cancelledTime` (string, optional): Cancellation timestamp (defaults to current time)
- `cancelledBy` (string, optional): Employee ID who cancelled the transaction

## 🔒 Security & Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `STOREHUB_API_KEY` | Your StoreHub API token | Yes |
| `STOREHUB_ACCOUNT_ID` | Your account ID (subdomain from BackOffice URL) | Yes |
| `LOG_LEVEL` | Logging level (INFO, DEBUG, ERROR) | No |

### Security Best Practices

- Store API credentials in environment variables only
- Never commit `.env` files to version control
- Use HTTPS for all API communications
- Implement proper API rate limiting
- Monitor API usage and logs



## 🆘 Support

For issues, questions, or feature requests:

1. Check the documentation
2. Review existing issues
3. Create a new issue with detailed information
4. Include logs and error messages when applicable

## ✅ Recently Completed (Major Release)

- **✅ Complete Online Order Management**: Multi-channel e-commerce support
- **✅ Full Customer Lifecycle Management**: Create, update, search customers
- **✅ Comprehensive Transaction Processing**: Sales, returns, cancellations
- **✅ Advanced Sales Analytics**: Promotions, returns, payments, delivery insights
- **✅ Enhanced Product Catalog**: Complete schema, filtering, profit margins
- **✅ Write Operations**: Transform from read-only to full business management

## 🔮 Future Enhancements

- **Machine Learning Insights**: Predictive analytics and trend forecasting
- **Real-time Notifications**: Webhook integration for instant updates
- **Advanced Multi-store Management**: Cross-location inventory and reporting
- **Custom Dashboards**: Visual analytics and KPI monitoring
- **Advanced Automation**: Intelligent reordering and customer engagement
- **Integration Ecosystem**: Connect with accounting, CRM, and marketing platforms 
