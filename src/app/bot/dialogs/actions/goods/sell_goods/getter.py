from aiogram_dialog import DialogManager

from app.service import RecordService
from app.db.unit_of_work import UnitOfWork


PAGINATION_THRESHOLD = 15

class SellGoodsGetter:
    
    @staticmethod
    async def get_available_record_ids(dialog_manager: DialogManager, **kwargs):
        """
        Получение id записей определенной игры
        """
        
        game_name = dialog_manager.dialog_data['game']
        
        uow: UnitOfWork = dialog_manager.middleware_data["uow"]
        
        async with uow() as session:
            service = RecordService(session)
            games = await service.get_available_by_game(game_name)
        
        return {
            'game_ids' : [{'id' : game.id, 'title' : game.id} for game in games],
            'gt_pagination_threshold' : len(games) > PAGINATION_THRESHOLD,
            'le_pagination_threshold' : 1 < len(games) <= PAGINATION_THRESHOLD,
            'is_not_one': len(games) > 1
        }