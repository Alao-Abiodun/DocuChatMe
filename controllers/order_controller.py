from fastapi import FastAPI
from fastapi.responses import JSONResponse, Response

from services.product_service import ProductService
from services.payment_service import PaymentService
from services.order_service import OrderService

class Order:
    async def create_order(self, request: Request) -> Response:
        order = await request.json()

            # Check if user is authenticated
        user = getattr(request.state, "user", None)
        if not user:
            return Response(status_code=401, content="Unauthorized")

        # Check if products exist
        products = await ProductService().get_products(order["products"])
        if not products:
            return Response(status_code=404, content="Products not found")

        # If the amount is enough
        amount = await PaymentService().check_amount(order["amount"], user)
        if not amount:
            return Response(status_code=400, content="Insufficient funds")

        # Create an order
        new_order = await OrderService().create_order(order, user)
        return JSONResponse(status_code=201, content=new_order)