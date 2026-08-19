from fastapi import FastAPI

from app.routers import auth, links

app = FastAPI(
    title="URL Shortener with Analytics API",
    description="Shorten URLs and track clicks by device, location, and time",
    version="0.1.0",
)

app.include_router(auth.router)
app.include_router(links.router)


@app.get("/")
def root():
    return {"status": "ok", "message": "URL Shortener API работает"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}