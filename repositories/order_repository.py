class OrderRepository:
    async def create_order(self, order_details: dict, user: dict) -> dict:
        new_order = await prisma.order.create(
            data={
                "userId": user["id"],
                "amount": order_details["amount"],
                "products": {
                    "connect": [{"id": pid} for pid in order_details["products"]]
                },
            }
        )

        return new_order