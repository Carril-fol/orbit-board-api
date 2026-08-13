from abc import ABC, abstractmethod
from .schemas.comment_schema import (
    DetailCommentOutputSchema,
    ListDetailCommentOutputSchema,
    RegisterCommentInputSchema,
    UpdateCommentSchema
)

class ICommentService(ABC):
    @abstractmethod
    async def create_comment(self, data: RegisterCommentInputSchema, user_id: int, task_id: int) -> None:
        pass

    @abstractmethod
    async def update_comment(self, data: UpdateCommentSchema, user_id: int, comment_id: int):
        pass

    @abstractmethod
    async def delete_comment(self, comment_id: int, user_id: int) -> None:
        pass

    @abstractmethod
    async def get_comments_by_task_id(self, task_id: int, user_id: int, limit: int = 20, offset: int = 0) -> ListDetailCommentOutputSchema:
        pass

    @abstractmethod
    async def get_comment_by_id(self, comment_id: int, user_id: int) -> DetailCommentOutputSchema:
        pass
