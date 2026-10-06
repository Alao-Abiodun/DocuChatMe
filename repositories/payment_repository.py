# Assignment
class PaymentRepository:
    async def check_amount(self, amount: float, user: dict) -> bool:
        # Find the user's wallet
        user_wallet = await prisma.wallet.find_unique(
            where={"userId": user["id"]}
        )

        # Handle wallet not found
        if not wallet:
            raise ValueError("Wallet not found!")

        # Check if the amount in wallet is not less than the order amount.
        return wallet.balance >= amount


