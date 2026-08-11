class InvalidCredentialsException(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)


class InvalidTokenExceptions(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)
        

class AuthUserAlreadyExistWithThatEmail(Exception):
    def __init__(self):
        super().__init__("An User already has this email")