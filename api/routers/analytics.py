"""
Analytics API endpoints for the data warehouse.
Provides REST API access to analytics and reporting functionality.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import logging

from data.warehouse.analytics.reports import AnalyticsReporter
from backend.app.config import WAREHOUSE_DATABASE_URL

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["analytics"])

# Initialize analytics reporter
analytics_reporter = AnalyticsReporter(WAREHOUSE_DATABASE_URL)

@router.get("/service-performance")
async def get_service_performance(
    start_date: Optional[datetime] = Query(None, description="Start date for analysis"),
    end_date: Optional[datetime] = Query(None, description="End date for analysis"),
    limit: int = Query(100, description="Maximum number of records to return")
):
    """Get service performance summary for the given date range."""
    try:
        df = analytics_reporter.get_service_performance_summary(start_date, end_date)
        
        # Convert DataFrame to list of dictionaries
        records = df.head(limit).to_dict('records')
        
        return {
            "status": "success",
            "data": records,
            "total_records": len(df),
            "returned_records": len(records)
        }
        
    except Exception as e:
        logger.error(f"Error getting service performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/top-services")
async def get_top_services(
    days: int = Query(30, description="Number of days to analyze"),
    limit: int = Query(10, description="Number of top services to return")
):
    """Get top performing services by usage and success rate."""
    try:
        df = analytics_reporter.get_top_performing_services(days, limit)
        records = df.to_dict('records')
        
        return {
            "status": "success",
            "data": records,
            "analysis_period_days": days
        }
        
    except Exception as e:
        logger.error(f"Error getting top services: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/content-quality")
async def get_content_quality_trends(
    start_date: Optional[datetime] = Query(None, description="Start date for analysis"),
    end_date: Optional[datetime] = Query(None, description="End date for analysis")
):
    """Get content quality trends over time."""
    try:
        df = analytics_reporter.get_content_quality_trends(start_date, end_date)
        records = df.to_dict('records')
        
        return {
            "status": "success",
            "data": records,
            "total_records": len(df)
        }
        
    except Exception as e:
        logger.error(f"Error getting content quality trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api-performance")
async def get_api_performance(
    start_date: Optional[datetime] = Query(None, description="Start date for analysis"),
    end_date: Optional[datetime] = Query(None, description="End date for analysis")
):
    """Get API performance metrics for the given date range."""
    try:
        df = analytics_reporter.get_api_performance_metrics(start_date, end_date)
        records = df.to_dict('records')
        
        return {
            "status": "success",
            "data": records,
            "total_records": len(df)
        }
        
    except Exception as e:
        logger.error(f"Error getting API performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user-engagement")
async def get_user_engagement(
    start_date: Optional[datetime] = Query(None, description="Start date for analysis"),
    end_date: Optional[datetime] = Query(None, description="End date for analysis")
):
    """Get user engagement metrics for the given date range."""
    try:
        df = analytics_reporter.get_user_engagement_metrics(start_date, end_date)
        records = df.to_dict('records')
        
        return {
            "status": "success",
            "data": records,
            "total_records": len(df)
        }
        
    except Exception as e:
        logger.error(f"Error getting user engagement: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/multilingual-coverage")
async def get_multilingual_coverage():
    """Get multilingual coverage report across all services."""
    try:
        df = analytics_reporter.get_multilingual_coverage_report()
        records = df.to_dict('records')
        
        return {
            "status": "success",
            "data": records,
            "total_records": len(df)
        }
        
    except Exception as e:
        logger.error(f"Error getting multilingual coverage: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/data-quality-dashboard")
async def get_data_quality_dashboard():
    """Get comprehensive data quality dashboard metrics."""
    try:
        dashboard_data = analytics_reporter.get_data_quality_dashboard()
        
        return {
            "status": "success",
            "data": dashboard_data
        }
        
    except Exception as e:
        logger.error(f"Error getting data quality dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/executive-summary")
async def get_executive_summary(
    days: int = Query(30, description="Number of days for the summary")
):
    """Generate executive summary report for the given period."""
    try:
        summary = analytics_reporter.generate_executive_summary(days)
        
        return {
            "status": "success",
            "data": summary
        }
        
    except Exception as e:
        logger.error(f"Error generating executive summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def analytics_health():
    """Check analytics service health."""
    try:
        # Simple health check - try to get basic metrics
        df = analytics_reporter.get_top_performing_services(1, 1)
        
        return {
            "status": "healthy",
            "service": "analytics",
            "timestamp": datetime.now().isoformat(),
            "records_available": len(df) > 0
        }
        
    except Exception as e:
        logger.error(f"Analytics health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "analytics",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

@router.get("/export/executive-summary")
async def export_executive_summary(
    days: int = Query(30, description="Number of days for the summary"),
    format: str = Query("json", description="Export format (json)")
):
    """Export executive summary report to file."""
    try:
        summary = analytics_reporter.generate_executive_summary(days)
        
        if format.lower() == "json":
            filename = analytics_reporter.export_report_to_json(summary)
            return {
                "status": "success",
                "message": f"Report exported to {filename}",
                "filename": filename
            }
        else:
            raise HTTPException(status_code=400, detail="Unsupported export format")
        
    except Exception as e:
        logger.error(f"Error exporting executive summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))