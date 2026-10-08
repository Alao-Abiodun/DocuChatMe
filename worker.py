# worker.py
import asyncio

from lib.prisma_lib import prisma
from queues.document_worker import create_document_worker


async def main():
    await prisma.connect()
    worker = create_document_worker()
    try:
        await asyncio.Event().wait()  # keep running until stopped (Ctrl+C)
    finally:
        await worker.close()
        await prisma.disconnect()


if __name__ == "__main__":
    asyncio.run(main())