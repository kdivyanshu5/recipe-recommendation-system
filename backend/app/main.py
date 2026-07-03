from fastapi import FastAPI

app = FastAPI(
    title="Recipe Recommendation API",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "Recipe Recommendation API is running!"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }