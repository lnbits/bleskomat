from fastapi import APIRouter

from .db import db
from .views import bleskomat_generic_router
from .views_api import bleskomat_api_router
from .views_lnurl import bleskomat_lnurl_router

bleskomat_static_files = [
    {
        "path": "/bleskomat/static",
        "name": "bleskomat_static",
    }
]

bleskomat_ext: APIRouter = APIRouter(prefix="/bleskomat", tags=["Bleskomat"])
bleskomat_ext.include_router(bleskomat_generic_router)
bleskomat_ext.include_router(bleskomat_api_router)
bleskomat_ext.include_router(bleskomat_lnurl_router)

__all__ = ["bleskomat_ext", "bleskomat_static_files", "db"]
