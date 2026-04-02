from fastapi import FastAPI

app = FastAPI(title="Algo Delta", version="1.0.0")

@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}

@app.get("/")
async def root() -> dict:
    return {"message": "Hello from OCI"}