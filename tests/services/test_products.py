"""Product service tests."""

import pytest
from hypothesis import given, assume, settings, HealthCheck
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


class TestProductService:
    """Product service test cases."""
    
    def test_product_service_initialization(self):
        """Test product service can be initialized."""
        from src.services.products.service import ProductService
        service = ProductService()
        assert service is not None
    
    def test_product_models_can_be_imported(self):
        """Test that product models can be imported correctly."""
        from src.services.products.service import (
            Product,
            ProductCreationData,
            ProductUpdates,
            SearchQuery,
            SearchResults,
        )
        
        # Test that models can be instantiated with valid data
        creation_data = ProductCreationData(
            seller_id="test-seller-123",
            name="Test Product",
            description="A comprehensive test product description",
            price=Decimal("99.99"),
            currency="USD",
            category="electronics",
            inventory_quantity=10
        )
        assert creation_data.name == "Test Product"
        assert creation_data.price == Decimal("99.99")
    
    @given(
        name=valid_product_names(),
        description=valid_descriptions(),
        price=valid_prices(),
        currency=valid_currencies(),
        category=valid_categories(),
        quantity=valid_quantities()
    )
    @pytest.mark.asyncio
    async def test_property_6_product_creation(self, name, description, price, currency, category, quantity):
        """
        Property 6: Creación de productos
        For any product with complete information, it should be saved and made visible in the catalog.
        **Feature: marketplace-platform, Property 6: Creación de productos**
        **Validates: Requirements 2.1**
        """
        from src.services.products.service import ProductService, ProductCreationData
        
        # Assume valid data (filter out edge cases that might cause issues)
        assume(len(name.strip()) > 0)
        assume(len(description.strip()) >= 10)
        assume(price > 0)
        
        service = ProductService()
        seller_id = "test-seller-123"
        
        # Create product data
        product_data = ProductCreationData(
            seller_id=seller_id,
            name=name,
            description=description,
            price=price,
            currency=currency,
            category=category,
            inventory_quantity=quantity
        )
        
        # Create product
        product = await service.create_product(product_data)
        
        # Verify product was created with correct data
        assert product.id is not None
        assert product.seller_id == seller_id
        assert product.name == name
        assert product.description == description
        assert product.price == price
        assert product.currency == currency
        assert product.category == category
        assert product.inventory_quantity == quantity
        
        # Verify product is visible in catalog (can be retrieved)
        retrieved_product = await service.get_product_by_id(product.id)
        assert retrieved_product is not None
        assert retrieved_product.id == product.id
    
    @given(
        name=valid_product_names(),
        description=valid_descriptions(),
        price=valid_prices(),
        category=valid_categories(),
        quantity=valid_quantities()
    )
    @pytest.mark.asyncio
    async def test_property_7_product_updates(self, name, description, price, category, quantity):
        """
        Property 7: Actualización de productos
        For any valid product update, changes should be reflected immediately.
        **Feature: marketplace-platform, Property 7: Actualización de productos**
        **Validates: Requirements 2.2**
        """
        from src.services.products.service import ProductService, ProductCreationData, ProductUpdates
        
        # Assume valid data
        assume(len(name.strip()) > 0)
        assume(len(description.strip()) >= 10)
        assume(price > 0)
        
        service = ProductService()
        
        # Create initial product
        initial_data = ProductCreationData(
            seller_id="test-seller-123",
            name="Initial Product",
            description="Initial description for testing updates",
            price=Decimal("50.00"),
            currency="USD",
            category="electronics",
            inventory_quantity=5
        )
        
        import asyncio
        product = await service.create_product(initial_data)
        
        # Update product
        updates = ProductUpdates(
            name=name,
            description=description,
            price=price,
            category=category,
            inventory_quantity=quantity
        )
        
        updated_product = await service.update_product(product.id, updates)
        
        # Verify changes are reflected immediately
        assert updated_product.name == name
        assert updated_product.description == description
        assert updated_product.price == price
        assert updated_product.category == category
        assert updated_product.inventory_quantity == quantity
        
        # Verify changes persist when retrieving product
        retrieved_product = await service.get_product_by_id(product.id)
        assert retrieved_product.name == name
        assert retrieved_product.description == description
        assert retrieved_product.price == price
        assert retrieved_product.category == category
        assert retrieved_product.inventory_quantity == quantity
    
    @pytest.mark.asyncio
    async def test_property_10_zero_inventory_marks_unavailable(self):
        """
        Property 10: Inventario cero marca no disponible
        For any product whose inventory reaches zero, it should be marked as unavailable.
        **Feature: marketplace-platform, Property 10: Inventario cero marca no disponible**
        **Validates: Requirements 2.5**
        """
        from src.services.products.service import ProductService, ProductCreationData
        
        service = ProductService()
        
        # Test 1: Product created with zero inventory should be marked as out_of_stock
        zero_inventory_data = ProductCreationData(
            seller_id="test-seller-123",
            name="Zero Inventory Product",
            description="Product created with zero inventory for testing",
            price=Decimal("99.99"),
            currency="USD",
            category="electronics",
            inventory_quantity=0
        )
        
        zero_product = await service.create_product(zero_inventory_data)
        assert zero_product.status == "out_of_stock"
        assert not zero_product.is_available
        
        # Test 2: Product with positive inventory should be active
        positive_inventory_data = ProductCreationData(
            seller_id="test-seller-123",
            name="Positive Inventory Product",
            description="Product created with positive inventory for testing",
            price=Decimal("99.99"),
            currency="USD",
            category="electronics",
            inventory_quantity=10
        )
        
        positive_product = await service.create_product(positive_inventory_data)
        assert positive_product.status == "active"
        assert positive_product.is_available
        
        # Test 3: Updating inventory to zero should mark as out_of_stock
        updated_product = await service.update_inventory(positive_product.id, 0)
        assert updated_product.status == "out_of_stock"
        assert not updated_product.is_available
        
        # Test 4: Updating inventory from zero to positive should mark as active
        restored_product = await service.update_inventory(zero_product.id, 5)
        assert restored_product.status == "active"
        assert restored_product.is_available
    
    def test_product_repository_interface(self):
        """Test product repository interface can be imported."""
        from src.services.products.repository import ProductRepository
        assert ProductRepository is not None
    
    def test_product_config_can_be_imported(self):
        """Test product configuration can be imported."""
        from src.services.products.config import product_config
        assert product_config is not None
        assert hasattr(product_config, 'max_product_images')
        assert hasattr(product_config, 'search_results_per_page')


