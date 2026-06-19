import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from src.api.routes import status, metrics, trends, sources, articles, insights, evaluation

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI App
app = FastAPI(
    title="MarketPulse Analytics API",
    description="REST API serving data mart metrics, trends, and chart configurations for MarketPulse AI Dashboard.",
    version="1.0.0",
)

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, this should be restricted to the frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handler for FileNotFoundError (Missing data mart files)
@app.exception_handler(FileNotFoundError)
async def file_not_found_exception_handler(request: Request, exc: FileNotFoundError):
    logger.error(f"File not found: {exc}")
    return JSONResponse(
        status_code=503,
        content={"detail": f"Service Unavailable: {str(exc)} Please run the ETL and Analytics pipelines first."},
    )

# Include Routers
app.include_router(status.router, prefix="/api/v1", tags=["System"])
app.include_router(metrics.router, prefix="/api/v1", tags=["Metrics"])
app.include_router(trends.router, prefix="/api/v1/trends", tags=["Trends"])
app.include_router(sources.router, prefix="/api/v1/sources", tags=["Sources"])
app.include_router(articles.router, prefix="/api/v1/articles", tags=["Articles"])
app.include_router(insights.router, prefix="/api/v1/insights", tags=["Insights"])
app.include_router(evaluation.router, prefix="/api/v1/evaluation", tags=["Evaluation"])

@app.get("/", tags=["Health Check"])
async def root():
    return {"message": "MarketPulse Analytics API is running. Visit /docs for the API documentation."}
