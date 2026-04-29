from aiogram.fsm.state import StatesGroup, State


class RegisterState(StatesGroup):
    name = State()


class CreateTest(StatesGroup):
    title = State()
    answers = State()
    duration = State()


class AddChannel(StatesGroup):
    channels = State()
    channel_id = State()


class DelChannel(StatesGroup):
    channel_id = State()
    is_checked = State()


class AddAdmin(StatesGroup):
    admins = State()
    admin_id = State()


class DelAdmin(StatesGroup):
    admin_id = State()
    is_checked = State()


class AdminStates(StatesGroup):
    waiting_for_broadcast = State()