"""Product service implementation."""

import uuid
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from datetime import datetime
from decimal import Decimal
from ..products.config import product_config
from ...shared.service_integration import event_bus, Event, EventType


class ProductCreationData(BaseModel):
    """Product creation data model."""
    seller_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=2000)
    price: Decimal = Field(..., gt=0, decimal_places=2)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    category: str = Field(..., min_length=1, max_length=100)
    inventory_quantity: int = Field(..., ge=0)
    low_stock_threshold: int = Field(default=5, ge=0)
    images: List[str] = Field(default_factory=list)

    @validator('price')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Price must be greater than 0')
        return v

    @validator('inventory_quantity')
    def validate_inventory_quantity(cls, v):
        if v < 0:
            raise ValueError('Inventory quantity cannot be negative')
        if v > product_config.max_inventory_quantity:
            raise ValueError(f'Inventory quantity cannot exceed {product_config.max_inventory_quantity}')
        return v


class ProductUpdates(BaseModel):
    """Product updates model."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=2000)
    price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    inventory_quantity: Optional[int] = Field(None, ge=0)
    low_stock_threshold: Optional[int] = Field(None, ge=0)
    images: Optional[List[str]] = None

    @validator('price')
    def validate_price(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Price must be greater than 0')
        return v

    @validator('inventory_quantity')
    def validate_inventory_quantity(cls, v):
        if v is not None:
            if v < 0:
                raise ValueError('Inventory quantity cannot be negative')
            if v > product_config.max_inventory_quantity:
                raise ValueError(f'Inventory quantity cannot exceed {product_config.max_inventory_quantity}')
        return v


class SearchQuery(BaseModel):
    """Search query model."""
    term: Optional[str] = None
    category: Optional[str] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    in_stock_only: bool = True
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class Product(BaseModel):
    """Product model."""
    id: str
    seller_id: str
    name: str
    description: str
    price: Decimal
    currency: str
    category: str
    images: List[str] = []
    inventory_quantity: int
    low_stock_threshold: int
    status: str = "active"
    created_at: datetime
    updated_at: datetime

    @property
    def is_available(self) -> bool:
        """Check if product is available for purchase."""
        return self.status == "active" and self.inventory_quantity > 0

    @property
    def is_low_stock(self) -> bool:
        """Check if product has low stock."""
        return self.inventory_quantity <= self.low_stock_threshold


class SearchResults(BaseModel):
    """Search results model."""
    products: List[Product]
    total_count: int
    page: int
    page_size: int


class ProductService:
    """Product service for managing product operations."""
    
    def __init__(self):
        """Initialize product service."""
        # In-memory storage for products (will be replaced with database in task 13)
        self._products: dict[str, Product] = {}
    
    async def create_product(self, product_data: ProductCreationData) -> Product:
        """
        Create a new product.
        
        Validates product data and creates a new product with unique ID.
        Sets status to 'out_of_stock' if inventory is zero.
        
        Args:
            product_data: Product creation data
            
        Returns:
            Created product
            
        Raises:
            ValueError: If product data is invalid
        """
        # Generate unique product ID
        product_id = str(uuid.uuid4())
        
        # Determine initial status based on inventory
        status = "active" if product_data.inventory_quantity > 0 else "out_of_stock"
        
        # Create product
        now = datetime.utcnow()
        product = Product(
            id=product_id,
            seller_id=product_data.seller_id,
            name=product_data.name,
            description=product_data.description,
            price=product_data.price,
            currency=product_data.currency,
            category=product_data.category,
            images=product_data.images,
            inventory_quantity=product_data.inventory_quantity,
            low_stock_threshold=product_data.low_stock_threshold,
            status=status,
            created_at=now,
            updated_at=now
        )
        
        # Store product
        self._products[product_id] = product
        
        # Publish product created event
        await event_bus.publish(Event(
            type=EventType.PRODUCT_CREATED,
            source_service="product_service",
            data={
                "product_id": product.id,
                "seller_id": product.seller_id,
                "name": product.name,
                "category": product.category,
                "price": float(product.price),
                "currency": product.currency,
                "inventory_quantity": product.inventory_quantity,
                "status": product.status
            }
        ))
        
        return product
    
    async def get_product_by_id(self, product_id: str) -> Optional[Product]:
        """
        Get product by ID.
        
        Args:
            product_id: Product ID
            
        Returns:
            Product if found, None otherwise
        """
        return self._products.get(product_id)
    
    async def update_product(self, product_id: str, updates: ProductUpdates) -> Product:
        """
        Update product information.
        
        Updates product fields and automatically adjusts status based on inventory.
        
        Args:
            product_id: Product ID to update
            updates: Product updates data
            
        Returns:
            Updated product
            
        Raises:
            ValueError: If product not found or updates are invalid
        """
        product = self._products.get(product_id)
        if not product:
            raise ValueError(f"Product with ID {product_id} not found")
        
        # Create updated product data
        update_data = {}
        if updates.name is not None:
            update_data['name'] = updates.name
        if updates.description is not None:
            update_data['description'] = updates.description
        if updates.price is not None:
            update_data['price'] = updates.price
        if updates.category is not None:
            update_data['category'] = updates.category
        if updates.inventory_quantity is not None:
            update_data['inventory_quantity'] = updates.inventory_quantity
        if updates.low_stock_threshold is not None:
            update_data['low_stock_threshold'] = updates.low_stock_threshold
        if updates.images is not None:
            update_data['images'] = updates.images
        
        # Update timestamp
        update_data['updated_at'] = datetime.utcnow()
        
        # Determine new status based on inventory
        new_inventory = update_data.get('inventory_quantity', product.inventory_quantity)
        if new_inventory == 0:
            update_data['status'] = "out_of_stock"
        elif product.status == "out_of_stock" and new_inventory > 0:
            update_data['status'] = "active"
        
        # Create updated product
        updated_product = product.copy(update=update_data)
        
        # Store updated product
        self._products[product_id] = updated_product
        
        return updated_product
    
    async def delete_product(self, product_id: str) -> None:
        """
        Delete a product.
        
        Removes product from catalog. In a real implementation, this would
        also cancel pending orders for this product.
        
        Args:
            product_id: Product ID to delete
            
        Raises:
            ValueError: If product not found
        """
        if product_id not in self._products:
            raise ValueError(f"Product with ID {product_id} not found")
        
        del self._products[product_id]
    
    async def search_products(self, query: SearchQuery) -> SearchResults:
        """
        Search products with basic filtering.
        
        Implements basic search functionality with term matching,
        category filtering, price range filtering, and stock filtering.
        
        Args:
            query: Search query parameters
            
        Returns:
            Search results with pagination
        """
        # Get all products
        all_products = list(self._products.values())
        
        # Apply filters
        filtered_products = []
        
        for product in all_products:
            # Skip if not in stock and in_stock_only is True
            if query.in_stock_only and product.inventory_quantity == 0:
                continue
            
            # Term search (case-insensitive, searches name and description)
            if query.term:
                term_lower = query.term.lower()
                if (term_lower not in product.name.lower() and 
                    term_lower not in product.description.lower()):
                    continue
            
            # Category filter (exact match, case-insensitive)
            if query.category:
                if product.category.lower() != query.category.lower():
                    continue
            
            # Price range filter
            if query.min_price is not None and product.price < query.min_price:
                continue
            if query.max_price is not None and product.price > query.max_price:
                continue
            
            filtered_products.append(product)
        
        # Sort by relevance (for now, just by name)
        filtered_products.sort(key=lambda p: p.name.lower())
        
        # Apply pagination
        total_count = len(filtered_products)
        start_idx = (query.page - 1) * query.page_size
        end_idx = start_idx + query.page_size
        paginated_products = filtered_products[start_idx:end_idx]
        
        return SearchResults(
            products=paginated_products,
            total_count=total_count,
            page=query.page,
            page_size=query.page_size
        )
    
    async def update_inventory(self, product_id: str, quantity: int) -> Product:
        """
        Update product inventory quantity.
        
        Updates inventory and automatically adjusts product status.
        
        Args:
            product_id: Product ID
            quantity: New inventory quantity
            
        Returns:
            Updated product
            
        Raises:
            ValueError: If product not found or quantity is invalid
        """
        if quantity < 0:
            raise ValueError("Inventory quantity cannot be negative")
        
        product = self._products.get(product_id)
        if not product:
            raise ValueError(f"Product with ID {product_id} not found")
        
        # Determine new status
        new_status = "active" if quantity > 0 else "out_of_stock"
        
        # Update product
        updated_product = product.copy(update={
            'inventory_quantity': quantity,
            'status': new_status,
            'updated_at': datetime.utcnow()
        })
        
        # Store updated product
        self._products[product_id] = updated_product
        
        # Publish inventory events
        if quantity == 0:
            await event_bus.publish(Event(
                type=EventType.PRODUCT_OUT_OF_STOCK,
                source_service="product_service",
                data={
                    "product_id": product.id,
                    "seller_id": product.seller_id,
                    "name": product.name,
                    "previous_quantity": product.inventory_quantity,
                    "new_quantity": quantity
                }
            ))
        elif quantity <= updated_product.low_stock_threshold:
            await event_bus.publish(Event(
                type=EventType.PRODUCT_INVENTORY_LOW,
                source_service="product_service",
                data={
                    "product_id": product.id,
                    "seller_id": product.seller_id,
                    "name": product.name,
                    "current_quantity": quantity,
                    "threshold": updated_product.low_stock_threshold
                }
            ))
        
        return updated_product
    
    async def get_products_by_seller(self, seller_id: str) -> List[Product]:
        """
        Get all products for a specific seller.
        
        Args:
            seller_id: Seller ID
            
        Returns:
            List of products for the seller
        """
        return [product for product in self._products.values() 
                if product.seller_id == seller_id]
    
    async def get_low_stock_products(self, seller_id: str) -> List[Product]:
        """
        Get products with low stock for a specific seller.
        
        Args:
            seller_id: Seller ID
            
        Returns:
            List of products with low stock
        """
        return [product for product in self._products.values() 
                if product.seller_id == seller_id and product.is_low_stock]