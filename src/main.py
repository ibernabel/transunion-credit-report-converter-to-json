from fastapi import FastAPI
from src.api.routes import router

app = FastAPI(
    title="Transunion PDF to JSON API",
    description="Modern, high-performance API to parse Transunion Credit Reports into structured JSON with PII scrubbing.",
    version="0.1.0"
)

app.include_router(router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Transunion PDF to JSON API",
        "docs": "/docs",
        "v1": "/v1/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
