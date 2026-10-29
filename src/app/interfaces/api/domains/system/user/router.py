from fastapi import APIRouter, Depends

from app.interfaces.api.dependencies.auth import CurrentIdentity, get_current_identity

from .schemas import UserProfileResponse

router = APIRouter(tags=['user'])

@router.get(
    '/profile',
    response_model=UserProfileResponse,
    summary="User Profile"
)
async def profile(
    identity: CurrentIdentity = Depends(get_current_identity)
) -> UserProfileResponse:
    """
    Получение информации о пользователе
    """
    return UserProfileResponse(key_id=identity.key_id)
    