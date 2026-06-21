from fastapi import FastAPI

app = FastAPI(
    title= "DSA TRACKER AI",
    description="AI-assisted DSA learning and progress tracking system.",
    version = "1.0.0"
)

@app.get("/")
def home():
    return {
        "message": "Welcome to DSA Tracker AI"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }
