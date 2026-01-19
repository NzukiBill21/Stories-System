"""Main entry point for running the API server."""
import uvicorn
from config import settings
from background_scheduler import start_background_scheduler
from loguru import logger

if __name__ == "__main__":
    # Start background scheduler for automatic scraping
    try:
        start_background_scheduler()
        logger.info("Background scheduler started - automatic scraping enabled")
    except Exception as e:
        logger.error(f"Failed to start background scheduler: {e}")
        logger.warning("Continuing without automatic scraping...")
    
    uvicorn.run(
        "api:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
