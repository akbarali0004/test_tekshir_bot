from aiogram import Router

from .start import rt as start_rt
from .admin_manage import rt as admins_rt
from .admin_panel import rt as panel_rt
from .channel_manage import rt as channels_rt
from .test_manage import rt as tests_rt
from .users import rt as users_rt


router = Router()
router.include_routers(start_rt, panel_rt, tests_rt, admins_rt, channels_rt, users_rt)