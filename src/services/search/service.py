"""Advanced search service implementation."""

import re
from typing import Optional, List, Dict, Set
from pydantic import BaseModel, Field, validator
from decimal import Decimal
from datetime import datetime
from ..products.service import Product, ProductService
from .config import search_config
from .repository import SearchRepository


class SearchFilters(BaseModel):
    """Advanced search filters model."""
    category: Optional[str] = None
    subcategory: Optional[str] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    seller_id: Optional[str] = None
    in_stock_only: bool = True
    min_rating: Optional[float] = None
    tags: Optional[List[str]] = None
    
    @validator('min_price', 'max_price')
    def validate_prices(cls, v):
        if v is not None and v < 0:
            raise ValueError('Price cannot be negative')
        return v
    
    @validator('min_rating')
    def validate_rating(cls, v):
        if v is not None and (v < 0 or v > 5):
            raise ValueError('Rating must be between 0 and 5')
        return v


class SortOption(BaseModel):
    """Sort option for search results."""
    field: str = Field(..., pattern=r'^(relevance|price|name|created_at|rating)$')
    direction: str = Field(default="asc", pattern=r'^(asc|desc)$')


class AdvancedSearchQuery(BaseModel):
    """Advanced search query model."""
    term: Optional[str] = Field(None, max_length=search_config.max_search_term_length)
    filters: SearchFilters = Field(default_factory=SearchFilters)
    sort: SortOption = Field(default_factory=lambda: SortOption(field="relevance"))
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=search_config.default_page_size, ge=1, le=search_config.max_results_per_page)
    
    @validator('term')
    def validate_term(cls, v):
        if v is not None:
            # Remove extra whitespace and validate length
            v = ' '.join(v.split())
            if len(v) == 0:
                return None
        return v


class ProductSearchResult(BaseModel):
    """Product search result with relevance score."""
    product: Product
    relevance_score: float = 0.0
    match_highlights: List[str] = Field(default_factory=list)


class CategoryInfo(BaseModel):
    """Category information for navigation."""
    name: str
    full_path: str
    product_count: int
    subcategories: List['CategoryInfo'] = Field(default_factory=list)


class SearchResults(BaseModel):
    """Advanced search results model."""
    results: List[ProductSearchResult]
    total_count: int
    page: int
    page_size: int
    categories: List[CategoryInfo] = Field(default_factory=list)
    suggested_terms: List[str] = Field(default_factory=list)
    applied_filters: SearchFilters
    sort_option: SortOption


