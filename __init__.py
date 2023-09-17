from fastapi import APIRouter

from lnbits.db import Database
from lnbits.helpers import template_renderer

db = Database("ext_bleskomat")

bleskomat_static_files = [
    {
        "path": "/bleskomat/static",
        "name": "bleskomat_static",
    }
]

bleskomat_ext: APIRouter = APIRouter(prefix="/bleskomat", tags=["Bleskomat"])


def bleskomat_renderer():
    return template_renderer(["bleskomat/templates"])


from .lnurl_api import *  # noqa: F401,F403
from .views import *  # noqa: F401,F403
from .views_api import *  # noqa: F401,F403
