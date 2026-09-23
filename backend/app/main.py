from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.middleware.error_handler import api_error_handler
from app.api.v1.endpoints import documents, clauses
from app.db.session import engine, Base
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB (create tables)
    # We must ensure models are imported before this, which app.models.base does
    import app.models.base
    Base.metadata.create_all(bind=engine)
    yield

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        lifespan=lifespan
    )

    # Set all CORS enabled origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], # In prod, restrict this to frontend domain
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Register global exception handler
    app.add_exception_handler(Exception, api_error_handler)

    # Include routers
    app.include_router(documents.router, prefix=f"{settings.API_V1_STR}/documents", tags=["documents"])
    app.include_router(clauses.router, prefix=f"{settings.API_V1_STR}/documents", tags=["clauses"])

    @app.get("/health")
    async def health_check():
        return {"status": "ok"}

    return app

app = create_app()
