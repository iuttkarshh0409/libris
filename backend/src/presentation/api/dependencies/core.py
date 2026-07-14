from src.application.container import container
from src.application.services.ingestion_application_service import IngestionApplicationService
from src.application.services.query_application_service import QueryApplicationService


def get_ingestion_service() -> IngestionApplicationService:
    """Dependency resolver for IngestionApplicationService."""
    return container.ingestion_service


def get_query_service() -> QueryApplicationService:
    """Dependency resolver for QueryApplicationService."""
    return container.query_service
