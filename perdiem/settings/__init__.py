"""
Django settings for perdiem project.
:Created: 5 March 2016
:Author: Lucas Connors

"""

import os

from cbsettings import switcher

from perdiem.settings.base import BaseSettings
from perdiem.settings.prod import ProdSettings


stage = os.environ.get("PERDIEM_STAGE", "dev")
switcher.register(BaseSettings, stage == "dev")
switcher.register(ProdSettings, stage == "production")
