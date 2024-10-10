from http import HTTPStatus

from fastapi import APIRouter, Depends, Query
from lnbits.core.crud import get_user
from lnbits.core.models import WalletTypeInfo
from lnbits.decorators import require_admin_key
from loguru import logger
from starlette.exceptions import HTTPException

from .crud import (
    create_bleskomat,
    delete_bleskomat,
    get_bleskomat,
    get_bleskomats,
    update_bleskomat,
)
from .exchange_rates import fetch_fiat_exchange_rate
from .models import Bleskomat, CreateBleskomat

bleskomat_api_router = APIRouter()


@bleskomat_api_router.get("/api/v1/bleskomats")
async def api_bleskomats(
    wallet: WalletTypeInfo = Depends(require_admin_key),
    all_wallets: bool = Query(False),
) -> list[Bleskomat]:
    wallet_ids = [wallet.wallet.id]

    if all_wallets:
        user = await get_user(wallet.wallet.user)
        wallet_ids = user.wallet_ids if user else []

    return await get_bleskomats(wallet_ids)


@bleskomat_api_router.get("/api/v1/bleskomat/{bleskomat_id}")
async def api_bleskomat_retrieve(
    bleskomat_id, wallet: WalletTypeInfo = Depends(require_admin_key)
) -> Bleskomat:
    bleskomat = await get_bleskomat(bleskomat_id)

    if not bleskomat or bleskomat.wallet != wallet.wallet.id:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Bleskomat configuration not found.",
        )

    return bleskomat


@bleskomat_api_router.post("/api/v1/bleskomat")
@bleskomat_api_router.put("/api/v1/bleskomat/{bleskomat_id}")
async def api_bleskomat_create_or_update(
    data: CreateBleskomat,
    wallet: WalletTypeInfo = Depends(require_admin_key),
    bleskomat_id=None,
) -> Bleskomat:
    fiat_currency = data.fiat_currency
    exchange_rate_provider = data.exchange_rate_provider
    try:
        await fetch_fiat_exchange_rate(
            currency=fiat_currency, provider=exchange_rate_provider
        )
    except Exception as exc:
        logger.error(exc)
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"""
            Failed to fetch BTC/{fiat_currency} currency pair
            from `{exchange_rate_provider}`
            """,
        ) from exc

    if bleskomat_id:
        bleskomat = await get_bleskomat(bleskomat_id)
        if not bleskomat or bleskomat.wallet != wallet.wallet.id:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail="Bleskomat configuration not found.",
            )

        for k, v in data.dict().items():
            setattr(bleskomat, k, v)
        bleskomat = await update_bleskomat(bleskomat)
    else:
        bleskomat = await create_bleskomat(wallet_id=wallet.wallet.id, data=data)

    assert bleskomat
    return bleskomat


@bleskomat_api_router.delete("/api/v1/bleskomat/{bleskomat_id}")
async def api_bleskomat_delete(
    bleskomat_id, wallet: WalletTypeInfo = Depends(require_admin_key)
) -> None:
    bleskomat = await get_bleskomat(bleskomat_id)

    if not bleskomat or bleskomat.wallet != wallet.wallet.id:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Bleskomat configuration not found.",
        )

    await delete_bleskomat(bleskomat_id)
