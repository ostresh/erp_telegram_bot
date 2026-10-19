from aiogram_dialog import Dialog
from aiogram_dialog.widgets.text import (
    Const, Format, Multi, Jinja
)
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button, Multiselect

from app.interfaces.bot.utils.emoji import Emoji
from app.interfaces.bot.dialogs.common import CommonWidgets
from app.interfaces.bot.dialogs.core import RootWindow, InnerWindow

from .states import AddGameSG as States
from .event_handler import AddGameEventHandler as EventHandler
from .getter import AddGameGetter as Getter

add_game_dialog = Dialog(
    
    # первый этап - ввод названия игры
    RootWindow(
        Multi(
            Format('{start_data[menu_text]}'),
            Jinja("{%- if dialog_data.get('game_error') -%}❌ {{ dialog_data['game_error'] }}\n\n{%- endif -%}"),
            Const(f'<b>{Emoji.GAME} ВВЕДИТЕ НАЗВАНИЕ ИГРЫ </b>'),
            sep='\n\n'
        ),
        TextInput(
            id='type_game',
            type_factory=str,
            on_success=EventHandler.on_game_typed,
            on_error=EventHandler.on_text_error
        ),
        state=States.game_input,
    ),
    
    # второй этап - выбор платформы
    InnerWindow(
        Multi(
            Format('{start_data[menu_text]}'),
            Format(f'<b>{Emoji.GAME} ИГРА: {{dialog_data[game_name]}}</b>'),
            Const(f'Выберите платформу:'),
            sep='\n\n'
        ),
        Multiselect(
            Format("✅ {item[id]}"),
            Format("🔳 {item[id]}"),
            id="multiselect_platforms",
            item_id_getter=lambda item: item["id"],
            items="platforms",
            on_state_changed=EventHandler.on_platform_select,
        ),
        Button(
            text=Const('Далее →'),
            id='end_dialog',
            on_click=EventHandler.end_dialog
        ),
        getter=Getter.get_platforms,
        state=States.select_platform
    ),
)