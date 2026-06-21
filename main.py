from fastapi import FastAPI

from routers import auth, users, problems

app = FastAPI(
    title="DSA Tracker AI",
    description="AI-assisted DSA learning and progress tracking system.",
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(problems.router)


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