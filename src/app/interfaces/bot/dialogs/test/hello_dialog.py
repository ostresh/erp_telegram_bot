"""
ДЕМО-ДИАЛОГ: все возможности aiogram-dialog 2.6.0 в одном месте.

Запуск: команда /hello

Содержит примеры всех виджетов:
- Тексты: Const, Format, Jinja, Case, Multi
- Кнопки: Button, SwitchTo, Back, Cancel, Url, Calendar, Counter
- Группировки: Group, Row, Column
- Выбор: Select, Multiselect, Radio, Checkbox
- Ввод: TextInput, MessageInput
- Навигация: ScrollingGroup, NextPage, PrevPage
- Условная отрисовка: When
- Данные: dialog_data, start_data
"""

from datetime import datetime
from typing import Any

from aiogram.types import CallbackQuery, Message, ContentType
from aiogram.fsm.state import StatesGroup, State

from aiogram_dialog import Dialog, Window, DialogManager, StartMode
from aiogram_dialog.widgets.kbd import (
    Button, SwitchTo, Back, Cancel,
    Group, Row, Column,
    Select, Multiselect, Radio, Checkbox,
    ScrollingGroup, NextPage, PrevPage,
    Url, Counter, Calendar,
)
from aiogram_dialog.widgets.text import (
    Const, Format, Jinja, Case, Multi,
)
from aiogram_dialog.widgets.input import TextInput, MessageInput


# ========================================
# СОСТОЯНИЯ ДИАЛОГА
# ========================================
class HelloSG(StatesGroup):
    """Все состояния демо-диалога"""
    main = State()
    texts = State()
    buttons = State()
    select = State()
    multi_select = State()
    radio = State()
    checkbox = State()
    input_text = State()
    input_message = State()
    calendar = State()
    counter = State()
    scroll = State()
    result = State()


# ========================================
# ГЕТТЕРЫ — получение данных для окон
# ========================================
async def get_main_data(dialog_manager: DialogManager, **kwargs):
    """Данные для главного окна"""
    return {
        "name": "Пользователь",
        "current_time": datetime.now().strftime("%H:%M:%S"),
        "clicks_count": dialog_manager.dialog_data.get("clicks", 0),
    }


async def get_select_data(dialog_manager: DialogManager, **kwargs):
    """Данные для примера Select"""
    return {
        "fruits": [
            {"id": "1", "name": "🍎 Яблоко"},
            {"id": "2", "name": "🍌 Банан"},
            {"id": "3", "name": "🍊 Апельсин"},
            {"id": "4", "name": "🍇 Виноград"},
            {"id": "5", "name": "🍓 Клубника"},
        ],
        "current_fruit": dialog_manager.dialog_data.get("selected_fruit", "не выбрано"),
    }


async def get_multiselect_data(dialog_manager: DialogManager, **kwargs):
    """Данные для Multiselect"""
    return {
        "toppings": [
            {"id": "cheese", "name": "🧀 Сыр"},
            {"id": "pepperoni", "name": "🍕 Пепперони"},
            {"id": "mushrooms", "name": "🍄 Грибы"},
            {"id": "olives", "name": "🫒 Оливки"},
        ],
    }


async def get_scroll_data(dialog_manager: DialogManager, **kwargs):
    """Данные для пагинации (50 элементов)"""
    items = [{"id": str(i), "name": f"Элемент #{i}"} for i in range(1, 51)]
    return {"items": items}


async def get_result_data(dialog_manager: DialogManager, **kwargs):
    """Собираем все данные из dialog_data для итогового экрана"""
    return {
        "clicks": dialog_manager.dialog_data.get("clicks", 0),
        "selected_fruit": dialog_manager.dialog_data.get("selected_fruit", "—"),
        "name_input": dialog_manager.dialog_data.get("name_input", "—"),
        "counter_value": dialog_manager.dialog_data.get("counter_value", 0),
        "selected_date": dialog_manager.dialog_data.get("selected_date", "—"),
        "radio_choice": dialog_manager.dialog_data.get("radio_choice", "—"),
        "checkbox_checked": dialog_manager.dialog_data.get("checkbox_checked", False),
    }


