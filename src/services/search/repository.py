"""Search service repository for data access."""

from typing import List, Dict, Optional
from datetime import datetime
from ..products.service import Product


class SearchRepository:
    """Repository for search-related data operations."""
    
    def __init__(self):
        """Initialize search repository."""
        # Cache for search analytics and popular terms
        self._search_analytics: Dict[str, int] = {}
        self._popular_categories: Dict[str, int] = {}
        self._last_updated: Optional[datetime] = None
    
    async def record_search_query(self, term: str, result_count: int) -> None:
        """
        Record a search query for analytics.
        
        Args:
            term: Search term used
            result_count: Number of results returned
        """
        if term:
            term_lower = term.lower().strip()
            self._search_analytics[term_lower] = self._search_analytics.get(term_lower, 0) + 1
            self._last_updated = datetime.utcnow()
    
    async def record_category_view(self, category: str) -> None:
        """
        Record a category view for popularity tracking.
        
        Args:
            category: Category that was viewed
        """
        if category:
            self._popular_categories[category] = self._popular_categories.get(category, 0) + 1
            self._last_updated = datetime.utcnow()
    
    async def get_popular_search_terms(self, limit: int = 10) -> List[str]:
        """
        Get most popular search terms.
        
        Args:
            limit: Maximum number of terms to return
            
        Returns:
            List of popular search terms
        """
        sorted_terms = sorted(
            self._search_analytics.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return [term for term, _ in sorted_terms[:limit]]
    
    async def get_popular_categories(self, limit: int = 10) -> List[str]:
        """
        Get most popular categories.
        
        Args:
            limit: Maximum number of categories to return
            
        Returns:
            List of popular categories
        """
        sorted_categories = sorted(
            self._popular_categories.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return [category for category, _ in sorted_categories[:limit]]
    
    async def get_search_suggestions(self, partial_term: str, limit: int = 5) -> List[str]:
        """
        Get search suggestions based on partial term.
        
        Args:
            partial_term: Partial search term
            limit: Maximum number of suggestions
            
        Returns:
            List of suggested search terms
        """
        if not partial_term:
            return []
        
        partial_lower = partial_term.lower()
        suggestions = []
        
        for term in self._search_analytics.keys():
            if term.startswith(partial_lower) and term != partial_lower:
                suggestions.append(term)
        
        # Sort by popularity (search count)
        suggestions.sort(key=lambda t: self._search_analytics.get(t, 0), reverse=True)
        
        return suggestions[:limit]
    
    async def clear_analytics(self) -> None:
        """Clear all search analytics data."""
        self._search_analytics.clear()
        self._popular_categories.clear()
        self._last_updated = None