class InvalidCredentialsException(Exception):
    def __init__(self):
        super().__init__("Invalid credentials")


class InvalidTokenExceptions(Exception):
    def __init__(self):
        super().__init__("Invalid token")
        

class AuthUserAlreadyExistWithThatEmail(Exception):
    def __init__(self):
        super().__init__("An User already has this email")