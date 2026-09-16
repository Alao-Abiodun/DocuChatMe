from repositories.product_repository import ProductRepository

class ProductService:
    async def get_products(self, product_ids: list[str]):
        # Implementation for fetching products
        return await ProductRepository().get_products(product_ids)