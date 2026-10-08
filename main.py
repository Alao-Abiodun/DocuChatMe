from contextlib import asynccontextmanager

import events.auth_events
import events.document_events

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from routes.auth_routes import router as auth_router
from routes.admin_routes import router as admin_router
from routes.document_routes import router as document_router
from routes.conversation_routes import router as conversation_router

from lib.errors_lib import AppError
from lib.prisma_lib import prisma

from queues.dead_letter_queue import dead_letter_queue
from queues.document_queue import document_queue
from queues.document_worker import create_document_worker


@asynccontextmanager
async def lifespan(app: FastAPI):
    await prisma.connect()
    worker = create_document_worker()  # starts listening for jobs
    yield
    await worker.close()               # finish current jobs, stop taking new ones
    await document_queue.close()
    await dead_letter_queue.close()
    await prisma.disconnect()


app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return { "message": "Hello World!" }

app.include_router(auth_router, prefix="/api/auth")

app.include_router(document_router, prefix="/api/documents")
app.include_router(conversation_router, prefix="/api/conversations")

app.include_router(admin_router, prefix="/api/v1/admin")

@app.exception_handler(AppError)
async def value_error_handler(request: Request, exc: AppError):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.message})