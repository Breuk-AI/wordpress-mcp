#!/usr/bin/env python3
"""
WordPress MCP Server - Test Version
Tests WordPress connection before full MCP implementation
"""

import asyncio
import json
import logging
import sys
from typing import Any, Dict, List, Optional

# Our imports
from wp_client import WordPressClient

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_connection():
    """Test WordPress connection"""
    logger.info("Testing WordPress connection...")
    
    # Load configuration
    import os
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    
    if not os.path.exists(config_path):
        logger.error(f"config.json not found! Please copy config.json.example to config.json and fill in your details.")
        return False
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Check config
    if not config.get('username') or config.get('username') == 'your_wordpress_username':
        logger.error("Please update config.json with your WordPress username and application password!")
        return False
    
    # Create client
    client = WordPressClient(
        site_url=config['site_url'],
        username=config['username'],
        app_password=config['app_password']
    )
    
    # Test connection
    async with client:
        if await client.test_connection():
            logger.info("✅ WordPress connection successful!")
            
            # Try to get some posts
            try:
                posts = await client.get_posts(per_page=5)
                logger.info(f"✅ Found {len(posts)} posts")
                for post in posts[:3]:
                    logger.info(f"   - {post.get('title', {}).get('rendered', 'No title')}")
            except Exception as e:
                logger.warning(f"Could not fetch posts: {e}")
            
            # Check for WooCommerce
            try:
                products = await client.get_products(per_page=5)
                logger.info(f"✅ WooCommerce is active! Found {len(products)} products")
            except Exception as e:
                logger.info("ℹ️  WooCommerce not detected or not accessible")
            
            return True
        else:
            logger.error("❌ WordPress connection failed!")
            logger.error("Please check:")
            logger.error("1. Site URL is correct (with https://)")
            logger.error("2. Username is correct")
            logger.error("3. Application Password is correct (spaces are OK)")
            logger.error("4. Application Passwords are enabled in WordPress")
            return False

async def main():
    """Main entry point"""
    logger.info("WordPress MCP Server - Connection Test")
    logger.info("=" * 50)
    
    success = await test_connection()
    
    if success:
        logger.info("\n✅ Connection test passed! Your WordPress site is ready for MCP.")
        logger.info("\nNext steps:")
        logger.info("1. Install MCP library: pip install mcp")
        logger.info("2. Run the full server: python server_mcp.py")
    else:
        logger.error("\n❌ Connection test failed. Please fix the issues above.")

if __name__ == "__main__":
    asyncio.run(main())
