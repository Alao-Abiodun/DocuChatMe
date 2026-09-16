from fastapi import FastAPI
from controllers.order_controller import Order

app = FastAPI

@app.get("/")
async def root():
    return { "message": "Hello World!" }

@app.get("/orders")
async def get_orders(request: Request):
    return await Order().create_order(request)