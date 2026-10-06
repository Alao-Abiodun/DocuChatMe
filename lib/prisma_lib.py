import os
from prisma import Prisma

# Create ONE instance and export it
prisma = Prisma(
    log_queries=os.getenv("ENVIRONMENT") == "development"
)