from pydantic import BaseModel

class UserProfileResponse(BaseModel):
    """
    Информация о пользователе
    
    Attributes:
        key_id (str): идентификатор пользователя
    """
    
    key_id: str
    