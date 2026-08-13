from abc import ABC, abstractmethod
from .schemas.requests_schemas import RegisterRequestsInputSchema, DetailRequestSchema

class IRequestsService(ABC):
    @abstractmethod
    async def create_request(self, data: RegisterRequestsInputSchema, user_id: int, project_id: int) -> None:
        pass

    @abstractmethod
    async def respond_request(self, request_id: int, user_id: int, accepted: bool) -> None:
        pass

    @abstractmethod
    async def get_all_requests(self, project_id: int, user_id: int) -> list[DetailRequestSchema]:
        pass

    @abstractmethod
    async def get_request(self, request_id: int, user_id: int) -> DetailRequestSchema:
        pass
