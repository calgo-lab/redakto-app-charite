from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parent / "src"))

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError as PydanticValidationError

from api.exceptions_handler import (
    configuration_exception_handler,
    generic_exception_handler,
    prediction_exception_handler,
    resource_not_found_exception_handler, 
    validation_exception_handler
)
from api.routes import app_info_routes, predict_routes
from application.services.app_info_service import AppInfoService
from application.services.prediction_service import PredictionService
from config_handlers.app_info_config_handler import AppInfoConfigHandler
from core.exceptions import (
    ConfigurationException,
    PredictionException,
    ResourceNotFoundException
)
from core.logging import (
    configure_logging,
    get_logger,
    log_exception
)
from infrastructure.services.model_service_impl import ModelServiceImpl

import subprocess
import sys
import threading
import time

import uvicorn


app_info_config_handler = AppInfoConfigHandler.load_from_file()

configure_logging(log_level=app_info_config_handler.app_log_level,
                  json_format=False,
                  log_to_file=True,
                  file_prefix=app_info_config_handler.app_name.lower().replace(" ", "_"))

logger = get_logger(__name__)

_services_ready: bool = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    This function sets up and tears down services required by the FastAPI app.
    """
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
              title=f"{app_info_config_handler.app_name} API",
              description=f"API for the {app_info_config_handler.app_name} application",
              version=app_info_config_handler.app_version,
              docs_url="/api/docs",
              redoc_url="/api/redoc",
              openapi_url="/api/openapi.json")

app.add_exception_handler(ConfigurationException, configuration_exception_handler)
app.add_exception_handler(PredictionException, prediction_exception_handler)
app.add_exception_handler(PydanticValidationError, validation_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ResourceNotFoundException, resource_not_found_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.include_router(app_info_routes.router)
app.include_router(predict_routes.router)

def run_streamlit() -> None:
    """
    Run the Streamlit application in a separate thread.
    This function starts the Streamlit app using a subprocess call.

    :return: None
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
        logger.info(f"Starting uvicorn server for {app_info_config_handler.app_name} FastAPI services ...")
        uvicorn.run(app, host="0.0.0.0", port=8000, access_log=False)
    except Exception as e:
        log_exception(f"Failed to start uvicorn server: {e}")
        sys.exit(1)