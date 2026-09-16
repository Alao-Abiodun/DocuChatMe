from repositories.order_repository import OrderRepository

class OrderService:
    async def create_order(self, order_details: dict, user: dict | None = None) -> dict:
        # Implementation for creating an order
        return await OrderRepository().create_order(order_details, user)