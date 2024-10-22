from fastapi import APIRouter, Depends, Request
from lnbits.core.models import User
from lnbits.decorators import check_user_exists
from lnbits.helpers import template_renderer
from starlette.responses import HTMLResponse

from .exchange_rates import exchange_rate_providers_serializable, fiat_currencies
from .helpers import get_callback_url


def bleskomat_renderer():
    return template_renderer(["bleskomat/templates"])


bleskomat_generic_router = APIRouter()


@bleskomat_generic_router.get("/", response_class=HTMLResponse)
async def index(req: Request, user: User = Depends(check_user_exists)):
    bleskomat_vars = {
        "callback_url": get_callback_url(req),
        "exchange_rate_providers": exchange_rate_providers_serializable,
        "fiat_currencies": fiat_currencies,
    }
    return bleskomat_renderer().TemplateResponse(
        "bleskomat/index.html",
        {"request": req, "user": user.json(), "bleskomat_vars": bleskomat_vars},
    )
