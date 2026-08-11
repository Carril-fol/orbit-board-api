from collaborators.repositories.collaborator_repository import CollaboratorRepository
from tasks.repositories.task_repository import TaskRepository

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
    CommentUserIsNotFromProject,
    CommentNotFound,
    CommentUserHasNoPrivileges,
    CommentTaskNotFound,
)

class CommentService:
    
    def __init__(
        self, 
        comment_repository: CommentRepository, 
        collaborator_repository: CollaboratorRepository,
        task_repo: TaskRepository
    ):
        self.comment_repository = comment_repository
        self.collaborator_repository = collaborator_repository
        self.task_repository = task_repo

    def _format_comments(self, comments: list[Comment]):
        comments_formatted = [
            DetailCommentOutputSchema.model_validate(comment)
            for comment in comments
        ]
        return ListDetailCommentOutputSchema(comments=comments_formatted)

    def _is_user_collaborator(self, user_id: int, project_id: int):
        collaborator = self.collaborator_repository.get_collaborator_by_user_id_and_project_id(user_id, project_id)
        if not collaborator:
            raise CommentUserIsNotFromProject()
        return True

    def _get_task(self, task_id: int):
        task = self.task_repository.get_by_id(task_id)
        if not task:
            raise CommentTaskNotFound()
        return task
    
    def _get_comment(self, comment_id: int):
        comment = self.comment_repository.get_by_id(comment_id)
        if not comment:
            raise CommentNotFound()
        return comment

    def create_comment(self, data: RegisterCommentInputSchema, user_id: int, task_id: int):
        project_id = self._get_task(task_id).project_id
        self._is_user_collaborator(user_id, project_id)
        
        create_comment_input = CreateCommentSchema.model_validate({
            **data.model_dump(),
            "user_id": user_id,
            "task_id": task_id,
        })
        comment_entity = Comment(**create_comment_input.model_dump())
        
        self.comment_repository.create(comment_entity)

    def update_comment(self, data: UpdateCommentSchema, user_id: int, comment_id: int):
        comment = self._get_comment(comment_id)

        if comment.user_id != user_id:
            raise CommentUserHasNoPrivileges()

        project_id = self.task_repository.get_by_id(comment.task_id).project_id
        self._is_user_collaborator(user_id, project_id)

        for key, value in data.model_dump().items():
            setattr(comment, key, value)

        self.comment_repository.update(comment)
        
    def delete_comment(self, comment_id: int, user_id: int):
        comment = self._get_comment(comment_id)

        if comment.user_id != user_id:
            raise CommentUserHasNoPrivileges()
        
        project_id = self.task_repository.get_by_id(comment.task_id).project_id
        self._is_user_collaborator(user_id, project_id)

        self.comment_repository.delete(comment.id)
        
    def get_comments_by_task_id(self, task_id: int, user_id: int, limit: int = 20, offset: int = 0):
        if not self.comment_repository.verify_user_access_to_task(user_id, task_id):
            raise CommentUserHasNoPrivileges()

        comments = self.comment_repository.get_comments_by_task_id(task_id, limit, offset)
        total = self.comment_repository.get_comments_count_by_task_id(task_id)

        comments_formatted = [
            DetailCommentOutputSchema.model_validate(comment)
            for comment in comments
        ]

        return ListDetailCommentOutputSchema(
            comments=comments_formatted,
            total=total,
            limit=limit,
            offset=offset
        )
    
    def get_comment_by_id(self, comment_id: int, user_id: int):
        comment = self._get_comment(comment_id)
        
        project_id = self.task_repository.get_by_id(comment.task_id).project_id
        self._is_user_collaborator(user_id, project_id)
        
        return DetailCommentOutputSchema.model_validate(comment).model_dump()