"""Product repository interface."""

from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime
import uuid
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_, desc, asc

from ...shared.models import Product, ProductStatus, InventoryInfo, SearchResults
from ...shared.db_models import ProductDB
from .service import ProductCreationData, ProductUpdates, SearchQuery


class ProductRepository(ABC):
    """Abstract product repository interface."""
    
    @abstractmethod
    async def create_product(self, product_data: ProductCreationData) -> Product:
        """Create a new product."""
        pass
    
    @abstractmethod
    async def get_product_by_id(self, product_id: str) -> Optional[Product]:
        """Get product by ID."""
        pass
    
    @abstractmethod
    async def update_product(self, product_id: str, updates: ProductUpdates) -> Product:
        """Update product."""
        pass
    
    @abstractmethod
    async def delete_product(self, product_id: str) -> None:
        """Delete product."""
        pass
    
    @abstractmethod
    async def search_products(self, query: SearchQuery) -> SearchResults:
        """Search products."""
        pass
    
    @abstractmethod
    async def get_products_by_seller(self, seller_id: str) -> List[Product]:
        """Get products by seller."""
        pass
    
    @abstractmethod
    async def update_inventory(self, product_id: str, quantity: int) -> Product:
        """Update product inventory."""
        pass
    
    @abstractmethod
    async def get_low_stock_products(self, seller_id: str) -> List[Product]:
        """Get products with low stock."""
        pass


class SQLAlchemyProductRepository(ProductRepository):
    """SQLAlchemy implementation of product repository."""
    
    def __init__(self, db_session: Session):
        """Initialize with database session."""
        self.db = db_session
    
    def _db_to_pydantic(self, db_product: ProductDB) -> Product:
        """Convert SQLAlchemy model to Pydantic model."""
        inventory = InventoryInfo(
            quantity=db_product.inventory_quantity,
            low_stock_threshold=db_product.low_stock_threshold,
            track_inventory=db_product.track_inventory
        )
        
        return Product(
            id=db_product.id,
            seller_id=db_product.seller_id,
            name=db_product.name,
            description=db_product.description,
            price=db_product.price,
            currency=db_product.currency,
            category=db_product.category,
            images=db_product.images or [],
            inventory=inventory,
            status=db_product.status,
            created_at=db_product.created_at,
            updated_at=db_product.updated_at
        )
    
    async def create_product(self, product_data: ProductCreationData) -> Product:
        """Create a new product."""
        product_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        # Determine initial status based on inventory
        initial_status = ProductStatus.ACTIVE
        if product_data.inventory.track_inventory and product_data.inventory.quantity == 0:
            initial_status = ProductStatus.OUT_OF_STOCK
        
        db_product = ProductDB(
            id=product_id,
            seller_id=product_data.seller_id,
            name=product_data.name,
            description=product_data.description,
            price=product_data.price,
            currency=product_data.currency,
            category=product_data.category,
            images=product_data.images,
            inventory_quantity=product_data.inventory.quantity,
            low_stock_threshold=product_data.inventory.low_stock_threshold,
            track_inventory=product_data.inventory.track_inventory,
            status=initial_status,
            created_at=now,
            updated_at=now
        )
        
        try:
            self.db.add(db_product)
            self.db.commit()
            self.db.refresh(db_product)
            return self._db_to_pydantic(db_product)
        except Exception:
            self.db.rollback()
            raise
    
    async def get_product_by_id(self, product_id: str) -> Optional[Product]:
        """Get product by ID."""
        db_product = self.db.query(ProductDB).filter(ProductDB.id == product_id).first()
        if db_product:
            return self._db_to_pydantic(db_product)
        return None
    
    async def update_product(self, product_id: str, updates: ProductUpdates) -> Product:
        """Update product."""
        db_product = self.db.query(ProductDB).filter(ProductDB.id == product_id).first()
        if not db_product:
            raise ValueError(f"Product with ID {product_id} not found")
        
        # Update fields if provided
        if updates.name is not None:
            db_product.name = updates.name
        if updates.description is not None:
            db_product.description = updates.description
        if updates.price is not None:
            db_product.price = updates.price
        if updates.category is not None:
            db_product.category = updates.category
        if updates.images is not None:
            db_product.images = updates.images
        if updates.inventory is not None:
            db_product.inventory_quantity = updates.inventory.quantity
            db_product.low_stock_threshold = updates.inventory.low_stock_threshold
            db_product.track_inventory = updates.inventory.track_inventory
            
            # Update status based on inventory
            if updates.inventory.track_inventory and updates.inventory.quantity == 0:
                db_product.status = ProductStatus.OUT_OF_STOCK
            elif db_product.status == ProductStatus.OUT_OF_STOCK and updates.inventory.quantity > 0:
                db_product.status = ProductStatus.ACTIVE
        
        db_product.updated_at = datetime.utcnow()
        
        try:
            self.db.commit()
            self.db.refresh(db_product)
            return self._db_to_pydantic(db_product)
        except Exception:
            self.db.rollback()
            raise
    
    async def delete_product(self, product_id: str) -> None:
        """Delete product."""
        db_product = self.db.query(ProductDB).filter(ProductDB.id == product_id).first()
        if db_product:
            self.db.delete(db_product)
            self.db.commit()
    
    async def search_products(self, query: SearchQuery) -> SearchResults:
        """Search products."""
        db_query = self.db.query(ProductDB).filter(ProductDB.status == ProductStatus.ACTIVE)
        
        # Apply search term filter
        if query.search_term:
            search_filter = or_(
                ProductDB.name.ilike(f"%{query.search_term}%"),
                ProductDB.description.ilike(f"%{query.search_term}%"),
                ProductDB.category.ilike(f"%{query.search_term}%")
            )
            db_query = db_query.filter(search_filter)
        
        # Apply category filter
        if query.category:
            db_query = db_query.filter(ProductDB.category == query.category)
        
        # Apply price range filter
        if query.min_price is not None:
            db_query = db_query.filter(ProductDB.price >= query.min_price)
        if query.max_price is not None:
            db_query = db_query.filter(ProductDB.price <= query.max_price)
        
        # Apply seller filter
        if query.seller_id:
            db_query = db_query.filter(ProductDB.seller_id == query.seller_id)
        
        # Get total count before pagination
        total_count = db_query.count()
        
        # Apply sorting
        if query.sort_by == "price_asc":
            db_query = db_query.order_by(asc(ProductDB.price))
        elif query.sort_by == "price_desc":
            db_query = db_query.order_by(desc(ProductDB.price))
        elif query.sort_by == "name":
            db_query = db_query.order_by(asc(ProductDB.name))
        elif query.sort_by == "newest":
            db_query = db_query.order_by(desc(ProductDB.created_at))
        else:  # Default to relevance (newest first)
            db_query = db_query.order_by(desc(ProductDB.created_at))
        
        # Apply pagination
        offset = (query.page - 1) * query.page_size
        db_products = db_query.offset(offset).limit(query.page_size).all()
        
        # Convert to Pydantic models
        products = [self._db_to_pydantic(db_product) for db_product in db_products]
        
        return SearchResults(
            products=products,
            total_count=total_count,
            page=query.page,
            page_size=query.page_size,
            total_pages=(total_count + query.page_size - 1) // query.page_size
        )
    
    async def get_products_by_seller(self, seller_id: str) -> List[Product]:
        """Get products by seller."""
        db_products = self.db.query(ProductDB).filter(ProductDB.seller_id == seller_id).all()
        return [self._db_to_pydantic(db_product) for db_product in db_products]
    
    async def update_inventory(self, product_id: str, quantity: int) -> Product:
        """Update product inventory."""
        db_product = self.db.query(ProductDB).filter(ProductDB.id == product_id).first()
        if not db_product:
            raise ValueError(f"Product with ID {product_id} not found")
        
        db_product.inventory_quantity = quantity
        
        # Update status based on inventory
        if db_product.track_inventory:
            if quantity == 0:
                db_product.status = ProductStatus.OUT_OF_STOCK
            elif db_product.status == ProductStatus.OUT_OF_STOCK and quantity > 0:
                db_product.status = ProductStatus.ACTIVE
        
        db_product.updated_at = datetime.utcnow()
        
        try:
            self.db.commit()
            self.db.refresh(db_product)
            return self._db_to_pydantic(db_product)
        except Exception:
            self.db.rollback()
            raise
    
    async def get_low_stock_products(self, seller_id: str) -> List[Product]:
        """Get products with low stock."""
        db_products = self.db.query(ProductDB).filter(
            and_(
                ProductDB.seller_id == seller_id,
                ProductDB.track_inventory == True,
                ProductDB.inventory_quantity <= ProductDB.low_stock_threshold,
                ProductDB.inventory_quantity > 0
            )
        ).all()
        
        return [self._db_to_pydantic(db_product) for db_product in db_products]


