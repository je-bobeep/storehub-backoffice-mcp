#!/usr/bin/env python3
"""
StoreHub MCP Server
A Model Context Protocol server for querying StoreHub BackOffice APIs
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import logging
import time

try:
    import httpx
    from mcp.server import Server
    from mcp.types import Tool, TextContent
    from mcp.server.stdio import stdio_server
    import base64
    import json
    from dotenv import load_dotenv
except ImportError as e:
    print(f"Missing dependencies: {e}", file=sys.stderr)
    print("Please run: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)

# Load environment variables from .env file
load_dotenv()

# Configure logging to stderr only (MCP requirement)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Server configuration
# StoreHub API Configuration
STOREHUB_API_BASE = "https://api.storehubhq.com"
STOREHUB_API_KEY = os.getenv("STOREHUB_API_KEY")
STOREHUB_ACCOUNT_ID = os.getenv("STOREHUB_ACCOUNT_ID")  # Account identifier for authentication

# Rate limiting configuration
RATE_LIMIT_DELAY = 0.35  # 350ms delay between calls = ~2.8 calls per second (under 3/sec limit)
last_api_call_time = 0

# Simple product cache to avoid repeated API calls
product_cache = {}
CACHE_DURATION = 300  # 5 minutes cache

# Store ID cache - fetch real store ID from API
actual_store_id_cache = None

# Create server instance
server = Server("storehub-backoffice")

# Initialize configuration
api_configured = all([STOREHUB_API_KEY, STOREHUB_ACCOUNT_ID])

def get_auth_headers():
    """Create authentication headers for StoreHub API"""
    if not api_configured:
        return None
    
    # StoreHub uses Basic Auth with account_id as username and api_key as password
    auth_string = f"{STOREHUB_ACCOUNT_ID}:{STOREHUB_API_KEY}"
    auth_bytes = auth_string.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    
    return {
        "Authorization": f"Basic {auth_b64}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

async def rate_limited_delay():
    """Implement rate limiting to stay under 3 calls per second"""
    global last_api_call_time
    current_time = time.time()
    time_since_last_call = current_time - last_api_call_time
    
    if time_since_last_call < RATE_LIMIT_DELAY:
        delay = RATE_LIMIT_DELAY - time_since_last_call
        logger.info(f"Rate limiting: waiting {delay:.2f}s")
        await asyncio.sleep(delay)
    
    last_api_call_time = time.time()

def cleanup_cache():
    """Remove expired entries from product cache"""
    global product_cache, actual_store_id_cache
    current_time = time.time()
    expired_keys = [
        key for key, (data, cached_time) in product_cache.items()
        if current_time - cached_time > CACHE_DURATION
    ]
    for key in expired_keys:
        del product_cache[key]
    
    # Optional: Reset store ID cache every hour to handle store changes
    # actual_store_id_cache = None
    
    if expired_keys:
        logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")

async def get_product_name_cached(product_id: str) -> str:
    """Get product name with caching to reduce API calls"""
    global product_cache
    
    current_time = time.time()
    cache_key = f"product_{product_id}"
    
    # Periodically clean up cache
    if len(product_cache) > 100:  # Clean when cache gets large
        cleanup_cache()
    
    # Check cache first
    if cache_key in product_cache:
        cached_data, cached_time = product_cache[cache_key]
        if current_time - cached_time < CACHE_DURATION:
            return cached_data
    
    # Cache miss - fetch from API with rate limiting
    try:
        product_details = await make_api_request(f"/products/{product_id}")
        product_name = product_details.get("name", f"Product {product_id}")
        
        # Cache the result
        product_cache[cache_key] = (product_name, current_time)
        return product_name
    except Exception as e:
        logger.warning(f"Failed to fetch product name for {product_id}: {e}")
        return f"Product {product_id}"

async def make_api_request(endpoint: str, method: str = "GET", params: dict = None, data: dict = None):
    """Make authenticated request to StoreHub API with rate limiting"""
    if not api_configured:
        raise Exception("StoreHub API credentials not configured")
    
    # Apply rate limiting for all API calls
    await rate_limited_delay()
    
    headers = get_auth_headers()
    url = f"{STOREHUB_API_BASE}{endpoint}"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            if method == "GET":
                response = await client.get(url, headers=headers, params=params)
            elif method == "POST":
                response = await client.post(url, headers=headers, json=data)
            else:
                raise Exception(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 409:
                error_details = ""
                try:
                    error_body = e.response.text
                    logger.error(f"409 Rate limit details: {error_body}")
                    error_details = f" Details: {error_body[:200]}"
                except:
                    pass
                
                logger.error(f"Rate limit hit (409) on {endpoint}: {e.response.text}")
                # Wait longer and retry once
                await asyncio.sleep(2.0)  # Increased wait time to 2 seconds
                try:
                    if method == "GET":
                        response = await client.get(url, headers=headers, params=params)
                    elif method == "POST":
                        response = await client.post(url, headers=headers, json=data)
                    response.raise_for_status()
                    return response.json()
                except Exception as retry_error:
                    logger.error(f"Retry also failed: {retry_error}")
                    raise Exception(f"StoreHub API rate limit exceeded. Endpoint: {endpoint}. Please try again later.{error_details}")
            else:
                logger.error(f"API request failed: {e.response.status_code} - {e.response.text}")
                raise Exception(f"StoreHub API error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"API request error: {str(e)}")
            raise

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available StoreHub BackOffice tools"""
    return [
        Tool(
            name="get_inventory",
            description="Get current inventory levels for all products in the store, including stock quantities and stock level alerts.",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ),
        Tool(
            name="get_products",
            description="Get all products with details including names, SKUs, prices, categories, and variants.",
            inputSchema={
                "type": "object",
                "properties": {
                    "search_term": {
                        "type": "string",
                        "description": "Optional search term to filter products by name or SKU"
                    }
                },
                "additionalProperties": False
            }
        ),
        Tool(
            name="get_sales_analytics",
            description="Get sales data and transaction analytics for specified date ranges.",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_date": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format (e.g., 2024-01-01). Defaults to 7 days ago if not specified."
                    },
                    "to_date": {
                        "type": "string",
                        "description": "End date in YYYY-MM-DD format (e.g., 2024-01-31). Defaults to today if not specified."
                    },
                    "include_online": {
                        "type": "boolean",
                        "description": "Whether to include online orders in the analysis. Defaults to true."
                    }
                },
                "additionalProperties": False
            }
        ),
        Tool(
            name="get_customers",
            description="Get customer information and search customers by various criteria.",
            inputSchema={
                "type": "object",
                "properties": {
                    "search_term": {
                        "type": "string",
                        "description": "Search by customer name, email, or phone number"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of customers to return (default: 10, max: 100)",
                        "default": 10
                    }
                },
                "additionalProperties": False
            }
        ),
        Tool(
            name="get_stores",
            description="Get information about all stores in the account.",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ),
        Tool(
            name="test_api_connection",
            description="Test StoreHub API connection and diagnose any issues.",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ),
        Tool(
            name="get_employees",
            description="Get all employees with their details including names, email, phone, and modification dates.",
            inputSchema={
                "type": "object",
                "properties": {
                    "modified_since": {
                        "type": "string",
                        "description": "Optional date in YYYY-MM-DD format to get employees modified since this date (e.g., 2024-01-01)"
                    }
                },
                "additionalProperties": False
            }
        ),
        Tool(
            name="search_timesheets",
            description="Search timesheet records for employees with filtering options for store, employee, and date range.",
            inputSchema={
                "type": "object",
                "properties": {
                    "store_id": {
                        "type": "string",
                        "description": "Optional store ID to filter timesheets by specific store"
                    },
                    "employee_id": {
                        "type": "string",
                        "description": "Optional employee ID to filter timesheets for specific employee"
                    },
                    "from_date": {
                        "type": "string",
                        "description": "Optional start date in YYYY-MM-DD format to search clock-in records after this time"
                    },
                    "to_date": {
                        "type": "string",
                        "description": "Optional end date in YYYY-MM-DD format to search clock-in records before this time"
                    }
                },
                "additionalProperties": False
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls for StoreHub BackOffice operations"""
    
    try:
        if name == "get_inventory":
            return await handle_get_inventory(arguments)
        elif name == "get_products":
            return await handle_get_products(arguments)
        elif name == "get_sales_analytics":
            return await handle_get_sales_analytics(arguments)
        elif name == "get_customers":
            return await handle_get_customers(arguments)
        elif name == "get_stores":
            return await handle_get_stores(arguments)
        elif name == "test_api_connection":
            return await handle_test_api_connection(arguments)
        elif name == "get_employees":
            return await handle_get_employees(arguments)
        elif name == "search_timesheets":
            return await handle_search_timesheets(arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
            
    except Exception as e:
        logger.error(f"Error in tool call {name}: {str(e)}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def handle_get_inventory(arguments: Dict[str, Any]) -> List[TextContent]:
    """Get current inventory levels using StoreHub API"""
    try:
        # Call StoreHub Inventory API
        inventory_data = await make_api_request(f"/inventory/{STOREHUB_STORE_ID}")
        
        if not inventory_data:
            return [TextContent(type="text", text="📦 No inventory data found.")]
        
        response = "📦 **CURRENT INVENTORY STATUS**\n\n"
        
        # Track statistics
        total_products = len(inventory_data)
        low_stock_count = 0
        out_of_stock_count = 0
        
        for item in inventory_data:
            product_id = item.get("productId")
            stock_qty = item.get("quantityOnHand", 0)
            warning_stock = item.get("warningStock")
            ideal_stock = item.get("idealStock")
            
            # Try to get product details for better display
            try:
                product_name = await get_product_name_cached(product_id)
                # For inventory, we still need SKU, so make one additional call if not cached
                product_details = await make_api_request(f"/products/{product_id}")
                sku = product_details.get("sku", "N/A")
            except:
                product_name = f"Product {product_id}"
                sku = "N/A"
            
            # Determine stock status
            if stock_qty <= 0:
                status_icon = "🔴"
                status = "OUT OF STOCK"
                out_of_stock_count += 1
            elif warning_stock and stock_qty <= warning_stock:
                status_icon = "🟡"
                status = "LOW STOCK"
                low_stock_count += 1
            else:
                status_icon = "🟢"
                status = "IN STOCK"
            
            response += f"{status_icon} **{product_name}** ({sku})\n"
            response += f"   Current Stock: {stock_qty} units\n"
            if warning_stock:
                response += f"   Warning Level: {warning_stock} units\n"
            if ideal_stock:
                response += f"   Ideal Level: {ideal_stock} units\n"
            response += f"   Status: {status}\n"
            
            # Add recommendations for low stock
            if warning_stock and stock_qty <= warning_stock:
                if ideal_stock:
                    recommended_order = ideal_stock - stock_qty
                else:
                    recommended_order = max(warning_stock * 2, 10)
                response += f"   💡 **Recommendation**: Reorder {recommended_order} units\n"
            
            response += "\n"
        
        # Add summary
        response += f"📊 **INVENTORY SUMMARY**\n"
        response += f"   Total Products Tracked: {total_products}\n"
        response += f"   Out of Stock: {out_of_stock_count}\n"
        response += f"   Low Stock Alerts: {low_stock_count}\n"
        response += f"   In Stock: {total_products - low_stock_count - out_of_stock_count}\n"
        
        return [TextContent(type="text", text=response)]
        
    except Exception as e:
        return [TextContent(type="text", text=f"❌ Error retrieving inventory: {str(e)}")]

async def handle_get_products(arguments: Dict[str, Any]) -> List[TextContent]:
    """Get products using StoreHub API"""
    try:
        search_term = arguments.get("search_term", "").lower()
        
        # Get all products
        products_data = await make_api_request("/products")
        
        if not products_data:
            return [TextContent(type="text", text="📦 No products found.")]
        
        # Filter by search term if provided
        if search_term:
            filtered_products = []
            for product in products_data:
                name = product.get("name", "").lower()
                sku = product.get("sku", "").lower()
                if search_term in name or search_term in sku:
                    filtered_products.append(product)
            products_data = filtered_products
        
        if not products_data:
            return [TextContent(type="text", text=f"📦 No products found matching '{search_term}'.")]
        
        response = "🛍️ **PRODUCT CATALOG**\n"
        if search_term:
            response += f"Search: '{search_term}'\n"
        response += f"Found {len(products_data)} products\n\n"
        
        # Group products by category
        categories = {}
        for product in products_data:
            category = product.get("category", "Uncategorized")
            if category not in categories:
                categories[category] = []
            categories[category].append(product)
        
        for category, products in categories.items():
            response += f"📂 **{category}**\n"
            
            for product in products:
                name = product.get("name", "Unknown Product")
                sku = product.get("sku", "N/A")
                price = product.get("unitPrice", 0)
                price_type = product.get("priceType", "Fixed")
                track_stock = product.get("trackStockLevel", False)
                is_parent = product.get("isParentProduct", False)
                
                response += f"   • **{name}** ({sku})\n"
                if price_type == "Fixed":
                    response += f"     Price: ${price:.2f}\n"
                else:
                    response += f"     Price: Variable (base: ${price:.2f})\n"
                response += f"     Stock Tracking: {'Yes' if track_stock else 'No'}\n"
                
                if is_parent:
                    response += f"     Type: Parent Product (has variants)\n"
                
                if product.get("tags"):
                    response += f"     Tags: {', '.join(product['tags'])}\n"
                
                response += "\n"
        
        # Add summary
        total_products = len(products_data)
        tracked_products = len([p for p in products_data if p.get("trackStockLevel")])
        parent_products = len([p for p in products_data if p.get("isParentProduct")])
        
        response += f"📊 **SUMMARY**\n"
        response += f"   Total Products: {total_products}\n"
        response += f"   Stock Tracked: {tracked_products}\n"
        response += f"   With Variants: {parent_products}\n"
        response += f"   Categories: {len(categories)}\n"
        
        return [TextContent(type="text", text=response)]
        
    except Exception as e:
        return [TextContent(type="text", text=f"❌ Error retrieving products: {str(e)}")]

async def handle_get_sales_analytics(arguments: Dict[str, Any]) -> List[TextContent]:
    """Get sales analytics using StoreHub Transaction API"""
    try:
        from_date = arguments.get("from_date")
        to_date = arguments.get("to_date")
        include_online = arguments.get("include_online", True)
        
        # Set default dates if not provided
        if not from_date:
            from_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        if not to_date:
            to_date = datetime.now().strftime("%Y-%m-%d")
        
        # Validate date range to prevent API overload
        try:
            from_dt = datetime.strptime(from_date, "%Y-%m-%d")
            to_dt = datetime.strptime(to_date, "%Y-%m-%d")
            date_diff = (to_dt - from_dt).days
            
            if date_diff > 90:  # More than 3 months
                return [TextContent(type="text", text="❌ Date range too large. Please limit to 90 days or less to avoid API limits.")]
            
            if date_diff < 0:
                return [TextContent(type="text", text="❌ Invalid date range. 'from_date' must be before 'to_date'.")]
                
        except ValueError:
            return [TextContent(type="text", text="❌ Invalid date format. Please use YYYY-MM-DD format.")]
        
        # Get the actual store ID first
        actual_store_id = await get_actual_store_id()
        if not actual_store_id:
            return [TextContent(type="text", text="❌ Error: Could not determine store ID. Please check your store configuration.")]
        
        # StoreHub API limit: max 5000 transactions per call
        # For large date ranges, we need to chunk the requests
        all_transactions = []
        
        if date_diff <= 14:  # 2 weeks or less - single API call
            # Single API call for small date ranges
            params = {
                "from": from_date,
                "to": to_date,
                "storeId": actual_store_id,
                "includeOnline": str(include_online).lower()
            }
            
            logger.info(f"Single API call: {from_date} to {to_date} ({date_diff} days)")
            transactions_data = await make_api_request("/transactions", params=params)
            all_transactions = transactions_data if transactions_data else []
            
        else:
            # Chunk large date ranges into 2-week periods to stay under 5000 limit
            logger.info(f"Chunking large date range: {from_date} to {to_date} ({date_diff} days)")
            
            current_date = from_dt
            chunk_size = timedelta(days=14)  # 2-week chunks
            
            while current_date <= to_dt:
                chunk_end = min(current_date + chunk_size, to_dt)
                chunk_from = current_date.strftime("%Y-%m-%d")
                chunk_to = chunk_end.strftime("%Y-%m-%d")
                
                params = {
                    "from": chunk_from,
                    "to": chunk_to,
                    "storeId": actual_store_id,
                    "includeOnline": str(include_online).lower()
                }
                
                logger.info(f"Fetching chunk: {chunk_from} to {chunk_to}")
                
                try:
                    chunk_data = await make_api_request("/transactions", params=params)
                    if chunk_data:
                        all_transactions.extend(chunk_data)
                        logger.info(f"Retrieved {len(chunk_data)} transactions for {chunk_from} to {chunk_to}")
                except Exception as e:
                    logger.error(f"Failed to fetch chunk {chunk_from} to {chunk_to}: {e}")
                    # Continue with other chunks rather than failing completely
                
                current_date = chunk_end + timedelta(days=1)
        
        if not all_transactions:
            return [TextContent(type="text", text=f"📊 No transactions found for {from_date} to {to_date}.")]
        
        response = f"💰 **SALES ANALYTICS**\n"
        response += f"Period: {from_date} to {to_date} ({date_diff} days)\n"
        response += f"Found {len(all_transactions)} transactions"
        
        # Add chunking info if applicable
        if date_diff > 14:
            chunks_count = (date_diff // 14) + (1 if date_diff % 14 > 0 else 0)
            response += f" (retrieved in {chunks_count} API calls due to 5000/call limit)"
        
        response += "\n\n"
        
        # Calculate metrics
        total_revenue = sum(tx.get("total", 0) for tx in all_transactions)
        completed_transactions = [tx for tx in all_transactions if not tx.get("isCancelled", False)]
        cancelled_transactions = [tx for tx in all_transactions if tx.get("isCancelled", False)]
        online_transactions = [tx for tx in all_transactions if tx.get("channel") in ["ONLINE_PAYMENTS", "GRABFOOD", "SHOPEEFOOD", "FOODPANDA"]]
        
        avg_order_value = total_revenue / len(completed_transactions) if completed_transactions else 0
        
        response += f"📊 **KEY METRICS**\n"
        response += f"   Total Revenue: ${total_revenue:,.2f}\n"
        response += f"   Completed Orders: {len(completed_transactions)}\n"
        response += f"   Cancelled Orders: {len(cancelled_transactions)}\n"
        response += f"   Online Orders: {len(online_transactions)}\n"
        response += f"   Average Order Value: ${avg_order_value:.2f}\n\n"
        
        # Channel breakdown
        channel_stats = {}
        for tx in all_transactions:
            channel = tx.get("channel", "UNKNOWN")
            if channel not in channel_stats:
                channel_stats[channel] = {"count": 0, "revenue": 0}
            channel_stats[channel]["count"] += 1
            channel_stats[channel]["revenue"] += tx.get("total", 0)
        
        response += f"📈 **SALES BY CHANNEL**\n"
        for channel, stats in channel_stats.items():
            channel_name = {
                "OFFLINE_PAYMENTS": "In-Store",
                "ONLINE_PAYMENTS": "Online Store",
                "GRABFOOD": "GrabFood",
                "SHOPEEFOOD": "Shopee Food",
                "FOODPANDA": "FoodPanda"
            }.get(channel, channel)
            
            response += f"   {channel_name}: {stats['count']} orders, ${stats['revenue']:.2f}\n"
        
        # Top products analysis
        product_sales = {}
        for tx in completed_transactions:
            for item in tx.get("items", []):
                product_id = item.get("productId")
                quantity = item.get("quantity", 0)
                if product_id in product_sales:
                    product_sales[product_id] += quantity
                else:
                    product_sales[product_id] = quantity
        
        if product_sales:
            response += f"\n🏆 **TOP SELLING PRODUCTS**\n"
            sorted_products = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Batch fetch product names with rate limiting
            for i, (product_id, quantity) in enumerate(sorted_products, 1):
                try:
                    product_name = await get_product_name_cached(product_id)
                except:
                    product_name = f"Product {product_id}"
                
                response += f"   {i}. {product_name}: {quantity} units sold\n"
            
            # Add a note about rate limiting
            if len(sorted_products) > 1:
                response += f"\n   💡 Fetched product details with rate limiting (~{RATE_LIMIT_DELAY:.1f}s between calls)\n"
        
        # Insights
        response += f"\n💡 **INSIGHTS**\n"
        if avg_order_value > 100:
            response += "   ✅ Strong average order value\n"
        else:
            response += "   💡 Consider strategies to increase average order value\n"
            
        if len(online_transactions) / len(all_transactions) > 0.3:
            response += "   📱 Good online sales performance\n"
        else:
            response += "   📱 Opportunity to grow online sales\n"
            
        cancellation_rate = len(cancelled_transactions) / len(all_transactions) if all_transactions else 0
        if cancellation_rate > 0.1:
            response += f"   ⚠️ High cancellation rate ({cancellation_rate:.1%}) - investigate causes\n"
        else:
            response += "   ✅ Low cancellation rate\n"
        
        return [TextContent(type="text", text=response)]
        
    except Exception as e:
        return [TextContent(type="text", text=f"❌ Error retrieving sales analytics: {str(e)}")]

async def handle_get_customers(arguments: Dict[str, Any]) -> List[TextContent]:
    """Get customers using StoreHub API"""
    try:
        search_term = arguments.get("search_term", "")
        limit = min(arguments.get("limit", 10), 100)  # Cap at 100
        
        if search_term:
            # Use search API with query parameters
            # StoreHub supports firstName, lastName, email, phone search
            params = {}
            if "@" in search_term:
                params["email"] = search_term
            elif search_term.isdigit():
                params["phone"] = search_term
            else:
                # Try as first or last name
                params["firstName"] = search_term
            
            customers_data = await make_api_request("/customers", params=params)
        else:
            # Get all customers
            customers_data = await make_api_request("/customers")
        
        if not customers_data:
            return [TextContent(type="text", text="👥 No customers found.")]
        
        # Limit results
        customers_data = customers_data[:limit]
        
        response = f"👥 **CUSTOMERS**\n"
        if search_term:
            response += f"Search: '{search_term}'\n"
        response += f"Showing {len(customers_data)} customers\n\n"
        
        for customer in customers_data:
            first_name = customer.get("firstName", "")
            last_name = customer.get("lastName", "")
            email = customer.get("email", "")
            phone = customer.get("phone", "")
            member_id = customer.get("memberId", "")
            created_time = customer.get("createdTime", "")
            tags = customer.get("tags", [])
            
            full_name = f"{first_name} {last_name}".strip()
            response += f"👤 **{full_name}**\n"
            
            if email:
                response += f"   📧 {email}\n"
            if phone:
                response += f"   📱 {phone}\n"
            if member_id:
                response += f"   🎫 Member ID: {member_id}\n"
            if created_time:
                created_date = created_time.split("T")[0]
                response += f"   📅 Customer since: {created_date}\n"
            if tags:
                response += f"   🏷️ Tags: {', '.join(tags)}\n"
            
            # Show loyalty/store credit if available
            if customer.get("storeCreditsBalance"):
                response += f"   💰 Store Credit: ${customer['storeCreditsBalance']:.2f}\n"
            if customer.get("cashbackBalance"):
                response += f"   🎁 Cashback: ${customer['cashbackBalance']:.2f}\n"
            
            response += "\n"
        
        # Add summary
        response += f"📊 **SUMMARY**\n"
        response += f"   Total Customers Shown: {len(customers_data)}\n"
        members_count = len([c for c in customers_data if c.get("memberId")])
        response += f"   Members: {members_count}\n"
        with_email = len([c for c in customers_data if c.get("email")])
        response += f"   With Email: {with_email}\n"
        
        return [TextContent(type="text", text=response)]
        
    except Exception as e:
        return [TextContent(type="text", text=f"❌ Error retrieving customers: {str(e)}")]

async def handle_get_stores(arguments: Dict[str, Any]) -> List[TextContent]:
    """Get store information using StoreHub API"""
    try:
        stores_data = await make_api_request("/stores")
        
        if not stores_data:
            return [TextContent(type="text", text="🏪 No stores found.")]
        
        response = f"🏪 **STORE INFORMATION**\n"
        response += f"Found {len(stores_data)} store(s)\n\n"
        
        for store in stores_data:
            store_id = store.get("id", "")
            name = store.get("name", "Unnamed Store")
            address1 = store.get("address1", "")
            address2 = store.get("address2", "")
            city = store.get("city", "")
            state = store.get("state", "")
            country = store.get("country", "")
            postal_code = store.get("postalCode", "")
            phone = store.get("phone", "")
            email = store.get("email", "")
            website = store.get("website", "")
            
            response += f"🎯 **{name}**\n"
            response += f"   ID: {store_id}\n"
            
            # Address
            address_parts = [address1, address2, city, state, country, postal_code]
            address = ", ".join([part for part in address_parts if part])
            if address:
                response += f"   📍 {address}\n"
            
            if phone:
                response += f"   📞 {phone}\n"
            if email:
                response += f"   📧 {email}\n"
            if website:
                response += f"   🌐 {website}\n"
            
            response += "\n"
        
        return [TextContent(type="text", text=response)]
        
    except Exception as e:
        return [TextContent(type="text", text=f"❌ Error retrieving stores: {str(e)}")]

async def handle_test_api_connection(arguments: Dict[str, Any]) -> List[TextContent]:
    """Test StoreHub API connection and diagnose issues"""
    try:
        response = "🔧 **STOREHUB API CONNECTION TEST**\n\n"
        
        # Test 1: Check configuration
        if not api_configured:
            response += "❌ **Configuration**: API credentials not configured\n"
            response += "   Please set STOREHUB_API_KEY and STOREHUB_ACCOUNT_ID\n\n"
        else:
            response += "✅ **Configuration**: API credentials found\n"
            response += f"   Account ID: {STOREHUB_ACCOUNT_ID}\n"
            response += f"   API Key: {'*' * (len(STOREHUB_API_KEY) - 4) + STOREHUB_API_KEY[-4:]}\n\n"
        
        # Test 2: Simple API call (stores endpoint - usually lightweight)
        response += "🔍 **Testing Stores API** (lightweight endpoint)...\n"
        try:
            stores_data = await make_api_request("/stores")
            response += f"✅ **Stores API**: Success - Found {len(stores_data) if stores_data else 0} stores\n\n"
        except Exception as e:
            response += f"❌ **Stores API**: Failed - {str(e)}\n\n"
            
        # Test 3: Test transactions API according to official documentation
        response += "🔍 **Testing Transactions API** (per official docs)...\n"
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Test 3a: Minimal call (should work for most accounts)
        try:
            params = {"from": today, "to": today}
            transactions_data = await make_api_request("/transactions", params=params)
            response += f"✅ **Transactions API (minimal)**: Success - Found {len(transactions_data) if transactions_data else 0} transactions today\n"
        except Exception as e:
            response += f"❌ **Transactions API (minimal)**: Failed - {str(e)}\n"
            
        # Test 3b: With store filter (recommended for multi-store accounts)
        try:
            actual_store_id = await get_actual_store_id()
            if actual_store_id:
                params = {
                    "from": today,
                    "to": today,
                    "storeId": actual_store_id
                }
                transactions_data = await make_api_request("/transactions", params=params)
                response += f"✅ **Transactions API (with storeId)**: Success - Found {len(transactions_data) if transactions_data else 0} transactions\n"
            else:
                response += "❌ **Transactions API (with storeId)**: Failed - Could not determine store ID\n"
        except Exception as e:
            response += f"❌ **Transactions API (with storeId)**: Failed - {str(e)}\n"
            
        # Test 3c: Include online orders (this often increases transaction count significantly)
        try:
            actual_store_id = await get_actual_store_id()
            if actual_store_id:
                params = {
                    "from": today,
                    "to": today,
                    "storeId": actual_store_id,
                    "includeOnline": "true"
                }
                transactions_data = await make_api_request("/transactions", params=params)
                response += f"✅ **Transactions API (with online)**: Success - Found {len(transactions_data) if transactions_data else 0} transactions\n"
            else:
                response += "❌ **Transactions API (with online)**: Failed - Could not determine store ID\n"
        except Exception as e:
            response += f"❌ **Transactions API (with online)**: Failed - {str(e)}\n"
        
        response += "\n"
            
        # Test 4: Test recent 7-day range
        response += "🔍 **Testing Transactions API** (7 day range)...\n"
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        try:
            actual_store_id = await get_actual_store_id()
            if actual_store_id:
                params = {
                    "from": week_ago,
                    "to": today,
                    "storeId": actual_store_id,
                    "includeOnline": "true"
                }
                transactions_data = await make_api_request("/transactions", params=params)
                response += f"✅ **Transactions API (7 days)**: Success - Found {len(transactions_data) if transactions_data else 0} transactions\n\n"
            else:
                response += "❌ **Transactions API (7 days)**: Failed - Could not determine store ID\n\n"
        except Exception as e:
            response += f"❌ **Transactions API (7 days)**: Failed - {str(e)}\n\n"
            
        # Rate limiting info
        response += "⏱️ **Rate Limiting Configuration**\n"
        response += f"   Delay between calls: {RATE_LIMIT_DELAY}s\n"
        response += f"   Effective rate: ~{1/RATE_LIMIT_DELAY:.1f} calls/second\n"
        response += f"   StoreHub limit: 3 calls/second\n\n"
        
        # Cache info
        response += f"💾 **Cache Status**\n"
        response += f"   Cached products: {len(product_cache)}\n"
        response += f"   Cache duration: {CACHE_DURATION}s\n\n"
        
        response += "💡 **API Limitations & Recommendations**\n"
        response += "   • StoreHub API limit: Max 5000 transactions per call\n"
        response += "   • Large date ranges are automatically chunked into 2-week periods\n"
        response += "   • Including online orders doubles potential transaction count\n"
        response += "   • Use shorter date ranges (< 14 days) for single API calls\n"
        response += "   • Check StoreHub status if all tests fail\n"
        response += "   • Contact StoreHub support if 409 errors persist\n"
        
        return [TextContent(type="text", text=response)]
        
    except Exception as e:
        return [TextContent(type="text", text=f"❌ Error testing API connection: {str(e)}")]

async def handle_get_employees(arguments: Dict[str, Any]) -> List[TextContent]:
    """Get all employees using StoreHub API"""
    try:
        # Build query parameters
        params = {}
        if "modified_since" in arguments and arguments["modified_since"]:
            params["modifiedSince"] = arguments["modified_since"]
        
        # Call StoreHub Employees API
        employees_data = await make_api_request("/employees", params=params)
        
        if not employees_data:
            return [TextContent(type="text", text="👥 No employees found.")]
        
        response = "👥 **EMPLOYEES LIST**\n\n"
        
        # Sort employees by last name, then first name
        sorted_employees = sorted(employees_data, key=lambda emp: (
            emp.get("lastName", "").lower(),
            emp.get("firstName", "").lower()
        ))
        
        for employee in sorted_employees:
            emp_id = employee.get("id", "N/A")
            first_name = employee.get("firstName", "")
            last_name = employee.get("lastName", "")
            email = employee.get("email", "")
            phone = employee.get("phone", "")
            created_time = employee.get("createdTime", "")
            modified_time = employee.get("modifiedTime", "")
            
            # Format full name
            full_name = f"{first_name} {last_name}".strip()
            if not full_name:
                full_name = f"Employee {emp_id}"
            
            response += f"**{full_name}**\n"
            response += f"   ID: {emp_id}\n"
            
            if email:
                response += f"   📧 {email}\n"
            if phone:
                response += f"   📞 {phone}\n"
            
            # Format dates
            if created_time:
                try:
                    created_dt = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
                    response += f"   📅 Created: {created_dt.strftime('%Y-%m-%d %H:%M')}\n"
                except:
                    response += f"   📅 Created: {created_time}\n"
            
            if modified_time:
                try:
                    modified_dt = datetime.fromisoformat(modified_time.replace('Z', '+00:00'))
                    response += f"   🔄 Modified: {modified_dt.strftime('%Y-%m-%d %H:%M')}\n"
                except:
                    response += f"   🔄 Modified: {modified_time}\n"
            
            response += "\n"
        
        # Add summary
        response += f"📊 **SUMMARY**\n"
        response += f"   Total Employees: {len(employees_data)}\n"
        
        if "modified_since" in arguments and arguments["modified_since"]:
            response += f"   Modified Since: {arguments['modified_since']}\n"
        
        return [TextContent(type="text", text=response)]
        
    except Exception as e:
        return [TextContent(type="text", text=f"❌ Error retrieving employees: {str(e)}")]

async def handle_search_timesheets(arguments: Dict[str, Any]) -> List[TextContent]:
    """Search timesheet records using StoreHub API"""
    try:
        # Build query parameters
        params = {}
        if "store_id" in arguments and arguments["store_id"]:
            params["storeId"] = arguments["store_id"]
        if "employee_id" in arguments and arguments["employee_id"]:
            params["employeeId"] = arguments["employee_id"]
        if "from_date" in arguments and arguments["from_date"]:
            params["from"] = arguments["from_date"]
        if "to_date" in arguments and arguments["to_date"]:
            params["to"] = arguments["to_date"]
        
        # Call StoreHub Timesheets API
        timesheets_data = await make_api_request("/timesheets", params=params)
        
        if not timesheets_data:
            return [TextContent(type="text", text="⏰ No timesheet records found.")]
        
        response = "⏰ **TIMESHEET RECORDS**\n\n"
        
        # Group timesheets by employee for better readability
        employee_timesheets = {}
        for timesheet in timesheets_data:
            emp_id = timesheet.get("employeeId", "Unknown")
            if emp_id not in employee_timesheets:
                employee_timesheets[emp_id] = []
            employee_timesheets[emp_id].append(timesheet)
        
        # Cache employee names to avoid repeated API calls
        employee_names = {}
        
        for emp_id, emp_timesheets in employee_timesheets.items():
            # Get employee name (with caching)
            if emp_id not in employee_names:
                try:
                    # Try to get employee details
                    employees_data = await make_api_request("/employees")
                    emp_name = "Unknown Employee"
                    for emp in employees_data:
                        if emp.get("id") == emp_id:
                            first_name = emp.get("firstName", "")
                            last_name = emp.get("lastName", "")
                            emp_name = f"{first_name} {last_name}".strip()
                            if not emp_name:
                                emp_name = f"Employee {emp_id}"
                            break
                    employee_names[emp_id] = emp_name
                except:
                    employee_names[emp_id] = f"Employee {emp_id}"
            
            response += f"👤 **{employee_names[emp_id]}** (ID: {emp_id})\n"
            
            # Sort timesheets by clock-in time
            sorted_timesheets = sorted(emp_timesheets, key=lambda ts: ts.get("clockInTime", ""))
            
            total_hours = 0
            for timesheet in sorted_timesheets:
                store_id = timesheet.get("storeId", "N/A")
                clock_in = timesheet.get("clockInTime", "")
                clock_out = timesheet.get("clockOutTime", "")
                
                response += f"   📍 Store: {store_id}\n"
                
                # Format clock-in time
                if clock_in:
                    try:
                        clock_in_dt = datetime.fromisoformat(clock_in.replace('Z', '+00:00'))
                        response += f"   🕐 Clock In:  {clock_in_dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    except:
                        response += f"   🕐 Clock In:  {clock_in}\n"
                
                # Format clock-out time and calculate duration
                if clock_out:
                    try:
                        clock_out_dt = datetime.fromisoformat(clock_out.replace('Z', '+00:00'))
                        response += f"   🕐 Clock Out: {clock_out_dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
                        
                        # Calculate hours worked
                        if clock_in:
                            try:
                                clock_in_dt = datetime.fromisoformat(clock_in.replace('Z', '+00:00'))
                                duration = clock_out_dt - clock_in_dt
                                hours_worked = duration.total_seconds() / 3600
                                total_hours += hours_worked
                                response += f"   ⏱️  Duration: {hours_worked:.2f} hours\n"
                            except:
                                pass
                    except:
                        response += f"   🕐 Clock Out: {clock_out}\n"
                else:
                    response += f"   🕐 Clock Out: Still clocked in\n"
                
                response += "\n"
            
            # Show total hours for this employee
            if total_hours > 0:
                response += f"   📊 **Total Hours for {employee_names[emp_id]}**: {total_hours:.2f} hours\n"
            
            response += "\n"
        
        # Add overall summary
        response += f"📊 **OVERALL SUMMARY**\n"
        response += f"   Total Records: {len(timesheets_data)}\n"
        response += f"   Employees: {len(employee_timesheets)}\n"
        
        # Add filter info
        if params:
            response += f"   **Filters Applied:**\n"
            if "storeId" in params:
                response += f"   - Store ID: {params['storeId']}\n"
            if "employeeId" in params:
                response += f"   - Employee ID: {params['employeeId']}\n"
            if "from" in params:
                response += f"   - From Date: {params['from']}\n"
            if "to" in params:
                response += f"   - To Date: {params['to']}\n"
        
        return [TextContent(type="text", text=response)]
        
    except Exception as e:
        return [TextContent(type="text", text=f"❌ Error searching timesheets: {str(e)}")]

async def get_actual_store_id():
    """Get the real store ID from the stores API"""
    global actual_store_id_cache
    
    # Return cached value if we have it
    if actual_store_id_cache:
        return actual_store_id_cache
    
    try:
        stores_data = await make_api_request("/stores")
        
        if not stores_data:
            logger.error("No stores found in API response")
            return None
        
        # If only one store, use that
        if len(stores_data) == 1:
            actual_store_id_cache = stores_data[0].get("id")
            logger.info(f"Single store found, using ID: {actual_store_id_cache}")
            return actual_store_id_cache
        
        # Multiple stores - try to find matching one
        for store in stores_data:
            store_id = store.get("id", "")
            store_name = store.get("name", "")
            
            # Check if configured ACCOUNT_ID matches the actual ID, name, or is similar
            if (STOREHUB_ACCOUNT_ID == store_id or 
                STOREHUB_ACCOUNT_ID.lower() == store_name.lower() or
                STOREHUB_ACCOUNT_ID.lower() in store_name.lower()):
                actual_store_id_cache = store_id
                logger.info(f"Found matching store: {store_name} (ID: {store_id})")
                return actual_store_id_cache
        
        # If no match found, use the first store and log a warning
        actual_store_id_cache = stores_data[0].get("id")
        logger.warning(f"No exact match for '{STOREHUB_ACCOUNT_ID}', using first store: {actual_store_id_cache}")
        return actual_store_id_cache
        
    except Exception as e:
        logger.error(f"Failed to fetch store ID: {e}")
        return None

async def main():
    """Main function to run the MCP server"""
    logger.info("Starting StoreHub MCP Server...")
    
    if api_configured:
        logger.info(f"Connected to StoreHub API - Account: {STOREHUB_ACCOUNT_ID}")
    else:
        logger.warning("StoreHub API credentials not configured")
        logger.warning("Set STOREHUB_API_KEY and STOREHUB_ACCOUNT_ID environment variables")
    
    try:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream, 
                write_stream, 
                server.create_initialization_options()
            )
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())
