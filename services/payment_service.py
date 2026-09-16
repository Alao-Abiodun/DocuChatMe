from repositories.payment_repository import PaymentRepository

class PaymentService:
   async def check_amount(self, amount: float, user: dict) -> bool:
        # Implementation for checking if the amoung is sufficient
        return await PaymentRepository().check_amount(amount, user)