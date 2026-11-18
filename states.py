from aiogram.fsm.state import State, StatesGroup
class UploadAPK(StatesGroup):
    file = State()
    name = State()
    description = State()
    code = State()
    category = State()
class SearchAPK(StatesGroup):
    query = State()
class RequestAPK(StatesGroup):
    title = State()
class AddChannel(StatesGroup):
    chat_id = State()
    url = State()
class EmojiEdit(StatesGroup):
    key = State()
    custom_id = State()
class Broadcast(StatesGroup):
    message = State()
