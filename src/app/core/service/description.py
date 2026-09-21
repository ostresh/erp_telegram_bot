from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.repository import DescriptionRepository
from app.core.db.models import Description
from app.core.service.base import BaseService

import logging

logger = logging.getLogger(__name__)

class DescriptionService(BaseService[Description, DescriptionRepository]):
    """Сервис для работы с Description"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, DescriptionRepository(session))