"""Search service tests."""

import pytest
from hypothesis import given, assume, settings, HealthCheck
from hypothesis.strategies import sampled_from
from decimal import Decimal
from tests.test_config import (
    valid_product_names,
    valid_descriptions,
    valid_prices,
    valid_quantities,
    valid_categories,
    valid_currencies,
    PropertyTestUtils,
)


class TestSearchService:
    """Search service test cases."""
    
    def test_search_service_initialization(self):
        """Test search service can be initialized."""
        from src.services.search.service import SearchService
        from src.services.products.service import ProductService
        
        product_service = ProductService()
        search_service = SearchService(product_service)
        assert search_service is not None
        assert search_service.product_service is product_service
    
    def test_search_models_can_be_imported(self):
        """Test that search models can be imported correctly."""
        from src.services.search.service import (
            AdvancedSearchQuery,
            SearchFilters,
            SortOption,
            SearchResults,
            ProductSearchResult,
            CategoryInfo
        )
        
        # Test that models can be instantiated with valid data
        filters = SearchFilters(
            category="electronics",
            min_price=Decimal("10.00"),
            max_price=Decimal("100.00"),
            in_stock_only=True
        )
        assert filters.category == "electronics"
        assert filters.min_price == Decimal("10.00")
        
        sort_option = SortOption(field="price", direction="asc")
        assert sort_option.field == "price"
        assert sort_option.direction == "asc"
        
        query = AdvancedSearchQuery(
            term="laptop",
            filters=filters,
            sort=sort_option,
            page=1,
            page_size=20
        )
        assert query.term == "laptop"
        assert query.filters.category == "electronics"
    @given(
        term=valid_product_names(),
        category=valid_categories(),
        min_price=valid_prices(),
        max_price=valid_prices()
    )
    @pytest.mark.asyncio
    async def test_property_11_search_by_term(self, term, category, min_price, max_price):
        """
        Property 11: Búsqueda por término
        For any search term, it should return relevant products ordered by relevance.
        **Feature: marketplace-platform, Property 11: Búsqueda por término**
        **Validates: Requirements 3.1**
        """
        from src.services.search.service import SearchService, AdvancedSearchQuery, SearchFilters
        from src.services.products.service import ProductService, ProductCreationData
        
        # Assume valid data
        assume(len(term.strip()) > 0)
        assume(min_price < max_price)
        
        product_service = ProductService()
        search_service = SearchService(product_service)
        
        # Create test products with the search term in different places
        products_data = [
            ProductCreationData(
                seller_id="seller-1",
                name=f"{term} Product 1",  # Term in name
                description="A comprehensive product description for testing",
                price=Decimal("50.00"),
                currency="USD",
                category=category,
                inventory_quantity=10
            ),
            ProductCreationData(
                seller_id="seller-1", 
                name="Product 2",
                description=f"This product contains {term} in description",  # Term in description
                price=Decimal("75.00"),
                currency="USD",
                category=category,
                inventory_quantity=5
            ),
            ProductCreationData(
                seller_id="seller-1",
                name="Unrelated Product",
                description="This product has no relation to the search",
                price=Decimal("100.00"),
                currency="USD",
                category="books",  # Different category
                inventory_quantity=3
            )
        ]
        
        # Create products
        for product_data in products_data:
            await product_service.create_product(product_data)
        
        # Search by term
        query = AdvancedSearchQuery(term=term)
        results = await search_service.search_products(query)
        
        # Verify results are relevant (contain the search term)
        for result in results.results:
            product = result.product
            term_lower = term.lower()
            assert (term_lower in product.name.lower() or 
                   term_lower in product.description.lower() or
                   term_lower in product.category.lower()), \
                   f"Product {product.name} should contain term '{term}'"
        
        # Verify results are ordered by relevance (higher scores first)
        if len(results.results) > 1:
            for i in range(len(results.results) - 1):
                assert results.results[i].relevance_score >= results.results[i + 1].relevance_score, \
                       "Results should be ordered by relevance score (highest first)"
    @given(
        category=valid_categories(),
        min_price=valid_prices(),
        max_price=valid_prices(),
        in_stock_only=sampled_from([True, False])
    )
    @pytest.mark.asyncio
    async def test_property_12_product_filtering(self, category, min_price, max_price, in_stock_only):
        """
        Property 12: Filtrado de productos
        For any combination of applied filters, it should show only products that meet all criteria.
        **Feature: marketplace-platform, Property 12: Filtrado de productos**
        **Validates: Requirements 3.2**
        """
        from src.services.search.service import SearchService, AdvancedSearchQuery, SearchFilters
        from src.services.products.service import ProductService, ProductCreationData
        
        # Assume valid price range
        assume(min_price < max_price)
        
        product_service = ProductService()
        search_service = SearchService(product_service)
        
        # Create products that should match filters
        matching_price = ((min_price + max_price) / 2).quantize(Decimal('0.01'))
        matching_product_data = ProductCreationData(
            seller_id="seller-1",
            name="Matching Product",
            description="Product that matches all filter criteria",
            price=matching_price,  # Price in range, properly rounded
            currency="USD",
            category=category,  # Matching category
            inventory_quantity=10 if in_stock_only else 10  # In stock
        )
        
        # Create products that should NOT match filters
        non_matching_products = [
            ProductCreationData(
                seller_id="seller-1",
                name="Wrong Category Product",
                description="Product with wrong category",
                price=matching_price,
                currency="USD",
                category="books" if category != "books" else "electronics",  # Different category
                inventory_quantity=10
            ),
            ProductCreationData(
                seller_id="seller-1",
                name="Too Expensive Product",
                description="Product that exceeds max price",
                price=(max_price + Decimal("10.00")).quantize(Decimal('0.01')),  # Price too high
                currency="USD",
                category=category,
                inventory_quantity=10
            ),
            ProductCreationData(
                seller_id="seller-1",
                name="Too Cheap Product", 
                description="Product below min price",
                price=max(Decimal("0.01"), (min_price - Decimal("1.00")).quantize(Decimal('0.01'))),  # Price too low
                currency="USD",
                category=category,
                inventory_quantity=10
            )
        ]
        
        # Add out of stock product if testing stock filter
        if in_stock_only:
            non_matching_products.append(ProductCreationData(
                seller_id="seller-1",
                name="Out of Stock Product",
                description="Product without inventory",
                price=matching_price,
                currency="USD",
                category=category,
                inventory_quantity=0  # Out of stock
            ))
        
        # Create all products
        await product_service.create_product(matching_product_data)
        for product_data in non_matching_products:
            await product_service.create_product(product_data)
        
        # Apply filters
        filters = SearchFilters(
            category=category,
            min_price=min_price,
            max_price=max_price,
            in_stock_only=in_stock_only
        )
        query = AdvancedSearchQuery(filters=filters)
        results = await search_service.search_products(query)
        
        # Verify all results meet filter criteria
        for result in results.results:
            product = result.product
            
            # Check category filter
            assert product.category.lower() == category.lower(), \
                   f"Product category '{product.category}' should match filter '{category}'"
            
            # Check price range filter
            assert min_price <= product.price <= max_price, \
                   f"Product price {product.price} should be between {min_price} and {max_price}"
            
            # Check stock filter
            if in_stock_only:
                assert product.inventory_quantity > 0, \
                       f"Product should be in stock when in_stock_only=True"
            
            # Check product is active
            assert product.status == "active", \
                   f"Only active products should be returned"
        
        # Verify at least the matching product is found
        matching_found = any(
            result.product.name == "Matching Product" 
            for result in results.results
        )
        assert matching_found, "The product that matches all criteria should be found"
    @given(
        name=valid_product_names(),
        description=valid_descriptions(),
        price=valid_prices(),
        category=valid_categories()
    )
    @pytest.mark.asyncio
    async def test_property_14_basic_info_in_results(self, name, description, price, category):
        """
        Property 14: Información básica en resultados
        For any search result, it should show basic product information.
        **Feature: marketplace-platform, Property 14: Información básica en resultados**
        **Validates: Requirements 3.4**
        """
        from src.services.search.service import SearchService, AdvancedSearchQuery
        from src.services.products.service import ProductService, ProductCreationData
        
        # Assume valid data
        assume(len(name.strip()) > 0)
        assume(len(description.strip()) >= 10)
        assume(price > 0)
        
        product_service = ProductService()
        search_service = SearchService(product_service)
        
        # Create a test product
        product_data = ProductCreationData(
            seller_id="seller-123",
            name=name,
            description=description,
            price=price,
            currency="USD",
            category=category,
            inventory_quantity=5
        )
        
        created_product = await product_service.create_product(product_data)
        
        # Search for products (should return our created product)
        query = AdvancedSearchQuery()
        results = await search_service.search_products(query)
        
        # Find our product in results
        our_result = None
        for result in results.results:
            if result.product.id == created_product.id:
                our_result = result
                break
        
        assert our_result is not None, "Created product should be found in search results"
        
        # Verify basic information is present in the result
        product = our_result.product
        
        # Check that all essential product information is available
        assert product.id is not None and len(product.id) > 0, \
               "Product ID should be present and non-empty"
        
        assert product.name is not None and len(product.name.strip()) > 0, \
               "Product name should be present and non-empty"
        
        assert product.description is not None and len(product.description.strip()) > 0, \
               "Product description should be present and non-empty"
        
        assert product.price is not None and product.price > 0, \
               "Product price should be present and positive"
        
        assert product.currency is not None and len(product.currency) > 0, \
               "Product currency should be present and non-empty"
        
        assert product.category is not None and len(product.category.strip()) > 0, \
               "Product category should be present and non-empty"
        
        assert product.inventory_quantity is not None and product.inventory_quantity >= 0, \
               "Product inventory quantity should be present and non-negative"
        
        assert product.status is not None and len(product.status) > 0, \
               "Product status should be present and non-empty"
        
        assert product.seller_id is not None and len(product.seller_id) > 0, \
               "Product seller ID should be present and non-empty"
        
        assert product.created_at is not None, \
               "Product creation date should be present"
        
        assert product.updated_at is not None, \
               "Product update date should be present"
        
        # Verify the values match what we created
        assert product.name == name, "Product name should match created product"
        assert product.description == description, "Product description should match created product"
        assert product.price == price, "Product price should match created product"
        assert product.category == category, "Product category should match created product"
        assert product.seller_id == "seller-123", "Product seller ID should match created product"


