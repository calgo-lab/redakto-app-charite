from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError as PydanticValidationError
from src.api.routes import app_info_routes
from src.api.routes import predict_routes
from src.application.services.app_info_service import AppInfoService
from src.application.services.prediction_service import PredictionService
from src.core.logging import configure_logging, get_logger, log_exception
from src.core.exceptions_handler import generic_exception_handler, redakto_exception_handler, validation_exception_handler
from src.domain.exceptions import RedaktoException
from src.infrastructure.services.model_service_impl import ModelServiceImpl

import subprocess
import sys
import threading
import time
import uvicorn

log_level: str = "INFO"
json_format: bool = False
configure_logging(log_level, json_format=json_format)

logger = get_logger(__name__)

_services_ready: bool = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _services_ready
    try:
        logger.info(f"Setting up FastAPI services ...")

        model_service = ModelServiceImpl()
        prediction_service = PredictionService(model_service)
        app_info_service = AppInfoService()
        
        app.state.app_info_service = app_info_service
        app.state.prediction_service = prediction_service
        _services_ready = True

        yield
    except Exception as ex:
        _services_ready = False
        log_exception(f"Failed to setup FastAPI services: {ex}")
        raise
    finally:
        logger.info(f"Shutting down FastAPI services ...")

app = FastAPI(lifespan=lifespan,
              title="Redakto API",
              description="API for the Redakto application",
              version="charite-1.0.0",
              docs_url="/api/docs",
              redoc_url="/api/redoc",
              openapi_url="/api/openapi.json")

app.add_exception_handler(RedaktoException, redakto_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(PydanticValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.include_router(app_info_routes.router)
app.include_router(predict_routes.router)

def run_streamlit():
    """
    Run the Streamlit application in a separate thread.
    This function starts the Streamlit app using a subprocess call.
    """
    max_wait = 10
    waited = 0

    while not _services_ready and waited < max_wait:
        time.sleep(0.5)
        waited += 0.5
    
    if not _services_ready:
        logger.error("FastAPI services not ready, aborting Streamlit app startup.")
        return

    try:
        logger.info("Starting Streamlit app ...")
        subprocess.run([
            "streamlit", "run", "streamlit_app.py", 
            "--server.port", "8501", 
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false"
        ])
    except Exception as e:
        log_exception(f"Failed to start Streamlit app: {e}")

threading.Thread(target=run_streamlit, daemon=True).start()

if __name__ == "__main__":
    try:
        logger.info("Starting uvicorn server for Redakto FastAPI ...")
        uvicorn.run(app, host="0.0.0.0", port=8000, access_log=False)
    except Exception as e:
        log_exception(f"Failed to start uvicorn server: {e}")
        sys.exit(1)