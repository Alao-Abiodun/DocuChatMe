# DocuChat

FastAPI backend. Controllers handle HTTP, services hold business logic, repositories talk to the DB (Prisma).

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn
```

## Run

```bash
uvicorn main:app --reload
```

Docs at `/docs`.

## Structure

```
main.py            entrypoint
controllers/        request handling
services/           business logic
repositories/       data access
```

## TODO

- fix `main.py` (`FastAPI` -> `FastAPI()`, missing `Request` import)
- wire up Prisma client
- add `requirements.txt`
- auth middleware
- tests
