from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repository import DescriptionRepository
from app.db.models import Description
from app.service.base import BaseService

import logging

logger = logging.getLogger(__name__)

class DescriptionService(BaseService[Description, DescriptionRepository]):
    """Сервис для работы с Description"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, DescriptionRepository(session))