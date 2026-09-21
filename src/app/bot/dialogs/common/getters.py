from aiogram_dialog import DialogManager


class CommonGetter:
    
    @staticmethod
    async def get_local_or_delivery(dialog_manager: DialogManager, **kwargs) -> dict[str, list]:
        """
        Геттер для получения методов продажи товара
        
        Содержит:
            Локально
            С доставкой
        """
        
        methods = [
        {'id': 'local', 'type': 'local', 'title': '📍 ЛОКАЛЬНО'},
        {'id': 'delivery', 'type': 'delivery', 'title': '🚚 С ДОСТАВКОЙ'},
        ]
        
        dialog_manager.dialog_data['receive_methods_map'] = {
            m['id']: m['title'] for m in methods
        }
        
        return {
            'methods' : methods
        }