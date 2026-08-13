from tasks.interfaces import ITaskService
from collaborators.interfaces import ICollaboratorService

from ..interfaces import ICommentService
from ..models.comment_model import Comment
from ..repositories.comment_repository import CommentRepository
from ..schemas.comment_schema import (
    DetailCommentOutputSchema,
    ListDetailCommentOutputSchema,
    RegisterCommentInputSchema, 
    CreateCommentSchema,
    UpdateCommentSchema
)
from ..exceptions import (
    CommentNotFound,
    CommentUserHasNoPrivileges,
)

class CommentService(ICommentService):
    
    def __init__(
        self, 
        comment_repository: CommentRepository,
        collaborator_service: ICollaboratorService,
        task_service: ITaskService
    ):
        self.comment_repository = comment_repository
        self.collaborator_service = collaborator_service
        self.task_service = task_service

    def _format_comments(self, comments: list[Comment]) -> ListDetailCommentOutputSchema:
        comments_formatted = [
            DetailCommentOutputSchema.model_validate(comment)
            for comment in comments
        ]
        return ListDetailCommentOutputSchema(comments=comments_formatted)

    async def _get_comment(self, comment_id: int) -> Comment:
        comment = await self.comment_repository.get_by_id(comment_id)
        if not comment:
            raise CommentNotFound()
        return comment

    async def create_comment(self, data: RegisterCommentInputSchema, user_id: int, task_id: int) -> None:
        task = await self.task_service.get_task_or_raise(task_id)
        await self.collaborator_service.require_project_member(user_id, task.project_id)
        
        create_comment_input = CreateCommentSchema.model_validate({
            **data.model_dump(),
            "user_id": user_id,
            "task_id": task_id,
        })
        comment_entity = Comment(**create_comment_input.model_dump())
        
        await self.comment_repository.create(comment_entity)

    async def update_comment(self, data: UpdateCommentSchema, user_id: int, comment_id: int):
        comment = await self._get_comment(comment_id)

        if comment.user_id != user_id:
            raise CommentUserHasNoPrivileges()

        task = await self.task_service.get_task_or_raise(comment.task_id)
        await self.collaborator_service.require_project_member(user_id, task.project_id)

        for key, value in data.model_dump().items():
            setattr(comment, key, value)

        await self.comment_repository.update(comment)
        
    async def delete_comment(self, comment_id: int, user_id: int) -> None:
        comment = await self._get_comment(comment_id)

        if comment.user_id != user_id:
            raise CommentUserHasNoPrivileges()
        
        task = await self.task_service.get_task_or_raise(comment.task_id)
        await self.collaborator_service.require_project_member(user_id, task.project_id)

        await self.comment_repository.delete(comment.id)
        
    async def get_comments_by_task_id(self, task_id: int, user_id: int, limit: int = 20, offset: int = 0) -> ListDetailCommentOutputSchema:
        if not await self.comment_repository.verify_user_access_to_task(user_id, task_id):
            raise CommentUserHasNoPrivileges()

        comments = await self.comment_repository.get_comments_by_task_id(task_id, limit, offset)
        total = await self.comment_repository.get_comments_count_by_task_id(task_id)

        comments_formatted = [DetailCommentOutputSchema.model_validate(comment) for comment in comments]

        return ListDetailCommentOutputSchema(
            comments=comments_formatted,
            total=total,
            limit=limit,
            offset=offset
        )
    
    async def get_comment_by_id(self, comment_id: int, user_id: int) -> DetailCommentOutputSchema:
        comment = await self._get_comment(comment_id)
        
        task = await self.task_service.get_task_or_raise(comment.task_id)
        await self.collaborator_service.require_project_member(user_id, task.project_id)
        
        return DetailCommentOutputSchema.model_validate(comment).model_dump()