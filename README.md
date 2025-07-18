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
- "Get sales analytics for the past week"
- "Show me revenue and transaction data for last month"
- "Analyze sales performance by channel (online vs in-store)"

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

## ✅ Real-Time API Integration

The MCP server is now **fully integrated** with live StoreHub APIs! Features include:

### 🔌 Live Data Sources
- **Inventory API** (`/inventory/{storeId}`) - Real-time stock levels and alerts
- **Products API** (`/products`) - Comprehensive product catalog with complete schema: IDs, barcodes, costs, margins, variants, and tags
- **Transactions API** (`/transactions`) - Sales data and analytics  
- **Customers API** (`/customers`) - Customer information and search
- **Stores API** (`/stores`) - Store configuration details
- **Employees API** (`/employees`) - Employee information and management
- **Timesheets API** (`/timesheets`) - Timesheet records and tracking

### 🛡️ Authentication & Security
- **Basic HTTP Authentication** using Store ID and API Key
- **Secure credential management** via environment variables
- **Rate limiting compliance** (max 3 calls/second)
- **Error handling** with detailed logging

### 📊 Real-Time Features
- Live inventory levels with stock alerts
- Actual sales data and transaction analytics
- Real customer information and search
- **Enhanced product catalog with complete details**: pricing, costs, margins, barcodes, variants, and business intelligence
- Store configuration and details
- Complete employee directory with contact information
- Real-time timesheet tracking and hours calculation

All data is retrieved directly from your StoreHub BackOffice in real-time.



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

**Enhanced Features:**
- Complete StoreHub API Product Schema alignment
- Profit margin calculation when cost data available
- Full variant group details for parent products
- Variant value relationships for child products
- Comprehensive business intelligence statistics

### `get_sales_analytics`
Get comprehensive sales analytics and transaction data for specified periods.

**Parameters:**
- `from_date` (string, optional): Start date (YYYY-MM-DD, defaults to 7 days ago)
- `to_date` (string, optional): End date (YYYY-MM-DD, defaults to today)
- `include_online` (boolean, optional): Include online orders (defaults to true)

### `get_customers`
Get customer information with search and filtering capabilities.

**Parameters:**
- `search_term` (string, optional): Search by name, email, or phone
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

## 🔮 Future Enhancements

- **Advanced Analytics**: Machine learning insights
- **Real-time Notifications**: Webhook integration
- **Multi-store Support**: Manage multiple locations
- **Custom Dashboards**: Visual analytics integration
- **API Rate Optimization**: Intelligent caching and batching 
