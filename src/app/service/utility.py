from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repository import UtilityRepository
from app.db.models import Utility
from app.service.base import BaseService

import logging

logger = logging.getLogger(__name__)

class UtilityService(BaseService[Utility, UtilityRepository]):
    """Сервис для работы с Utility"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, UtilityRepository(session))