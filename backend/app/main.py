from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI(title="AgentAdvisors Backend", version="0.1.0")

    # Routers will be included here later, e.g.:
    # from .api import router as api_router
    # app.include_router(api_router)

    return app


app = create_app()

