"""Product service module."""

from .service import (
    ProductService,
    Product,
    ProductCreationData,
    ProductUpdates,
    SearchQuery,
    SearchResults,
)
from .repository import ProductRepository
from .config import product_config

__all__ = [
    "ProductService",
    "Product",
    "ProductCreationData",
    "ProductUpdates",
    "SearchQuery",
    "SearchResults",
    "ProductRepository",
    "product_config",
]