"""Product endpoints."""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
from pydantic import BaseModel
from decimal import Decimal

from ...services.products.service import ProductService, ProductCreationData, ProductUpdates, SearchQuery, Product, SearchResults
from ...shared.models import BaseResponse
from ..dependencies import get_current_user, get_current_user_optional

router = APIRouter(tags=["products"])

# Initialize product service
product_service = ProductService()


class ProductCreateRequest(BaseModel):
    """Product creation request model."""
    name: str
    description: str
    price: Decimal
    currency: str = "USD"
    category: str
    inventory_quantity: int
    low_stock_threshold: int = 5
    images: List[str] = []


class ProductUpdateRequest(BaseModel):
    """Product update request model."""
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    category: Optional[str] = None
    inventory_quantity: Optional[int] = None
    low_stock_threshold: Optional[int] = None
    images: Optional[List[str]] = None


class ProductResponse(BaseModel):
    """Product response model."""
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
    status: str
    created_at: str
    updated_at: str


class SearchResponse(BaseModel):
    """Search response model."""
    products: List[ProductResponse]
    total_count: int
    page: int
    page_size: int


@router.get("/", response_model=SearchResponse)
async def list_products(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page")
):
    """List all products with pagination."""
    try:
        query = SearchQuery(
            term=None,
            category=None,
            min_price=None,
            max_price=None,
            in_stock_only=True,
            page=page,
            page_size=page_size
        )
        
        results = await product_service.search_products(query)
        
        products = [
            ProductResponse(
                id=product.id,
                seller_id=product.seller_id,
                name=product.name,
                description=product.description,
                price=product.price,
                currency=product.currency,
                category=product.category,
                images=product.images,
                inventory_quantity=product.inventory_quantity,
                low_stock_threshold=product.low_stock_threshold,
                status=product.status,
                created_at=product.created_at.isoformat(),
                updated_at=product.updated_at.isoformat()
            )
            for product in results.products
        ]
        
        return SearchResponse(
            products=products,
            total_count=results.total_count,
            page=results.page,
            page_size=results.page_size
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/", response_model=ProductResponse)
async def create_product(
    request: ProductCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a new product (sellers only)."""
    if current_user["role"] != "seller":
        raise HTTPException(status_code=403, detail="Only sellers can create products")
    
    try:
        product_data = ProductCreationData(
            seller_id=current_user["sub"],
            name=request.name,
            description=request.description,
            price=request.price,
            currency=request.currency,
            category=request.category,
            inventory_quantity=request.inventory_quantity,
            low_stock_threshold=request.low_stock_threshold,
            images=request.images
        )
        
        product = await product_service.create_product(product_data)
        
        return ProductResponse(
            id=product.id,
            seller_id=product.seller_id,
            name=product.name,
            description=product.description,
            price=product.price,
            currency=product.currency,
            category=product.category,
            images=product.images,
            inventory_quantity=product.inventory_quantity,
            low_stock_threshold=product.low_stock_threshold,
            status=product.status,
            created_at=product.created_at.isoformat(),
            updated_at=product.updated_at.isoformat()
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/search", response_model=SearchResponse)
async def search_products(
    term: Optional[str] = Query(None, description="Search term"),
    category: Optional[str] = Query(None, description="Product category"),
    min_price: Optional[Decimal] = Query(None, description="Minimum price"),
    max_price: Optional[Decimal] = Query(None, description="Maximum price"),
    in_stock_only: bool = Query(True, description="Show only in-stock products"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page")
):
    """Search products with filters."""
    try:
        query = SearchQuery(
            term=term,
            category=category,
            min_price=min_price,
            max_price=max_price,
            in_stock_only=in_stock_only,
            page=page,
            page_size=page_size
        )
        
        results = await product_service.search_products(query)
        
        products = [
            ProductResponse(
                id=product.id,
                seller_id=product.seller_id,
                name=product.name,
                description=product.description,
                price=product.price,
                currency=product.currency,
                category=product.category,
                images=product.images,
                inventory_quantity=product.inventory_quantity,
                low_stock_threshold=product.low_stock_threshold,
                status=product.status,
                created_at=product.created_at.isoformat(),
                updated_at=product.updated_at.isoformat()
            )
            for product in results.products
        ]
        
        return SearchResponse(
            products=products,
            total_count=results.total_count,
            page=results.page,
            page_size=results.page_size
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str):
    """Get product by ID."""
    product = await product_service.get_product_by_id(product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return ProductResponse(
        id=product.id,
        seller_id=product.seller_id,
        name=product.name,
        description=product.description,
        price=product.price,
        currency=product.currency,
        category=product.category,
        images=product.images,
        inventory_quantity=product.inventory_quantity,
        low_stock_threshold=product.low_stock_threshold,
        status=product.status,
        created_at=product.created_at.isoformat(),
        updated_at=product.updated_at.isoformat()
    )


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    request: ProductUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update product (seller only, own products)."""
    if current_user["role"] != "seller":
        raise HTTPException(status_code=403, detail="Only sellers can update products")
    
    # Check if product exists and belongs to seller
    existing_product = await product_service.get_product_by_id(product_id)
    if not existing_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if existing_product.seller_id != current_user["sub"]:
        raise HTTPException(status_code=403, detail="You can only update your own products")
    
    try:
        updates = ProductUpdates(
            name=request.name,
            description=request.description,
            price=request.price,
            category=request.category,
            inventory_quantity=request.inventory_quantity,
            low_stock_threshold=request.low_stock_threshold,
            images=request.images
        )
        
        product = await product_service.update_product(product_id, updates)
        
        return ProductResponse(
            id=product.id,
            seller_id=product.seller_id,
            name=product.name,
            description=product.description,
            price=product.price,
            currency=product.currency,
            category=product.category,
            images=product.images,
            inventory_quantity=product.inventory_quantity,
            low_stock_threshold=product.low_stock_threshold,
            status=product.status,
            created_at=product.created_at.isoformat(),
            updated_at=product.updated_at.isoformat()
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{product_id}", response_model=BaseResponse)
async def delete_product(
    product_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete product (seller only, own products)."""
    if current_user["role"] != "seller":
        raise HTTPException(status_code=403, detail="Only sellers can delete products")
    
    # Check if product exists and belongs to seller
    existing_product = await product_service.get_product_by_id(product_id)
    if not existing_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if existing_product.seller_id != current_user["sub"]:
        raise HTTPException(status_code=403, detail="You can only delete your own products")
    
    try:
        await product_service.delete_product(product_id)
        
        return BaseResponse(
            success=True,
            message="Product deleted successfully"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/seller/{seller_id}", response_model=List[ProductResponse])
async def get_products_by_seller(seller_id: str):
    """Get all products for a specific seller."""
    products = await product_service.get_products_by_seller(seller_id)
    
    return [
        ProductResponse(
            id=product.id,
            seller_id=product.seller_id,
            name=product.name,
            description=product.description,
            price=product.price,
            currency=product.currency,
            category=product.category,
            images=product.images,
            inventory_quantity=product.inventory_quantity,
            low_stock_threshold=product.low_stock_threshold,
            status=product.status,
            created_at=product.created_at.isoformat(),
            updated_at=product.updated_at.isoformat()
        )
        for product in products
    ]


@router.patch("/{product_id}/inventory", response_model=ProductResponse)
async def update_product_inventory(
    product_id: str,
    quantity: int,
    current_user: dict = Depends(get_current_user)
):
    """Update product inventory (seller only, own products)."""
    if current_user["role"] != "seller":
        raise HTTPException(status_code=403, detail="Only sellers can update inventory")
    
    # Check if product exists and belongs to seller
    existing_product = await product_service.get_product_by_id(product_id)
    if not existing_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if existing_product.seller_id != current_user["sub"]:
        raise HTTPException(status_code=403, detail="You can only update your own products")
    
    try:
        product = await product_service.update_inventory(product_id, quantity)
        
        return ProductResponse(
            id=product.id,
            seller_id=product.seller_id,
            name=product.name,
            description=product.description,
            price=product.price,
            currency=product.currency,
            category=product.category,
            images=product.images,
            inventory_quantity=product.inventory_quantity,
            low_stock_threshold=product.low_stock_threshold,
            status=product.status,
            created_at=product.created_at.isoformat(),
            updated_at=product.updated_at.isoformat()
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))