class SearchService:
    """Advanced search service for products."""
    
    def __init__(self, product_service: ProductService):
        """Initialize search service with product service dependency."""
        self.product_service = product_service
        self.repository = SearchRepository()
        # Cache for category hierarchy
        self._category_cache: Dict[str, CategoryInfo] = {}
        self._last_cache_update: Optional[datetime] = None
    
    async def search_products(self, query: AdvancedSearchQuery) -> SearchResults:
        """
        Perform advanced product search with filtering, sorting, and relevance scoring.
        
        Args:
            query: Advanced search query with filters and options
            
        Returns:
            Search results with relevance scoring and category information
        """
        # Get all products from product service
        all_products = list(self.product_service._products.values())
        
        # Apply basic filters first
        filtered_products = self._apply_filters(all_products, query.filters)
        
        # Apply text search and calculate relevance scores
        if query.term:
            search_results = self._search_by_term(filtered_products, query.term)
        else:
            search_results = [
                ProductSearchResult(product=product, relevance_score=1.0)
                for product in filtered_products
            ]
        
        # Apply sorting
        sorted_results = self._sort_results(search_results, query.sort)
        
        # Get category information
        categories = await self._get_category_hierarchy(filtered_products)
        
        # Generate suggested terms if no results
        suggested_terms = []
        if not sorted_results and query.term:
            suggested_terms = self._generate_suggested_terms(query.term, all_products)
        
        # Apply pagination
        total_count = len(sorted_results)
        start_idx = (query.page - 1) * query.page_size
        end_idx = start_idx + query.page_size
        paginated_results = sorted_results[start_idx:end_idx]
        
        # Record search analytics
        if query.term:
            await self.repository.record_search_query(query.term, total_count)
        if query.filters.category:
            await self.repository.record_category_view(query.filters.category)
        
        return SearchResults(
            results=paginated_results,
            total_count=total_count,
            page=query.page,
            page_size=query.page_size,
            categories=categories,
            suggested_terms=suggested_terms,
            applied_filters=query.filters,
            sort_option=query.sort
        )
    
    async def get_categories(self) -> List[CategoryInfo]:
        """
        Get hierarchical category structure with product counts.
        
        Returns:
            List of top-level categories with subcategories
        """
        all_products = list(self.product_service._products.values())
        return await self._get_category_hierarchy(all_products)
    
    async def search_by_category(self, category_path: str, page: int = 1, page_size: int = 20) -> SearchResults:
        """
        Search products by category path.
        
        Args:
            category_path: Full category path (e.g., "Electronics/Smartphones")
            page: Page number
            page_size: Results per page
            
        Returns:
            Search results for the category
        """
        query = AdvancedSearchQuery(
            filters=SearchFilters(category=category_path),
            page=page,
            page_size=page_size,
            sort=SortOption(field="name", direction="asc")
        )
        return await self.search_products(query)
    
    def _apply_filters(self, products: List[Product], filters: SearchFilters) -> List[Product]:
        """Apply search filters to product list."""
        filtered = []
        
        for product in products:
            # Stock filter
            if filters.in_stock_only and product.inventory_quantity == 0:
                continue
            
            # Category filter (supports hierarchical matching)
            if filters.category:
                if not self._matches_category(product.category, filters.category):
                    continue
            
            # Subcategory filter
            if filters.subcategory:
                if not self._matches_subcategory(product.category, filters.subcategory):
                    continue
            
            # Price range filters
            if filters.min_price is not None and product.price < filters.min_price:
                continue
            if filters.max_price is not None and product.price > filters.max_price:
                continue
            
            # Seller filter
            if filters.seller_id and product.seller_id != filters.seller_id:
                continue
            
            # Only include active products
            if product.status != "active":
                continue
            
            filtered.append(product)
        
        return filtered
    
    def _search_by_term(self, products: List[Product], term: str) -> List[ProductSearchResult]:
        """Search products by text term with relevance scoring."""
        results = []
        term_lower = term.lower()
        term_words = set(term_lower.split())
        
        for product in products:
            score = 0.0
            highlights = []
            
            # Search in product name (higher weight)
            name_lower = product.name.lower()
            if term_lower in name_lower:
                score += search_config.relevance_boost_name
                highlights.append(f"Name: {product.name}")
            
            # Word matching in name
            name_words = set(name_lower.split())
            name_matches = len(term_words.intersection(name_words))
            if name_matches > 0:
                score += name_matches * (search_config.relevance_boost_name * 0.5)
            
            # Search in description (lower weight)
            desc_lower = product.description.lower()
            if term_lower in desc_lower:
                score += search_config.relevance_boost_description
                # Extract snippet around match
                snippet = self._extract_snippet(product.description, term, 100)
                highlights.append(f"Description: {snippet}")
            
            # Word matching in description
            desc_words = set(desc_lower.split())
            desc_matches = len(term_words.intersection(desc_words))
            if desc_matches > 0:
                score += desc_matches * (search_config.relevance_boost_description * 0.3)
            
            # Search in category
            if term_lower in product.category.lower():
                score += 0.5
                highlights.append(f"Category: {product.category}")
            
            # Only include products with some relevance
            if score > 0:
                results.append(ProductSearchResult(
                    product=product,
                    relevance_score=score,
                    match_highlights=highlights
                ))
        
        return results
    
    def _sort_results(self, results: List[ProductSearchResult], sort_option: SortOption) -> List[ProductSearchResult]:
        """Sort search results based on sort option."""
        reverse = sort_option.direction == "desc"
        
        if sort_option.field == "relevance":
            return sorted(results, key=lambda r: r.relevance_score, reverse=True)
        elif sort_option.field == "price":
            return sorted(results, key=lambda r: r.product.price, reverse=reverse)
        elif sort_option.field == "name":
            return sorted(results, key=lambda r: r.product.name.lower(), reverse=reverse)
        elif sort_option.field == "created_at":
            return sorted(results, key=lambda r: r.product.created_at, reverse=reverse)
        else:
            # Default to relevance
            return sorted(results, key=lambda r: r.relevance_score, reverse=True)
    
    async def _get_category_hierarchy(self, products: List[Product]) -> List[CategoryInfo]:
        """Build hierarchical category structure from products."""
        category_counts: Dict[str, int] = {}
        category_paths: Set[str] = set()
        
        # Count products per category and collect all category paths
        for product in products:
            if product.status == "active":
                category_counts[product.category] = category_counts.get(product.category, 0) + 1
                category_paths.add(product.category)
                
                # Add parent categories for hierarchical structure
                parts = product.category.split(search_config.category_hierarchy_separator)
                for i in range(1, len(parts)):
                    parent_path = search_config.category_hierarchy_separator.join(parts[:i])
                    category_paths.add(parent_path)
        
        # Build hierarchy
        categories: Dict[str, CategoryInfo] = {}
        
        for path in sorted(category_paths):
            parts = path.split(search_config.category_hierarchy_separator)
            name = parts[-1]
            count = category_counts.get(path, 0)
            
            category_info = CategoryInfo(
                name=name,
                full_path=path,
                product_count=count
            )
            categories[path] = category_info
        
        # Link parent-child relationships
        root_categories = []
        for path, category in categories.items():
            parts = path.split(search_config.category_hierarchy_separator)
            if len(parts) == 1:
                # Root category
                root_categories.append(category)
            else:
                # Child category - add to parent
                parent_path = search_config.category_hierarchy_separator.join(parts[:-1])
                if parent_path in categories:
                    categories[parent_path].subcategories.append(category)
        
        return sorted(root_categories, key=lambda c: c.name)
    
    def _matches_category(self, product_category: str, filter_category: str) -> bool:
        """Check if product category matches filter (supports hierarchical matching)."""
        return product_category.lower().startswith(filter_category.lower())
    
    def _matches_subcategory(self, product_category: str, subcategory: str) -> bool:
        """Check if product is in specific subcategory."""
        parts = product_category.split(search_config.category_hierarchy_separator)
        return subcategory.lower() in [part.lower() for part in parts]
    
    def _extract_snippet(self, text: str, term: str, max_length: int) -> str:
        """Extract a snippet around the search term."""
        text_lower = text.lower()
        term_lower = term.lower()
        
        # Find the position of the term
        pos = text_lower.find(term_lower)
        if pos == -1:
            return text[:max_length] + "..." if len(text) > max_length else text
        
        # Calculate snippet boundaries
        start = max(0, pos - max_length // 2)
        end = min(len(text), start + max_length)
        
        # Adjust start if we're at the end
        if end == len(text):
            start = max(0, end - max_length)
        
        snippet = text[start:end]
        
        # Add ellipsis if needed
        if start > 0:
            snippet = "..." + snippet
        if end < len(text):
            snippet = snippet + "..."
        
        return snippet
    
    def _generate_suggested_terms(self, original_term: str, all_products: List[Product]) -> List[str]:
        """Generate suggested search terms when no results found."""
        suggestions = set()
        term_lower = original_term.lower()
        
        # Collect words from product names and categories
        all_words = set()
        for product in all_products:
            if product.status == "active":
                all_words.update(product.name.lower().split())
                all_words.update(product.category.lower().split())
        
        # Find similar words (simple fuzzy matching)
        for word in all_words:
            if len(word) >= 3:  # Only suggest meaningful words
                # Check for partial matches
                if (term_lower in word or word in term_lower or 
                    self._calculate_similarity(term_lower, word) > 0.6):
                    suggestions.add(word.title())
        
        # Limit suggestions
        return sorted(list(suggestions))[:5]
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate simple similarity between two strings."""
        if not str1 or not str2:
            return 0.0
        
        # Simple Jaccard similarity based on character bigrams
        def get_bigrams(s):
            return set(s[i:i+2] for i in range(len(s)-1))
        
        bigrams1 = get_bigrams(str1)
        bigrams2 = get_bigrams(str2)
        
        if not bigrams1 and not bigrams2:
            return 1.0
        if not bigrams1 or not bigrams2:
            return 0.0
        
        intersection = len(bigrams1.intersection(bigrams2))
        union = len(bigrams1.union(bigrams2))
        
        return intersection / union if union > 0 else 0.0
    
    async def get_popular_search_terms(self, limit: int = 10) -> List[str]:
        """
        Get popular search terms for suggestions.
        
        Args:
            limit: Maximum number of terms to return
            
        Returns:
            List of popular search terms
        """
        return await self.repository.get_popular_search_terms(limit)
    
    async def get_search_suggestions(self, partial_term: str, limit: int = 5) -> List[str]:
        """
        Get search suggestions based on partial input.
        
        Args:
            partial_term: Partial search term
            limit: Maximum number of suggestions
            
        Returns:
            List of suggested completions
        """
        return await self.repository.get_search_suggestions(partial_term, limit)
    
    async def get_trending_categories(self, limit: int = 10) -> List[str]:
        """
        Get trending categories based on search activity.
        
        Args:
            limit: Maximum number of categories to return
            
        Returns:
            List of trending categories
        """
        return await self.repository.get_popular_categories(limit)


# Fix forward reference for CategoryInfo
CategoryInfo.model_rebuild()