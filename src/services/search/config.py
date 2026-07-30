"""Search service configuration."""

from pydantic import BaseModel


class SearchConfig(BaseModel):
    """Configuration for search service."""
    max_results_per_page: int = 50
    default_page_size: int = 20
    max_search_term_length: int = 200
    enable_fuzzy_search: bool = True
    relevance_boost_name: float = 2.0
    relevance_boost_description: float = 1.0
    category_hierarchy_separator: str = "/"


# Global search configuration instance
search_config = SearchConfig()