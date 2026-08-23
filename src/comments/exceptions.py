class CommentNotFound(Exception):
    def __init__(self, message="Comment not found"):
        self.message = message
        

class CommentUserHasNoPrivileges(Exception):
    def __init__(self, message="Permission denied"):
        self.message = message
    