"""
WooCommerce Tools for WordPress MCP
Handles all WooCommerce operations
"""

from typing import List, Dict, Any
from mcp.types import Tool

class WooCommerceTools:
    """Tools for managing WooCommerce"""
    
    def __init__(self, wp_client):
        self.wp = wp_client
        self.tools = {
            # Products
            "wc_get_products": self.get_products,
            "wc_create_product": self.create_product,
            "wc_update_product": self.update_product,
            "wc_delete_product": self.delete_product,
            # Orders
            "wc_get_orders": self.get_orders,
            "wc_update_order": self.update_order,
            # Customers
            "wc_get_customers": self.get_customers,
            # Bulk operations
            "wc_bulk_update_prices": self.bulk_update_prices,
            "wc_bulk_update_stock": self.bulk_update_stock
        }
    
    def get_tools(self) -> List[Tool]:
        """Return list of available tools"""
        return [
            # Product tools
            Tool(
                name="wc_get_products",
                description="Get WooCommerce products",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "per_page": {
                            "type": "integer",
                            "description": "Number of products",
                            "default": 10
                        },
                        "status": {
                            "type": "string",
                            "description": "Product status",
                            "default": "publish"
                        },
                        "stock_status": {
                            "type": "string",
                            "description": "Stock status (instock, outofstock)"
                        }
                    }
                }
            ),
            Tool(
                name="wc_create_product",
                description="Create a new WooCommerce product",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Product name"
                        },
                        "type": {
                            "type": "string",
                            "description": "Product type (simple, variable)",
                            "default": "simple"
                        },
                        "regular_price": {
                            "type": "string",
                            "description": "Regular price"
                        },
                        "description": {
                            "type": "string",
                            "description": "Product description"
                        },
                        "short_description": {
                            "type": "string",
                            "description": "Short description"
                        },
                        "sku": {
                            "type": "string",
                            "description": "Product SKU"
                        },
                        "manage_stock": {
                            "type": "boolean",
                            "description": "Enable stock management",
                            "default": True
                        },
                        "stock_quantity": {
                            "type": "integer",
                            "description": "Stock quantity"
                        }
                    },
                    "required": ["name", "regular_price"]
                }
            ),
            Tool(
                name="wc_update_product",
                description="Update WooCommerce product",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "product_id": {
                            "type": "integer",
                            "description": "Product ID"
                        },
                        "regular_price": {
                            "type": "string",
                            "description": "New regular price"
                        },
                        "sale_price": {
                            "type": "string",
                            "description": "Sale price"
                        },
                        "stock_quantity": {
                            "type": "integer",
                            "description": "Stock quantity"
                        },
                        "stock_status": {
                            "type": "string",
                            "description": "Stock status"
                        }
                    },
                    "required": ["product_id"]
                }
            ),
            Tool(
                name="wc_delete_product",
                description="Delete WooCommerce product",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "product_id": {
                            "type": "integer",
                            "description": "Product ID"
                        }
                    },
                    "required": ["product_id"]
                }
            ),
            # Order tools
            Tool(
                name="wc_get_orders",
                description="Get WooCommerce orders",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "per_page": {
                            "type": "integer",
                            "description": "Number of orders",
                            "default": 10
                        },
                        "status": {
                            "type": "string",
                            "description": "Order status"
                        },
                        "customer": {
                            "type": "integer",
                            "description": "Customer ID"
                        }
                    }
                }
            ),
            Tool(
                name="wc_update_order",
                description="Update order status",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "order_id": {
                            "type": "integer",
                            "description": "Order ID"
                        },
                        "status": {
                            "type": "string",
                            "description": "New status"
                        },
                        "note": {
                            "type": "string",
                            "description": "Order note"
                        }
                    },
                    "required": ["order_id", "status"]
                }
            ),
            # Customer tools
            Tool(
                name="wc_get_customers",
                description="Get WooCommerce customers",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "per_page": {
                            "type": "integer",
                            "description": "Number of customers",
                            "default": 10
                        },
                        "search": {
                            "type": "string",
                            "description": "Search term"
                        }
                    }
                }
            ),
            # Bulk operations
            Tool(
                name="wc_bulk_update_prices",
                description="Bulk update product prices",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "products": {
                            "type": "array",
                            "description": "Array of {id, regular_price, sale_price}",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "integer"},
                                    "regular_price": {"type": "string"},
                                    "sale_price": {"type": "string"}
                                }
                            }
                        }
                    },
                    "required": ["products"]
                }
            ),
            Tool(
                name="wc_bulk_update_stock",
                description="Bulk update product stock",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "products": {
                            "type": "array",
                            "description": "Array of {id, stock_quantity}",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "integer"},
                                    "stock_quantity": {"type": "integer"}
                                }
                            }
                        }
                    },
                    "required": ["products"]
                }
            )
        ]
    
    def handles_tool(self, tool_name: str) -> bool:
        """Check if this module handles the given tool"""
        return tool_name in self.tools
    
    async def execute_tool(self, tool_name: str, arguments: Dict) -> Any:
        """Execute a tool with given arguments"""
        if tool_name in self.tools:
            return await self.tools[tool_name](**arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    # Product methods
    async def get_products(self, per_page=10, status="publish", stock_status=None):
        """Get products"""
        params = {"per_page": per_page, "status": status}
        if stock_status:
            params["stock_status"] = stock_status
            
        products = await self.wp.get_products(**params)
        return [{
            "id": p["id"],
            "name": p["name"],
            "sku": p["sku"],
            "price": p["price"],
            "regular_price": p["regular_price"],
            "sale_price": p["sale_price"],
            "stock_quantity": p.get("stock_quantity"),
            "stock_status": p["stock_status"],
            "status": p["status"]
        } for p in products]
    
    async def create_product(self, name: str, regular_price: str, **kwargs):
        """Create product"""
        data = {
            "name": name,
            "regular_price": regular_price,
            "type": kwargs.get("type", "simple"),
            **kwargs
        }
        result = await self.wp.post("wc/products", data)
        return {
            "success": True,
            "product_id": result["id"],
            "name": result["name"],
            "price": result["regular_price"]
        }
    
    async def update_product(self, product_id: int, **kwargs):
        """Update product"""
        result = await self.wp.put(f"wc/products/{product_id}", kwargs)
        return {
            "success": True,
            "product_id": result["id"],
            "message": f"Product {product_id} updated"
        }
    
    async def delete_product(self, product_id: int):
        """Delete product"""
        result = await self.wp.delete(f"wc/products/{product_id}")
        return {
            "success": True,
            "message": f"Product {product_id} deleted"
        }
    
    # Order methods
    async def get_orders(self, per_page=10, status=None, customer=None):
        """Get orders"""
        params = {"per_page": per_page}
        if status:
            params["status"] = status
        if customer:
            params["customer"] = customer
            
        orders = await self.wp.get_orders(**params)
        return [{
            "id": o["id"],
            "status": o["status"],
            "total": o["total"],
            "customer_id": o["customer_id"],
            "date_created": o["date_created"],
            "billing": o["billing"]
        } for o in orders]
    
    async def update_order(self, order_id: int, status: str, note=""):
        """Update order status"""
        data = {"status": status}
        if note:
            data["customer_note"] = note
            
        result = await self.wp.put(f"wc/orders/{order_id}", data)
        return {
            "success": True,
            "order_id": result["id"],
            "status": result["status"]
        }
    
    # Customer methods
    async def get_customers(self, per_page=10, search=None):
        """Get customers"""
        params = {"per_page": per_page}
        if search:
            params["search"] = search
            
        customers = await self.wp.get_customers(**params)
        return [{
            "id": c["id"],
            "email": c["email"],
            "first_name": c["first_name"],
            "last_name": c["last_name"],
            "username": c["username"]
        } for c in customers]
    
    # Bulk operations
    async def bulk_update_prices(self, products: List[Dict]):
        """Bulk update product prices"""
        results = []
        for product in products:
            try:
                data = {}
                if "regular_price" in product:
                    data["regular_price"] = product["regular_price"]
                if "sale_price" in product:
                    data["sale_price"] = product["sale_price"]
                    
                await self.wp.put(f"wc/products/{product['id']}", data)
                results.append({"id": product["id"], "success": True})
            except Exception as e:
                results.append({"id": product["id"], "success": False, "error": str(e)})
                
        return {
            "processed": len(results),
            "results": results
        }
    
    async def bulk_update_stock(self, products: List[Dict]):
        """Bulk update product stock"""
        results = []
        for product in products:
            try:
                data = {
                    "stock_quantity": product["stock_quantity"],
                    "stock_status": "instock" if product["stock_quantity"] > 0 else "outofstock"
                }
                await self.wp.put(f"wc/products/{product['id']}", data)
                results.append({"id": product["id"], "success": True})
            except Exception as e:
                results.append({"id": product["id"], "success": False, "error": str(e)})
                
        return {
            "processed": len(results),
            "results": results
        }
