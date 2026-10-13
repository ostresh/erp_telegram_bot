import json

from pydantic import ValidationError

from app.core.dto.bulk_order import BulkOrderJsonDTO


class CommonValidators:

    @staticmethod
    def validate_json_for_bulk_order(text: str) -> BulkOrderJsonDTO:
        """
        Кастомный type_factory (валидатор) для TextInput: разбирает JSON-строку
        и валидирует её через BulkOrderJsonDTO.

        aiogram_dialog устроен так, что если type_factory выбрасывает ValueError,
        вызывается on_error-хендлер (on_text_error), а если возвращает объект —
        он приходит в on_success-хендлер третьим аргументом.

        Args:
            text (str): Исходная строка, введённая пользователем

        Returns:
            BulkOrderJsonDTO: Валидированный DTO оптового заказа

        Raises:
            ValueError: Если JSON некорректен или не проходит схему BulkOrderJsonDTO
        """
        
        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f'Некорректный JSON: {e.msg} (строка {e.lineno}, колонка {e.colno})') from e
        
        try:
            BulkOrderJsonDTO.model_validate_json(text)
            return text
        except ValidationError as e:
            errors = '; '.join(
                f"{'.'.join(str(loc) for loc in err['loc'])}: {err['msg']}"
                for err in e.errors()
            )
            raise ValueError(f'Ошибка схемы оптового заказа: {errors}') from e