class TestProductServiceUnitTests:
    """Unit tests for ProductService CRUD operations and validations."""
    
    @pytest.mark.asyncio
    async def test_create_product_with_valid_data(self):
        """Test creating a product with valid data."""
        from src.services.products.service import ProductService, ProductCreationData
        from decimal import Decimal
        
        service = ProductService()
        
        product_data = ProductCreationData(
            seller_id="seller-123",
            name="Test Product",
            description="A detailed test product description",
            price=Decimal("99.99"),
            currency="USD",
            category="electronics",
            inventory_quantity=10
        )
        
        product = await service.create_product(product_data)
        
        assert product.id is not None
        assert product.seller_id == "seller-123"
        assert product.name == "Test Product"
        assert product.description == "A detailed test product description"
        assert product.price == Decimal("99.99")
        assert product.currency == "USD"
        assert product.category == "electronics"
        assert product.inventory_quantity == 10
        assert product.status == "active"
        assert product.is_available is True
        assert product.created_at is not None
        assert product.updated_at is not None
    
    @pytest.mark.asyncio
    async def test_create_product_with_zero_inventory(self):
        """Test creating a product with zero inventory marks it as out_of_stock."""
        from src.services.products.service import ProductService, ProductCreationData
        from decimal import Decimal
        
        service = ProductService()
        
        product_data = ProductCreationData(
            seller_id="seller-123",
            name="Out of Stock Product",
            description="A product with zero inventory",
            price=Decimal("49.99"),
            currency="USD",
            category="books",
            inventory_quantity=0
        )
        
        product = await service.create_product(product_data)
        
        assert product.inventory_quantity == 0
        assert product.status == "out_of_stock"
        assert product.is_available is False
    
    @pytest.mark.asyncio
    async def test_get_product_by_id_existing(self):
        """Test retrieving an existing product by ID."""
        from src.services.products.service import ProductService, ProductCreationData
        from decimal import Decimal
        
        service = ProductService()
        
        # Create a product first
        product_data = ProductCreationData(
            seller_id="seller-123",
            name="Retrievable Product",
            description="A product for retrieval testing",
            price=Decimal("29.99"),
            currency="USD",
            category="clothing",
            inventory_quantity=5
        )
        
        created_product = await service.create_product(product_data)
        
        # Retrieve the product
        retrieved_product = await service.get_product_by_id(created_product.id)
        
        assert retrieved_product is not None
        assert retrieved_product.id == created_product.id
        assert retrieved_product.name == "Retrievable Product"
    
    @pytest.mark.asyncio
    async def test_get_product_by_id_nonexistent(self):
        """Test retrieving a non-existent product returns None."""
        from src.services.products.service import ProductService
        
        service = ProductService()
        
        retrieved_product = await service.get_product_by_id("nonexistent-id")
        
        assert retrieved_product is None
    
    @pytest.mark.asyncio
    async def test_update_product_name_and_description(self):
        """Test updating product name and description."""
        from src.services.products.service import ProductService, ProductCreationData, ProductUpdates
        from decimal import Decimal
        
        service = ProductService()
        
        # Create initial product
        product_data = ProductCreationData(
            seller_id="seller-123",
            name="Original Name",
            description="Original description",
            price=Decimal("19.99"),
            currency="USD",
            category="toys",
            inventory_quantity=3
        )
        
        product = await service.create_product(product_data)
        original_updated_at = product.updated_at
        
        # Update product
        updates = ProductUpdates(
            name="Updated Name",
            description="Updated description with more details"
        )
        
        updated_product = await service.update_product(product.id, updates)
        
        assert updated_product.name == "Updated Name"
        assert updated_product.description == "Updated description with more details"
        assert updated_product.price == Decimal("19.99")  # Unchanged
        assert updated_product.category == "toys"  # Unchanged
        assert updated_product.inventory_quantity == 3  # Unchanged
        assert updated_product.updated_at > original_updated_at
    
    @pytest.mark.asyncio
    async def test_update_product_price_and_category(self):
        """Test updating product price and category."""
        from src.services.products.service import ProductService, ProductCreationData, ProductUpdates
        from decimal import Decimal
        
        service = ProductService()
        
        # Create initial product
        product_data = ProductCreationData(
            seller_id="seller-123",
            name="Price Test Product",
            description="Product for price testing",
            price=Decimal("50.00"),
            currency="USD",
            category="electronics",
            inventory_quantity=8
        )
        
        product = await service.create_product(product_data)
        
        # Update price and category
        updates = ProductUpdates(
            price=Decimal("75.50"),
            category="computers"
        )
        
        updated_product = await service.update_product(product.id, updates)
        
        assert updated_product.price == Decimal("75.50")
        assert updated_product.category == "computers"
        assert updated_product.name == "Price Test Product"  # Unchanged
    
    @pytest.mark.asyncio
    async def test_update_product_inventory_to_zero(self):
        """Test updating product inventory to zero changes status to out_of_stock."""
        from src.services.products.service import ProductService, ProductCreationData, ProductUpdates
        from decimal import Decimal
        
        service = ProductService()
        
        # Create product with positive inventory
        product_data = ProductCreationData(
            seller_id="seller-123",
            name="Inventory Test Product",
            description="Product for inventory testing",
            price=Decimal("25.00"),
            currency="USD",
            category="home",
            inventory_quantity=5
        )
        
        product = await service.create_product(product_data)
        assert product.status == "active"
        assert product.is_available is True
        
        # Update inventory to zero
        updates = ProductUpdates(inventory_quantity=0)
        updated_product = await service.update_product(product.id, updates)
        
        assert updated_product.inventory_quantity == 0
        assert updated_product.status == "out_of_stock"
        assert updated_product.is_available is False
    
    @pytest.mark.asyncio
    async def test_update_product_inventory_from_zero_to_positive(self):
        """Test updating product inventory from zero to positive changes status to active."""
        from src.services.products.service import ProductService, ProductCreationData, ProductUpdates
        from decimal import Decimal
        
        service = ProductService()
        
        # Create product with zero inventory
        product_data = ProductCreationData(
            seller_id="seller-123",
            name="Restock Test Product",
            description="Product for restock testing",
            price=Decimal("15.00"),
            currency="USD",
            category="books",
            inventory_quantity=0
        )
        
        product = await service.create_product(product_data)
        assert product.status == "out_of_stock"
        assert product.is_available is False
        
        # Update inventory to positive
        updates = ProductUpdates(inventory_quantity=10)
        updated_product = await service.update_product(product.id, updates)
        
        assert updated_product.inventory_quantity == 10
        assert updated_product.status == "active"
        assert updated_product.is_available is True
    
    @pytest.mark.asyncio
    async def test_update_nonexistent_product_raises_error(self):
        """Test updating a non-existent product raises ValueError."""
        from src.services.products.service import ProductService, ProductUpdates
        from decimal import Decimal
        
        service = ProductService()
        
        updates = ProductUpdates(name="New Name")
        
        with pytest.raises(ValueError, match="Product with ID nonexistent-id not found"):
            await service.update_product("nonexistent-id", updates)
    
    @pytest.mark.asyncio
    async def test_delete_existing_product(self):
        """Test deleting an existing product."""
        from src.services.products.service import ProductService, ProductCreationData
        from decimal import Decimal
        
        service = ProductService()
        
        # Create a product
        product_data = ProductCreationData(
            seller_id="seller-123",
            name="Deletable Product",
            description="A product to be deleted",
            price=Decimal("10.00"),
            currency="USD",
            category="test",
            inventory_quantity=1
        )
        
        product = await service.create_product(product_data)
        
        # Verify product exists
        retrieved_product = await service.get_product_by_id(product.id)
        assert retrieved_product is not None
        
        # Delete product
        await service.delete_product(product.id)
        
        # Verify product is deleted
        deleted_product = await service.get_product_by_id(product.id)
        assert deleted_product is None
    
    @pytest.mark.asyncio
    async def test_delete_nonexistent_product_raises_error(self):
        """Test deleting a non-existent product raises ValueError."""
        from src.services.products.service import ProductService
        
        service = ProductService()
        
        with pytest.raises(ValueError, match="Product with ID nonexistent-id not found"):
            await service.delete_product("nonexistent-id")
    
    @pytest.mark.asyncio
    async def test_update_inventory_directly(self):
        """Test updating inventory directly using update_inventory method."""
        from src.services.products.service import ProductService, ProductCreationData
        from decimal import Decimal
        
        service = ProductService()
        
        # Create product
        product_data = ProductCreationData(
            seller_id="seller-123",
            name="Inventory Update Product",
            description="Product for direct inventory updates",
            price=Decimal("30.00"),
            currency="USD",
            category="sports",
            inventory_quantity=20
        )
        
        product = await service.create_product(product_data)
        
        # Update inventory to 5
        updated_product = await service.update_inventory(product.id, 5)
        
        assert updated_product.inventory_quantity == 5
        assert updated_product.status == "active"
        assert updated_product.is_available is True
        
        # Update inventory to 0
        zero_product = await service.update_inventory(product.id, 0)
        
        assert zero_product.inventory_quantity == 0
        assert zero_product.status == "out_of_stock"
        assert zero_product.is_available is False
    
    @pytest.mark.asyncio
    async def test_update_inventory_negative_raises_error(self):
        """Test updating inventory to negative value raises ValueError."""
        from src.services.products.service import ProductService, ProductCreationData
        from decimal import Decimal
        
        service = ProductService()
        
        # Create product
        product_data = ProductCreationData(
            seller_id="seller-123",
            name="Negative Inventory Test",
            description="Product for negative inventory testing",
            price=Decimal("40.00"),
            currency="USD",
            category="test",
            inventory_quantity=5
        )
        
        product = await service.create_product(product_data)
        
        # Try to update inventory to negative
        with pytest.raises(ValueError, match="Inventory quantity cannot be negative"):
            await service.update_inventory(product.id, -1)
    
    @pytest.mark.asyncio
    async def test_update_inventory_nonexistent_product_raises_error(self):
        """Test updating inventory of non-existent product raises ValueError."""
        from src.services.products.service import ProductService
        
        service = ProductService()
        
        with pytest.raises(ValueError, match="Product with ID nonexistent-id not found"):
            await service.update_inventory("nonexistent-id", 10)
    
    @pytest.mark.asyncio
    async def test_get_products_by_seller(self):
        """Test retrieving products by seller ID."""
        from src.services.products.service import ProductService, ProductCreationData
        from decimal import Decimal
        
        service = ProductService()
        
        # Create products for different sellers
        seller1_product1 = ProductCreationData(
            seller_id="seller-1",
            name="Seller 1 Product 1",
            description="First product from seller 1",
            price=Decimal("10.00"),
            currency="USD",
            category="test",
            inventory_quantity=5
        )
        
        seller1_product2 = ProductCreationData(
            seller_id="seller-1",
            name="Seller 1 Product 2",
            description="Second product from seller 1",
            price=Decimal("20.00"),
            currency="USD",
            category="test",
            inventory_quantity=3
        )
        
        seller2_product = ProductCreationData(
            seller_id="seller-2",
            name="Seller 2 Product",
            description="Product from seller 2",
            price=Decimal("15.00"),
            currency="USD",
            category="test",
            inventory_quantity=8
        )
        
        await service.create_product(seller1_product1)
        await service.create_product(seller1_product2)
        await service.create_product(seller2_product)
        
        # Get products for seller 1
        seller1_products = await service.get_products_by_seller("seller-1")
        
        assert len(seller1_products) == 2
        assert all(p.seller_id == "seller-1" for p in seller1_products)
        
        # Get products for seller 2
        seller2_products = await service.get_products_by_seller("seller-2")
        
        assert len(seller2_products) == 1
        assert seller2_products[0].seller_id == "seller-2"
        
        # Get products for non-existent seller
        no_products = await service.get_products_by_seller("nonexistent-seller")
        
        assert len(no_products) == 0
    
    @pytest.mark.asyncio
    async def test_get_low_stock_products(self):
        """Test retrieving low stock products for a seller."""
        from src.services.products.service import ProductService, ProductCreationData
        from decimal import Decimal
        
        service = ProductService()
        
        # Create products with different stock levels
        high_stock_product = ProductCreationData(
            seller_id="seller-1",
            name="High Stock Product",
            description="Product with high stock",
            price=Decimal("10.00"),
            currency="USD",
            category="test",
            inventory_quantity=20,
            low_stock_threshold=5
        )
        
        low_stock_product = ProductCreationData(
            seller_id="seller-1",
            name="Low Stock Product",
            description="Product with low stock",
            price=Decimal("20.00"),
            currency="USD",
            category="test",
            inventory_quantity=3,
            low_stock_threshold=5
        )
        
        zero_stock_product = ProductCreationData(
            seller_id="seller-1",
            name="Zero Stock Product",
            description="Product with zero stock",
            price=Decimal("30.00"),
            currency="USD",
            category="test",
            inventory_quantity=0,
            low_stock_threshold=5
        )
        
        other_seller_low_stock = ProductCreationData(
            seller_id="seller-2",
            name="Other Seller Low Stock",
            description="Low stock product from different seller",
            price=Decimal("15.00"),
            currency="USD",
            category="test",
            inventory_quantity=2,
            low_stock_threshold=5
        )
        
        await service.create_product(high_stock_product)
        await service.create_product(low_stock_product)
        await service.create_product(zero_stock_product)
        await service.create_product(other_seller_low_stock)
        
        # Get low stock products for seller 1
        seller1_low_stock = await service.get_low_stock_products("seller-1")
        
        assert len(seller1_low_stock) == 2  # low_stock_product and zero_stock_product
        assert all(p.seller_id == "seller-1" for p in seller1_low_stock)
        assert all(p.is_low_stock for p in seller1_low_stock)
        
        # Get low stock products for seller 2
        seller2_low_stock = await service.get_low_stock_products("seller-2")
        
        assert len(seller2_low_stock) == 1
        assert seller2_low_stock[0].seller_id == "seller-2"
        assert seller2_low_stock[0].is_low_stock
    
    @pytest.mark.asyncio
    async def test_search_products_by_term(self):
        """Test searching products by term."""
        from src.services.products.service import ProductService, ProductCreationData, SearchQuery
        from decimal import Decimal
        
        service = ProductService()
        
        # Create test products
        laptop_product = ProductCreationData(
            seller_id="seller-1",
            name="Gaming Laptop",
            description="High-performance laptop for gaming",
            price=Decimal("1200.00"),
            currency="USD",
            category="electronics",
            inventory_quantity=5
        )
        
        phone_product = ProductCreationData(
            seller_id="seller-1",
            name="Smartphone",
            description="Latest smartphone with advanced features",
            price=Decimal("800.00"),
            currency="USD",
            category="electronics",
            inventory_quantity=10
        )
        
        book_product = ProductCreationData(
            seller_id="seller-1",
            name="Programming Book",
            description="Learn programming fundamentals",
            price=Decimal("50.00"),
            currency="USD",
            category="books",
            inventory_quantity=20
        )
        
        await service.create_product(laptop_product)
        await service.create_product(phone_product)
        await service.create_product(book_product)
        
        # Search for "laptop"
        laptop_query = SearchQuery(term="laptop")
        laptop_results = await service.search_products(laptop_query)
        
        assert laptop_results.total_count == 1
        assert len(laptop_results.products) == 1
        assert laptop_results.products[0].name == "Gaming Laptop"
        
        # Search for "programming"
        programming_query = SearchQuery(term="programming")
        programming_results = await service.search_products(programming_query)
        
        assert programming_results.total_count == 1
        assert len(programming_results.products) == 1
        assert programming_results.products[0].name == "Programming Book"
        
        # Search for "advanced" (in description)
        advanced_query = SearchQuery(term="advanced")
        advanced_results = await service.search_products(advanced_query)
        
        assert advanced_results.total_count == 1
        assert len(advanced_results.products) == 1
        assert advanced_results.products[0].name == "Smartphone"
    
    @pytest.mark.asyncio
    async def test_search_products_by_category(self):
        """Test searching products by category."""
        from src.services.products.service import ProductService, ProductCreationData, SearchQuery
        from decimal import Decimal
        
        service = ProductService()
        
        # Create products in different categories
        electronics1 = ProductCreationData(
            seller_id="seller-1",
            name="Tablet",
            description="Portable tablet device",
            price=Decimal("400.00"),
            currency="USD",
            category="electronics",
            inventory_quantity=8
        )
        
        electronics2 = ProductCreationData(
            seller_id="seller-1",
            name="Headphones",
            description="Wireless headphones",
            price=Decimal("150.00"),
            currency="USD",
            category="electronics",
            inventory_quantity=15
        )
        
        clothing_product = ProductCreationData(
            seller_id="seller-1",
            name="T-Shirt",
            description="Cotton t-shirt",
            price=Decimal("25.00"),
            currency="USD",
            category="clothing",
            inventory_quantity=50
        )
        
        await service.create_product(electronics1)
        await service.create_product(electronics2)
        await service.create_product(clothing_product)
        
        # Search electronics category
        electronics_query = SearchQuery(category="electronics")
        electronics_results = await service.search_products(electronics_query)
        
        assert electronics_results.total_count == 2
        assert len(electronics_results.products) == 2
        assert all(p.category == "electronics" for p in electronics_results.products)
        
        # Search clothing category
        clothing_query = SearchQuery(category="clothing")
        clothing_results = await service.search_products(clothing_query)
        
        assert clothing_results.total_count == 1
        assert len(clothing_results.products) == 1
        assert clothing_results.products[0].category == "clothing"
    
    @pytest.mark.asyncio
    async def test_search_products_by_price_range(self):
        """Test searching products by price range."""
        from src.services.products.service import ProductService, ProductCreationData, SearchQuery
        from decimal import Decimal
        
        service = ProductService()
        
        # Create products with different prices
        cheap_product = ProductCreationData(
            seller_id="seller-1",
            name="Cheap Item",
            description="Affordable product",
            price=Decimal("10.00"),
            currency="USD",
            category="test",
            inventory_quantity=10
        )
        
        medium_product = ProductCreationData(
            seller_id="seller-1",
            name="Medium Item",
            description="Mid-range product",
            price=Decimal("50.00"),
            currency="USD",
            category="test",
            inventory_quantity=5
        )
        
        expensive_product = ProductCreationData(
            seller_id="seller-1",
            name="Expensive Item",
            description="Premium product",
            price=Decimal("200.00"),
            currency="USD",
            category="test",
            inventory_quantity=2
        )
        
        await service.create_product(cheap_product)
        await service.create_product(medium_product)
        await service.create_product(expensive_product)
        
        # Search with min price
        min_price_query = SearchQuery(min_price=Decimal("40.00"))
        min_price_results = await service.search_products(min_price_query)
        
        assert min_price_results.total_count == 2
        assert all(p.price >= Decimal("40.00") for p in min_price_results.products)
        
        # Search with max price
        max_price_query = SearchQuery(max_price=Decimal("60.00"))
        max_price_results = await service.search_products(max_price_query)
        
        assert max_price_results.total_count == 2
        assert all(p.price <= Decimal("60.00") for p in max_price_results.products)
        
        # Search with price range
        range_query = SearchQuery(min_price=Decimal("20.00"), max_price=Decimal("100.00"))
        range_results = await service.search_products(range_query)
        
        assert range_results.total_count == 1
        assert range_results.products[0].name == "Medium Item"
    
    @pytest.mark.asyncio
    async def test_search_products_in_stock_only(self):
        """Test searching products with in_stock_only filter."""
        from src.services.products.service import ProductService, ProductCreationData, SearchQuery
        from decimal import Decimal
        
        service = ProductService()
        
        # Create products with different stock levels
        in_stock_product = ProductCreationData(
            seller_id="seller-1",
            name="In Stock Product",
            description="Product with inventory",
            price=Decimal("30.00"),
            currency="USD",
            category="test",
            inventory_quantity=5
        )
        
        out_of_stock_product = ProductCreationData(
            seller_id="seller-1",
            name="Out of Stock Product",
            description="Product without inventory",
            price=Decimal("40.00"),
            currency="USD",
            category="test",
            inventory_quantity=0
        )
        
        await service.create_product(in_stock_product)
        await service.create_product(out_of_stock_product)
        
        # Search with in_stock_only=True (default)
        in_stock_query = SearchQuery(in_stock_only=True)
        in_stock_results = await service.search_products(in_stock_query)
        
        assert in_stock_results.total_count == 1
        assert in_stock_results.products[0].name == "In Stock Product"
        assert in_stock_results.products[0].inventory_quantity > 0
        
        # Search with in_stock_only=False
        all_products_query = SearchQuery(in_stock_only=False)
        all_results = await service.search_products(all_products_query)
        
        assert all_results.total_count == 2
    
    @pytest.mark.asyncio
    async def test_search_products_pagination(self):
        """Test search results pagination."""
        from src.services.products.service import ProductService, ProductCreationData, SearchQuery
        from decimal import Decimal
        
        service = ProductService()
        
        # Create multiple products
        for i in range(5):
            product_data = ProductCreationData(
                seller_id="seller-1",
                name=f"Product {i+1}",
                description=f"Description for product {i+1}",
                price=Decimal(f"{10 + i}.00"),
                currency="USD",
                category="test",
                inventory_quantity=10
            )
            await service.create_product(product_data)
        
        # Test first page with page_size=2
        page1_query = SearchQuery(page=1, page_size=2)
        page1_results = await service.search_products(page1_query)
        
        assert page1_results.total_count == 5
        assert len(page1_results.products) == 2
        assert page1_results.page == 1
        assert page1_results.page_size == 2
        
        # Test second page
        page2_query = SearchQuery(page=2, page_size=2)
        page2_results = await service.search_products(page2_query)
        
        assert page2_results.total_count == 5
        assert len(page2_results.products) == 2
        assert page2_results.page == 2
        
        # Test third page (partial)
        page3_query = SearchQuery(page=3, page_size=2)
        page3_results = await service.search_products(page3_query)
        
        assert page3_results.total_count == 5
        assert len(page3_results.products) == 1
        assert page3_results.page == 3
    
    def test_product_creation_data_validation_errors(self):
        """Test ProductCreationData validation errors."""
        from src.services.products.service import ProductCreationData
        from decimal import Decimal
        import pytest
        from pydantic import ValidationError
        
        # Test empty name
        with pytest.raises(ValidationError):
            ProductCreationData(
                seller_id="seller-123",
                name="",
                description="Valid description",
                price=Decimal("10.00"),
                currency="USD",
                category="test",
                inventory_quantity=5
            )
        
        # Test negative price
        with pytest.raises(ValidationError):
            ProductCreationData(
                seller_id="seller-123",
                name="Valid Name",
                description="Valid description",
                price=Decimal("-10.00"),
                currency="USD",
                category="test",
                inventory_quantity=5
            )
        
        # Test zero price
        with pytest.raises(ValidationError):
            ProductCreationData(
                seller_id="seller-123",
                name="Valid Name",
                description="Valid description",
                price=Decimal("0.00"),
                currency="USD",
                category="test",
                inventory_quantity=5
            )
        
        # Test negative inventory
        with pytest.raises(ValidationError):
            ProductCreationData(
                seller_id="seller-123",
                name="Valid Name",
                description="Valid description",
                price=Decimal("10.00"),
                currency="USD",
                category="test",
                inventory_quantity=-1
            )
        
        # Test inventory exceeding max limit
        with pytest.raises(ValidationError):
            ProductCreationData(
                seller_id="seller-123",
                name="Valid Name",
                description="Valid description",
                price=Decimal("10.00"),
                currency="USD",
                category="test",
                inventory_quantity=20000  # Exceeds max_inventory_quantity (10000)
            )
    
    def test_product_updates_validation_errors(self):
        """Test ProductUpdates validation errors."""
        from src.services.products.service import ProductUpdates
        from decimal import Decimal
        import pytest
        from pydantic import ValidationError
        
        # Test negative price update
        with pytest.raises(ValidationError):
            ProductUpdates(price=Decimal("-5.00"))
        
        # Test zero price update
        with pytest.raises(ValidationError):
            ProductUpdates(price=Decimal("0.00"))
        
        # Test negative inventory update
        with pytest.raises(ValidationError):
            ProductUpdates(inventory_quantity=-1)
        
        # Test inventory exceeding max limit
        with pytest.raises(ValidationError):
            ProductUpdates(inventory_quantity=15000)  # Exceeds max_inventory_quantity (10000)
    
    def test_product_is_low_stock_property(self):
        """Test Product.is_low_stock property."""
        from src.services.products.service import Product
        from decimal import Decimal
        from datetime import datetime
        
        now = datetime.utcnow()
        
        # Product with inventory above threshold
        high_stock_product = Product(
            id="test-1",
            seller_id="seller-1",
            name="High Stock",
            description="Product with high stock",
            price=Decimal("10.00"),
            currency="USD",
            category="test",
            inventory_quantity=10,
            low_stock_threshold=5,
            status="active",
            created_at=now,
            updated_at=now
        )
        
        assert not high_stock_product.is_low_stock
        
        # Product with inventory at threshold
        threshold_product = Product(
            id="test-2",
            seller_id="seller-1",
            name="Threshold Stock",
            description="Product at stock threshold",
            price=Decimal("10.00"),
            currency="USD",
            category="test",
            inventory_quantity=5,
            low_stock_threshold=5,
            status="active",
            created_at=now,
            updated_at=now
        )
        
        assert threshold_product.is_low_stock
        
        # Product with inventory below threshold
        low_stock_product = Product(
            id="test-3",
            seller_id="seller-1",
            name="Low Stock",
            description="Product with low stock",
            price=Decimal("10.00"),
            currency="USD",
            category="test",
            inventory_quantity=2,
            low_stock_threshold=5,
            status="active",
            created_at=now,
            updated_at=now
        )
        
        assert low_stock_product.is_low_stock