class TestSearchServiceUnitTests:
    """Unit tests for SearchService functionality."""
    
    @pytest.mark.asyncio
    async def test_search_with_empty_term_returns_all_products(self):
        """Test searching with empty term returns all active products."""
        from src.services.search.service import SearchService, AdvancedSearchQuery
        from src.services.products.service import ProductService, ProductCreationData
        from decimal import Decimal
        
        product_service = ProductService()
        search_service = SearchService(product_service)
        
        # Create test products
        products_data = [
            ProductCreationData(
                seller_id="seller-1",
                name="Product 1",
                description="First test product",
                price=Decimal("10.00"),
                currency="USD",
                category="electronics",
                inventory_quantity=5
            ),
            ProductCreationData(
                seller_id="seller-1",
                name="Product 2", 
                description="Second test product",
                price=Decimal("20.00"),
                currency="USD",
                category="books",
                inventory_quantity=3
            )
        ]
        
        for product_data in products_data:
            await product_service.create_product(product_data)
        
        # Search with empty term
        query = AdvancedSearchQuery(term="")
        results = await search_service.search_products(query)
        
        assert results.total_count == 2
        assert len(results.results) == 2
    
    @pytest.mark.asyncio
    async def test_search_by_category_hierarchy(self):
        """Test searching by category supports hierarchical matching."""
        from src.services.search.service import SearchService, AdvancedSearchQuery, SearchFilters
        from src.services.products.service import ProductService, ProductCreationData
        from decimal import Decimal
        
        product_service = ProductService()
        search_service = SearchService(product_service)
        
        # Create products with hierarchical categories
        products_data = [
            ProductCreationData(
                seller_id="seller-1",
                name="Laptop",
                description="Gaming laptop",
                price=Decimal("1000.00"),
                currency="USD",
                category="Electronics/Computers/Laptops",
                inventory_quantity=2
            ),
            ProductCreationData(
                seller_id="seller-1",
                name="Smartphone",
                description="Latest smartphone",
                price=Decimal("800.00"),
                currency="USD",
                category="Electronics/Mobile/Smartphones",
                inventory_quantity=5
            ),
            ProductCreationData(
                seller_id="seller-1",
                name="Book",
                description="Programming book",
                price=Decimal("50.00"),
                currency="USD",
                category="Books/Technology",
                inventory_quantity=10
            )
        ]
        
        for product_data in products_data:
            await product_service.create_product(product_data)
        
        # Search by top-level category "Electronics"
        filters = SearchFilters(category="Electronics")
        query = AdvancedSearchQuery(filters=filters)
        results = await search_service.search_products(query)
        
        assert results.total_count == 2
        assert all("Electronics" in result.product.category for result in results.results)
    
    @pytest.mark.asyncio
    async def test_search_relevance_scoring(self):
        """Test that search results are properly scored by relevance."""
        from src.services.search.service import SearchService, AdvancedSearchQuery
        from src.services.products.service import ProductService, ProductCreationData
        from decimal import Decimal
        
        product_service = ProductService()
        search_service = SearchService(product_service)
        
        # Create products with different relevance to search term "laptop"
        products_data = [
            ProductCreationData(
                seller_id="seller-1",
                name="Gaming Laptop",  # Term in name - should have highest score
                description="High performance computer",
                price=Decimal("1200.00"),
                currency="USD",
                category="electronics",
                inventory_quantity=3
            ),
            ProductCreationData(
                seller_id="seller-1",
                name="Computer",
                description="This is a laptop computer for work",  # Term in description - lower score
                price=Decimal("800.00"),
                currency="USD",
                category="electronics",
                inventory_quantity=5
            ),
            ProductCreationData(
                seller_id="seller-1",
                name="Tablet",
                description="Portable device for reading",  # No term - should not appear
                price=Decimal("400.00"),
                currency="USD",
                category="electronics",
                inventory_quantity=8
            )
        ]
        
        for product_data in products_data:
            await product_service.create_product(product_data)
        
        # Search for "laptop"
        query = AdvancedSearchQuery(term="laptop")
        results = await search_service.search_products(query)
        
        # Should find 2 products (Gaming Laptop and Computer)
        assert results.total_count == 2
        
        # Gaming Laptop should have higher relevance score (term in name)
        assert results.results[0].product.name == "Gaming Laptop"
        assert results.results[0].relevance_score > results.results[1].relevance_score
        
        # Computer should have lower score (term only in description)
        assert results.results[1].product.name == "Computer"
    
    @pytest.mark.asyncio
    async def test_search_pagination(self):
        """Test search results pagination."""
        from src.services.search.service import SearchService, AdvancedSearchQuery
        from src.services.products.service import ProductService, ProductCreationData
        from decimal import Decimal
        
        product_service = ProductService()
        search_service = SearchService(product_service)
        
        # Create 5 test products
        for i in range(5):
            product_data = ProductCreationData(
                seller_id="seller-1",
                name=f"Product {i+1}",
                description=f"Test product number {i+1}",
                price=Decimal(f"{10 + i}.00"),
                currency="USD",
                category="test",
                inventory_quantity=10
            )
            await product_service.create_product(product_data)
        
        # Test first page with page_size=2
        query = AdvancedSearchQuery(page=1, page_size=2)
        results = await search_service.search_products(query)
        
        assert results.total_count == 5
        assert len(results.results) == 2
        assert results.page == 1
        assert results.page_size == 2
        
        # Test second page
        query = AdvancedSearchQuery(page=2, page_size=2)
        results = await search_service.search_products(query)
        
        assert results.total_count == 5
        assert len(results.results) == 2
        assert results.page == 2
        
        # Test last page (partial)
        query = AdvancedSearchQuery(page=3, page_size=2)
        results = await search_service.search_products(query)
        
        assert results.total_count == 5
        assert len(results.results) == 1
        assert results.page == 3
    
    @pytest.mark.asyncio
    async def test_get_categories_hierarchy(self):
        """Test getting category hierarchy."""
        from src.services.search.service import SearchService
        from src.services.products.service import ProductService, ProductCreationData
        from decimal import Decimal
        
        product_service = ProductService()
        search_service = SearchService(product_service)
        
        # Create products with hierarchical categories
        products_data = [
            ProductCreationData(
                seller_id="seller-1",
                name="Laptop",
                description="Gaming laptop",
                price=Decimal("1000.00"),
                currency="USD",
                category="Electronics",
                inventory_quantity=2
            ),
            ProductCreationData(
                seller_id="seller-1",
                name="Phone",
                description="Smartphone",
                price=Decimal("600.00"),
                currency="USD",
                category="Electronics",
                inventory_quantity=5
            ),
            ProductCreationData(
                seller_id="seller-1",
                name="Book",
                description="Programming book",
                price=Decimal("50.00"),
                currency="USD",
                category="Books",
                inventory_quantity=10
            )
        ]
        
        for product_data in products_data:
            await product_service.create_product(product_data)
        
        # Get categories
        categories = await search_service.get_categories()
        
        assert len(categories) >= 2  # At least Electronics and Books
        
        # Find Electronics category
        electronics_category = next(
            (cat for cat in categories if cat.name == "Electronics"), 
            None
        )
        assert electronics_category is not None
        assert electronics_category.product_count == 2
        
        # Find Books category
        books_category = next(
            (cat for cat in categories if cat.name == "Books"),
            None
        )
        assert books_category is not None
        assert books_category.product_count == 1
    
    @pytest.mark.asyncio
    async def test_search_by_category_method(self):
        """Test search_by_category convenience method."""
        from src.services.search.service import SearchService
        from src.services.products.service import ProductService, ProductCreationData
        from decimal import Decimal
        
        product_service = ProductService()
        search_service = SearchService(product_service)
        
        # Create products in different categories
        products_data = [
            ProductCreationData(
                seller_id="seller-1",
                name="Laptop",
                description="Gaming laptop",
                price=Decimal("1000.00"),
                currency="USD",
                category="Electronics",
                inventory_quantity=2
            ),
            ProductCreationData(
                seller_id="seller-1",
                name="Book",
                description="Programming book",
                price=Decimal("50.00"),
                currency="USD",
                category="Books",
                inventory_quantity=10
            )
        ]
        
        for product_data in products_data:
            await product_service.create_product(product_data)
        
        # Search by Electronics category
        results = await search_service.search_by_category("Electronics")
        
        assert results.total_count == 1
        assert results.results[0].product.category == "Electronics"
        assert results.results[0].product.name == "Laptop"
    
    def test_search_filters_validation(self):
        """Test SearchFilters validation."""
        from src.services.search.service import SearchFilters
        from decimal import Decimal
        import pytest
        from pydantic import ValidationError
        
        # Test valid filters
        filters = SearchFilters(
            category="electronics",
            min_price=Decimal("10.00"),
            max_price=Decimal("100.00"),
            in_stock_only=True
        )
        assert filters.category == "electronics"
        assert filters.min_price == Decimal("10.00")
        
        # Test negative price validation
        with pytest.raises(ValidationError):
            SearchFilters(min_price=Decimal("-10.00"))
        
        with pytest.raises(ValidationError):
            SearchFilters(max_price=Decimal("-5.00"))
        
        # Test invalid rating
        with pytest.raises(ValidationError):
            SearchFilters(min_rating=6.0)  # Rating should be <= 5
        
        with pytest.raises(ValidationError):
            SearchFilters(min_rating=-1.0)  # Rating should be >= 0
    
    def test_sort_option_validation(self):
        """Test SortOption validation."""
        from src.services.search.service import SortOption
        import pytest
        from pydantic import ValidationError
        
        # Test valid sort options
        sort = SortOption(field="price", direction="asc")
        assert sort.field == "price"
        assert sort.direction == "asc"
        
        sort = SortOption(field="relevance", direction="desc")
        assert sort.field == "relevance"
        assert sort.direction == "desc"
        
        # Test invalid field
        with pytest.raises(ValidationError):
            SortOption(field="invalid_field")
        
        # Test invalid direction
        with pytest.raises(ValidationError):
            SortOption(field="price", direction="invalid_direction")
    
    def test_advanced_search_query_validation(self):
        """Test AdvancedSearchQuery validation."""
        from src.services.search.service import AdvancedSearchQuery, SearchFilters, SortOption
        from decimal import Decimal
        import pytest
        from pydantic import ValidationError
        
        # Test valid query
        query = AdvancedSearchQuery(
            term="laptop",
            filters=SearchFilters(category="electronics"),
            sort=SortOption(field="price", direction="asc"),
            page=1,
            page_size=20
        )
        assert query.term == "laptop"
        assert query.page == 1
        
        # Test term length validation (should be trimmed)
        long_term = "a" * 300  # Exceeds max length
        with pytest.raises(ValidationError):
            AdvancedSearchQuery(term=long_term)
        
        # Test page validation
        with pytest.raises(ValidationError):
            AdvancedSearchQuery(page=0)  # Page should be >= 1
        
        # Test page_size validation
        with pytest.raises(ValidationError):
            AdvancedSearchQuery(page_size=0)  # Should be >= 1
        
        with pytest.raises(ValidationError):
            AdvancedSearchQuery(page_size=200)  # Should be <= max_results_per_page