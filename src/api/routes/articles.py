import math
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from src.api.schemas import PaginatedResponse
from src.api.data_loader import data_loader
import pandas as pd

router = APIRouter()

@router.get("/", response_model=PaginatedResponse)
async def get_articles(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    keyword: Optional[str] = Query(None, description="Filter by keyword"),
    source: Optional[str] = Query(None, description="Filter by source name"),
    has_quality_flags: Optional[bool] = Query(None, description="Filter by presence of quality flags")
):
    """
    Returns a paginated list of processed articles, with optional filtering.
    """
    try:
        articles_df = data_loader.get_data("articles_clean")
        if articles_df is None or articles_df.empty:
            raise FileNotFoundError("Missing articles_clean.csv data.")

        df = articles_df.copy()

        # Apply filters
        if keyword:
            df = df[df['keyword'].str.contains(keyword, case=False, na=False)]
        
        if source:
            df = df[df['source'].str.contains(source, case=False, na=False)]
            
        if has_quality_flags is not None:
            if has_quality_flags:
                df = df[df['quality_flag_count'] > 0]
            else:
                df = df[df['quality_flag_count'] == 0]

        # Calculate pagination
        total_items = len(df)
        total_pages = math.ceil(total_items / limit) if limit > 0 else 1
        
        # Slicing
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_df = df.iloc[start_idx:end_idx]

        data = paginated_df.to_dict(orient="records")

        return PaginatedResponse(
            total_items=total_items,
            total_pages=total_pages,
            current_page=page,
            limit=limit,
            data=data
        )

    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=f"Service Unavailable: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