# ========================================
# ОБРАБОТЧИКИ СОБЫТИЙ
# ========================================
async def on_button_click(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    """Обычная кнопка — считаем клики"""
    clicks = manager.dialog_data.get("clicks", 0) + 1
    manager.dialog_data["clicks"] = clicks
    await callback.answer(f"Клик #{clicks}!")


async def on_fruit_selected(
    callback: CallbackQuery,
    widget: Select,
    manager: DialogManager,
    item_id: str,
):
    """Обработчик выбора фрукта"""
    manager.dialog_data["selected_fruit"] = item_id
    await callback.answer(f"Выбран фрукт с id={item_id}")


async def on_multiselect_changed(
    event: CallbackQuery,
    widget: Multiselect,
    manager: DialogManager,
    item_id: str,
):
    """Обработчик Multiselect — изменение выбора"""
    selected = widget.get_checked()
    await event.answer(f"Выбрано: {', '.join(selected)}")


async def on_radio_changed(
    event: CallbackQuery,
    widget: Radio,
    manager: DialogManager,
    item_id: str,
):
    """Обработчик Radio"""
    manager.dialog_data["radio_choice"] = item_id
    await event.answer(f"Выбрано: {item_id}")


async def on_checkbox_changed(
    event: CallbackQuery,
    widget: Checkbox,
    manager: DialogManager,
    checked: bool,
):
    """Обработчик Checkbox"""
    manager.dialog_data["checkbox_checked"] = checked
    await event.answer()


async def on_name_success(
    message: Message,
    widget: TextInput,
    manager: DialogManager,
    text: str,
):
    """Успешный ввод имени (валидация прошла)"""
    manager.dialog_data["name_input"] = text
    await message.answer(f"✅ Принято: {text}")
    await manager.next()


async def on_name_error(
    message: Message,
    widget: TextInput,
    manager: DialogManager,
    error: ValueError,
):
    """Ошибка валидации имени"""
    await message.answer(f"❌ Ошибка: {error}. Попробуйте ещё раз.")


def validate_name(value: str) -> str:
    """Фабрика типа для валидации имени"""
    if len(value) < 2:
        raise ValueError("Имя должно быть минимум 2 символа")
    if len(value) > 50:
        raise ValueError("Имя слишком длинное")
    return value


async def on_photo_received(
    message: Message,
    widget: MessageInput,
    manager: DialogManager,
):
    """Обработка любого сообщения (фото, голос, видео и т.д.)"""
    if message.photo:
        await message.answer(f"✅ Получено фото, id: {message.photo[-1].file_id}")
    elif message.voice:
        await message.answer("✅ Получено голосовое сообщение")
    elif message.video:
        await message.answer("✅ Получено видео")
    else:
        await message.answer(f"✅ Получен текст: {message.text}")
    
    manager.dialog_data["received_message"] = True
    await manager.next()


async def on_date_selected(
    callback: CallbackQuery,
    widget: Calendar,
    manager: DialogManager,
    selected_date: datetime,
):
    """Выбрана дата в календаре"""
    manager.dialog_data["selected_date"] = selected_date.strftime("%d.%m.%Y")
    await manager.next()
    await callback.answer()


async def on_counter_changed(
    event: CallbackQuery,
    widget: Counter,
    manager: DialogManager,
):
    """Изменение счётчика"""
    counter = manager.find("amount_counter")
    value = counter.get_value()
    manager.dialog_data["counter_value"] = value
    await event.answer(f"Значение: {value}")


async def on_go_to_result(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    """Переход к итоговым данным"""
    await manager.switch_to(HelloSG.result)
    await callback.answer()


async def on_restart(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    """Перезапуск диалога с нуля"""
    manager.dialog_data.clear()
    await manager.switch_to(HelloSG.main)
    await callback.answer()

# ========================================
# САМ ДИАЛОГ
# ========================================
hello_dialog = Dialog(

    # ============ ГЛАВНОЕ МЕНЮ ============
    Window(
        Multi(
            Const("🎨 <b>ДЕМО AIОGRAM-DIALOG</b>\n\n"),
            Format("👋 Привет, {name}!\n"),
            Format("⏰ Время: {current_time}\n"),
            Format("🔢 Кликов по кнопке: {clicks_count}\n\n"),
            Const("Выбери раздел для изучения:"),
        ),
        
        Group(
            Button(
                Const("🔢 Кликни меня!"),
                id="click_btn",
                on_click=on_button_click,
            ),
            
            SwitchTo(Const("📝 Тексты"), id="to_texts", state=HelloSG.texts),
            SwitchTo(Const("🔘 Кнопки"), id="to_buttons", state=HelloSG.buttons),
            SwitchTo(Const("🍎 Select"), id="to_select", state=HelloSG.select),
            SwitchTo(Const("✅ Multi"), id="to_multi", state=HelloSG.multi_select),
            SwitchTo(Const("📻 Radio"), id="to_radio", state=HelloSG.radio),
            SwitchTo(Const("☑️ Checkbox"), id="to_check", state=HelloSG.checkbox),
            SwitchTo(Const("⌨️ Ввод текста"), id="to_input", state=HelloSG.input_text),
            SwitchTo(Const("📎 Ввод медиа"), id="to_msg", state=HelloSG.input_message),
            SwitchTo(Const("📅 Календарь"), id="to_cal", state=HelloSG.calendar),
            SwitchTo(Const("🔢 Counter"), id="to_counter", state=HelloSG.counter),
            SwitchTo(Const("📜 Пагинация"), id="to_scroll", state=HelloSG.scroll),
            SwitchTo(Const("📊 Итоги"), id="to_result", state=HelloSG.result),
            width=2,
        ),
        
        Cancel(Const("❌ Закрыть")),
        state=HelloSG.main,
        getter=get_main_data,
    ),

    # ============ ТЕКСТЫ (Const, Format, Jinja, Case) ============
    Window(
        Const("📝 <b>ВИДЖЕТЫ ТЕКСТА</b>\n\n"),
        
        Const("1️⃣ <b>Const</b> — статичный текст (этот самый)\n\n"),
        
        Format("2️⃣ <b>Format</b> — с переменными: {clicks_count} кликов\n\n"),
        
        Jinja("""3️⃣ <b>Jinja</b> — условный текст:
{% if clicks_count > 5 %}
   🔥 Ты профи! Кликов больше 5
{% elif clicks_count > 0 %}
   👍 Хороший прогресс
{% else %}
   🐣 Кликов ещё нет — кликни кнопку в главном меню
{% endif %}

"""),
        
        Const("4️⃣ <b>Case</b> — варианты по условию: "),
        Case(
            {
                0: Const("ноль кликов 🥚"),
                1: Const("один клик 👆"),
                ...: Format("{clicks_count} кликов 🎉"),  # Default case
            },
            selector="clicks_count",
        ),
        Const("\n"),
        
        Const("\n5️⃣ <b>Multi</b> — объединение текстов:\n"),
        Multi(
            Const("  • Строка 1"),
            Const("  • Строка 2"),
            Const("  • Строка 3"),
        ),
        
        Row(
            Back(Const("⬅️ Назад")),
            Cancel(Const("❌ Закрыть")),
        ),
        state=HelloSG.texts,
        getter=get_main_data,
    ),

    # ============ КНОПКИ (Url) ============
    Window(
        Const("🔘 <b>ТИПЫ КНОПОК</b>\n\n"),
        
        Const("• <b>Button</b> — обычная кнопка с on_click\n"),
        Const("• <b>SwitchTo</b> — переход между состояниями\n"),
        Const("• <b>Back</b> — возврат к предыдущему окну\n"),
        Const("• <b>Cancel</b> — закрытие всего диалога\n"),
        Const("• <b>Url</b> — кнопка со ссылкой\n\n"),
        
        Url(
            Const("🌐 Открыть документацию"),
            Const("https://aiogram-dialog.readthedocs.io/"),
        ),
        
        Row(
            Back(Const("⬅️ Назад")),
            Cancel(Const("❌ Закрыть")),
        ),
        state=HelloSG.buttons,
    ),

    # ============ SELECT (выбор одного) ============
    Window(
        Const("🍎 <b>SELECT</b> — выбор одного элемента из списка\n\n"),
        Format("Выбрано: {current_fruit}\n\n"),
        
        Select(
            Format("{item[name]}"),
            id="fruit_select",
            item_id_getter=lambda item: item["id"],
            items="fruits",
            on_click=on_fruit_selected,
        ),
        
        Row(
            Back(Const("⬅️ Назад")),
            Cancel(Const("❌ Закрыть")),
        ),
        state=HelloSG.select,
        getter=get_select_data,
    ),

    # ============ MULTISELECT (выбор нескольких) ============
    Window(
        Const("✅ <b>MULTISELECT</b> — выбор нескольких элементов\n\n"),
        Const("Выберите начинку для пиццы (можно несколько):\n\n"),
        
        Multiselect(
            Format("✓ {item[name]}"),
            Format("✗ {item[name]}"),
            id="topping_select",
            item_id_getter=lambda item: item["id"],
            items="toppings",
            on_state_changed=on_multiselect_changed,
        ),
        
        Row(
            Back(Const("⬅️ Назад")),
            Cancel(Const("❌ Закрыть")),
        ),
        state=HelloSG.multi_select,
        getter=get_multiselect_data,
    ),

    # ============ RADIO (радиокнопки) ============
    Window(
        Const("📻 <b>RADIO</b> — один из многих, с индикатором\n\n"),
        
        Column(
            Radio(
                Format("🔘 {item[name]}"),
                Format("⚪ {item[name]}"),
                id="size_radio",
                item_id_getter=lambda item: item["id"],
                items=[
                    {"id": "small", "name": "Маленький"},
                    {"id": "medium", "name": "Средний"},
                    {"id": "large", "name": "Большой"},
                ],
                on_state_changed=on_radio_changed,
            ),
        ),
        
        Row(
            Back(Const("⬅️ Назад")),
            Cancel(Const("❌ Закрыть")),
        ),
        state=HelloSG.radio,
    ),

    # ============ CHECKBOX (один чекбокс) ============
    Window(
        Const("☑️ <b>CHECKBOX</b> — одиночный переключатель\n\n"),
        
        Checkbox(
            Const("☑️ Я согласен с условиями"),
            Const("☐ Я согласен с условиями"),
            id="agree_check",
            default=False,
            on_state_changed=on_checkbox_changed,
        ),
        
        Row(
            Back(Const("⬅️ Назад")),
            Cancel(Const("❌ Закрыть")),
        ),
        state=HelloSG.checkbox,
    ),

    # ============ ВВОД ТЕКСТА ============
    Window(
        Const("⌨️ <b>TEXTINPUT</b> — ввод текста с валидацией\n\n"),
        Const("Введите имя (2-50 символов):\n"),
        
        TextInput(
            id="name_input",
            type_factory=validate_name,
            on_success=on_name_success,
            on_error=on_name_error,
        ),
        
        Row(
            Back(Const("⬅️ Назад")),
            Cancel(Const("❌ Закрыть")),
        ),
        state=HelloSG.input_text,
    ),

    # ============ ВВОД ЛЮБЫХ СООБЩЕНИЙ ============
    Window(
        Const("📎 <b>MESSAGEINPUT</b> — ввод любых сообщений\n\n"),
        Const("Отправьте любое сообщение: текст, фото, голос, видео...\n"),
        
        MessageInput(
            func=on_photo_received,
            content_types=[ContentType.TEXT, ContentType.PHOTO, ContentType.VOICE, ContentType.VIDEO],
        ),
        
        Row(
            Back(Const("⬅️ Назад")),
            Cancel(Const("❌ Закрыть")),
        ),
        state=HelloSG.input_message,
    ),

    # ============ КАЛЕНДАРЬ ============
    Window(
        Const("📅 <b>CALENDAR</b> — выбор даты\n\n"),
        Const("Выберите дату:\n"),
        
        Calendar(
            id="date_calendar",
            on_click=on_date_selected,
        ),
        
        Row(
            Back(Const("⬅️ Назад")),
            Cancel(Const("❌ Закрыть")),
        ),
        state=HelloSG.calendar,
    ),

    # ============ СЧЁТЧИК ============
    Window(
        Const("🔢 <b>COUNTER</b> — числовой счётчик с +/-\n\n"),
        Const("Укажите количество:\n"),
        
        Counter(
            id="amount_counter",
            default=1,
            min_value=0,
            max_value=100,
            increment=1,
            cycle=False,
            on_click=on_counter_changed,
        ),
        
        Row(
            Back(Const("⬅️ Назад")),
            Cancel(Const("❌ Закрыть")),
        ),
        state=HelloSG.counter,
    ),

   # ============ ПАГИНАЦИЯ (ScrollingGroup) ============
    Window(
        Const("📜 <b>SCROLLINGGROUP</b> — пагинация списка\n\n"),
        Const("50 элементов, 5 на странице:\n\n"),
        
        ScrollingGroup(
            Select(
                Format("{item[name]}"),
                id="scroll_item",
                item_id_getter=lambda item: item["id"],
                items="items",
                on_click=lambda c, w, m, i: c.answer(f"Клик на элемент {i}"),
            ),
            id="items_scroll",
            width=1,
            height=5,
        ),
        
        Row(
            PrevPage(scroll="items_scroll", text=Const("⬅️ Назад")),
            NextPage(scroll="items_scroll", text=Const("➡️ Вперёд")),
        ),
        
        Row(
            Back(Const("⬅️ Назад")),
            Cancel(Const("❌ Закрыть")),
        ),
        state=HelloSG.scroll,
        getter=get_scroll_data,
    ),

    # ============ ИТОГОВОЕ ОКНО ============
    Window(
        Const("📊 <b>ИТОГИ ДИАЛОГА</b>\n\n"),
        Const("Все данные, собранные через dialog_data:\n\n"),
        
        Format("🔢 Кликов: <b>{clicks}</b>\n"),
        Format("🍎 Фрукт: <b>{selected_fruit}</b>\n"),
        Format("👤 Имя: <b>{name_input}</b>\n"),
        Format("📅 Дата: <b>{selected_date}</b>\n"),
        Format("🔢 Counter: <b>{counter_value}</b>\n"),
        Format("📻 Radio: <b>{radio_choice}</b>\n"),
        Format("☑️ Checkbox: <b>{checkbox_checked}</b>\n\n"),
        
        Const("Это всё сохраняется в <code>dialog_data</code>"),
        
        Row(
            Button(Const("🔄 Начать заново"), id="restart", on_click=on_restart),
            Back(Const("⬅️ Назад")),
        ),
        Cancel(Const("❌ Закрыть диалог")),
        state=HelloSG.result,
        getter=get_result_data,
    ),
)


# Обработчик для Multiselect (добавлен)
async def on_multiselect_changed(
    event: CallbackQuery,
    widget: Multiselect,
    manager: DialogManager,
    item_id: str,
):
    """Обработчик Multiselect"""
    selected = widget.get_checked()
    await event.answer(f"Выбрано: {', '.join(selected)}")