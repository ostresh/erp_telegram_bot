from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.repository import UtilityRepository
from app.core.db.models import Utility
from app.core.service.base import BaseService

import logging

logger = logging.getLogger(__name__)

class UtilityService(BaseService[Utility, UtilityRepository]):
    """Сервис для работы с Utility"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, UtilityRepository(session))