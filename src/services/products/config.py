"""Product service configuration."""

from typing import Optional


class ProductServiceConfig:
    """Product service configuration settings."""
    
    def __init__(self):
        # Product Configuration
        self.max_product_images: int = 10
        self.max_product_name_length: int = 200
        self.max_product_description_length: int = 2000
        
        # Inventory Configuration
        self.default_low_stock_threshold: int = 5
        self.max_inventory_quantity: int = 10000
        
        # Search Configuration
        self.search_results_per_page: int = 20
        self.max_search_results: int = 1000
        
        # Category Configuration
        self.max_category_depth: int = 5


# Global configuration instance
product_config = ProductServiceConfig()