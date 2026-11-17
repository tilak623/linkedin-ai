import logging
import sys
import os

def setup_logging():
    log_level = logging.INFO if os.getenv("ENVIRONMENT") != "development" else logging.DEBUG
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers = [handler]
    
    # Silence overly verbose third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger("brand_agent")
