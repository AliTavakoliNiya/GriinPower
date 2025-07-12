from models.users import get_user_by_username


class UserSession:
    """Singleton class to store the current user's session info."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:  # new loggin
            cls._instance = super(UserSession, cls).__new__(cls)
            cls._instance.id = None
            cls._instance.username = None
            cls._instance.password = None
            cls._instance.first_name = None
            cls._instance.last_name = None
            cls._instance.email = None
            cls._instance.role = None
            cls._instance.created_at = None
        return cls._instance

    def set_user(self, user):
        self.id = user.id
        self.username = user.username
        self.password = user.password
        self.first_name = user.first_name
        self.last_name = user.last_name
        self.email = user.email
        self.role = user.role
        self.created_at = user.created_at

    def clear(self):
        """Clear the session (e.g., on logout)."""
        self.__class__._instance = None


def authenticate(username: str, password: str) -> bool:
    user = get_user_by_username(username, password)
    if user:
        UserSession().set_user(user)
        return True
    return False
