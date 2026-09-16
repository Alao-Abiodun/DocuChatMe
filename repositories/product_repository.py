class ProductRepository:
    async def get_products(self, product_ids: list[str]):
        # Find all products by their IDs and return them
        products = await prisma.product.find_many(
            where={
                "id": {
                    "id": product_ids
                }
            }
        )

        # Check if the productIds exists in products array
        if len(products) != len(product_ids):
            raise ValueError("Some products not found")

        return products