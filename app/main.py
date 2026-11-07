from fastapi import Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.auth import router as auth_router
from fastapi import FastAPI, Query
from app.scraper import scrape_jobs

app = FastAPI(
    title="JobPulse API",
    description="Job Market Data Scraping REST API",
    version="1.0"
)
limiter = Limiter(key_func=get_remote_address)

app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler
)
app.include_router(auth_router)

@app.get("/")
def home():
    return {
        "message": "Welcome to JobPulse API",
        "status": "Running"
    }


@app.get("/jobs")
@limiter.limit("10/minute")
def get_jobs(request: Request):
    jobs = scrape_jobs()

    return {
        "total_jobs": len(jobs),
        "jobs": jobs
    }
@app.get("/jobs/search")
@limiter.limit("10/minute")
def search_jobs(request: Request, title: str = None, location: str = None):
    jobs = scrape_jobs()

    if title:
        jobs = [
            job for job in jobs
            if title.lower() in job["title"].lower()
        ]

    if location:
        jobs = [
            job for job in jobs
            if location.lower() in job["location"].lower()
        ]

    return {
        "total_jobs": len(jobs),
        "jobs": jobs
    }