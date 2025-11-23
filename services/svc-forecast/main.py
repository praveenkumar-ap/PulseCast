import logging
from fastapi import FastAPI

from routes import router


def configure_logging() -> None:
    """Configure application logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )


def create_app() -> FastAPI:
    """Create and configure the FastAPI app."""
    configure_logging()
    app = FastAPI(title="svc-forecast")
    app.include_router(router)
    return app


app = create_app()