class InMemoryProductRepository(ProductRepository):
    """In-memory implementation of product repository for testing."""
    
    def __init__(self):
        """Initialize repository."""
        self._products: dict[str, Product] = {}
    
    async def create_product(self, product_data: ProductCreationData) -> Product:
        """Create a new product."""
        # This would delegate to the service in a real implementation
        # For now, this is a placeholder
        raise NotImplementedError("Use ProductService directly")
    
    async def get_product_by_id(self, product_id: str) -> Optional[Product]:
        """Get product by ID."""
        return self._products.get(product_id)
    
    async def update_product(self, product_id: str, updates: ProductUpdates) -> Product:
        """Update product."""
        raise NotImplementedError("Use ProductService directly")
    
    async def delete_product(self, product_id: str) -> None:
        """Delete product."""
        if product_id in self._products:
            del self._products[product_id]
    
    async def search_products(self, query: SearchQuery) -> SearchResults:
        """Search products."""
        raise NotImplementedError("Use ProductService directly")
    
    async def get_products_by_seller(self, seller_id: str) -> List[Product]:
        """Get products by seller."""
        return [product for product in self._products.values() 
                if product.seller_id == seller_id]
    
    async def update_inventory(self, product_id: str, quantity: int) -> Product:
        """Update product inventory."""
        raise NotImplementedError("Use ProductService directly")
    
    async def get_low_stock_products(self, seller_id: str) -> List[Product]:
        """Get products with low stock."""
        return [product for product in self._products.values() 
                if product.seller_id == seller_id and product.is_low_stock]