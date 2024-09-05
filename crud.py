import secrets
import time
from typing import List, Optional, Union
from uuid import uuid4

from lnbits.helpers import update_query

from .db import db
from .helpers import generate_bleskomat_lnurl_hash
from .models import Bleskomat, BleskomatLnurl, CreateBleskomat


async def create_bleskomat(data: CreateBleskomat, wallet_id: str) -> Bleskomat:
    bleskomat_id = uuid4().hex
    api_key_id = secrets.token_hex(8)
    api_key_secret = secrets.token_hex(32)
    api_key_encoding = "hex"
    await db.execute(
        """
        INSERT INTO bleskomat.bleskomats
        (
            id, wallet, api_key_id, api_key_secret, api_key_encoding,
            name, fiat_currency, exchange_rate_provider, fee
        )
        VALUES (:id, :wallet, :api_key_id, :api_key_secret, :api_key_encoding,
                :name, :fiat_currency, :exchange_rate_provider, :fee)
        """,
        {
            "id": bleskomat_id,
            "wallet": wallet_id,
            "api_key_id": api_key_id,
            "api_key_secret": api_key_secret,
            "api_key_encoding": api_key_encoding,
            "name": data.name,
            "fiat_currency": data.fiat_currency,
            "exchange_rate_provider": data.exchange_rate_provider,
            "fee": data.fee,
        },
    )
    bleskomat = await get_bleskomat(bleskomat_id)
    assert bleskomat, "Newly created bleskomat couldn't be retrieved"
    return bleskomat


async def get_bleskomat(bleskomat_id: str) -> Optional[Bleskomat]:
    row = await db.fetchone(
        "SELECT * FROM bleskomat.bleskomats WHERE id = :id", {"id": bleskomat_id}
    )
    return Bleskomat(**row) if row else None


async def get_bleskomat_by_api_key_id(api_key_id: str) -> Optional[Bleskomat]:
    row = await db.fetchone(
        "SELECT * FROM bleskomat.bleskomats WHERE api_key_id = :id", {"id": api_key_id}
    )
    return Bleskomat(**row) if row else None


async def get_bleskomats(wallet_ids: Union[str, List[str]]) -> List[Bleskomat]:
    if isinstance(wallet_ids, str):
        wallet_ids = [wallet_ids]
    q = ",".join([f"'{wallet_id}'" for wallet_id in wallet_ids])
    rows = await db.fetchall(
        f"SELECT * FROM bleskomat.bleskomats WHERE wallet IN ({q})"
    )
    return [Bleskomat(**row) for row in rows]


async def update_bleskomat(bleskomat_id: str, data: CreateBleskomat) -> Bleskomat:
    await db.execute(
        update_query("bleskomat.bleskomats", data), {"id": bleskomat_id, **data.dict()}
    )
    row = await db.fetchone(
        "SELECT * FROM bleskomat.bleskomats WHERE id = :id", {"id": bleskomat_id}
    )
    assert row, "Bleskomat not found after update"
    return Bleskomat(**row)


async def delete_bleskomat(bleskomat_id: str) -> None:
    await db.execute(
        "DELETE FROM bleskomat.bleskomats WHERE id = :id", {"id": bleskomat_id}
    )


async def create_bleskomat_lnurl(
    *, bleskomat: Bleskomat, secret: str, tag: str, params: str, uses: int = 1
) -> BleskomatLnurl:
    bleskomat_lnurl_id = uuid4().hex
    lnurl_hash = generate_bleskomat_lnurl_hash(secret)
    now = int(time.time())
    await db.execute(
        """
        INSERT INTO bleskomat.bleskomat_lnurls (
            id, bleskomat, wallet, hash, tag, params, api_key_id,
            initial_uses, remaining_uses, created_time, updated_time
        )
        VALUES (:id, :bleskomat, :wallet, :hash, :tag, :params, :api_key_id,
                :initial_uses, :remaining_uses, :created_time, :updated_time)
        """,
        {
            "id": bleskomat_lnurl_id,
            "bleskomat": bleskomat.id,
            "wallet": bleskomat.wallet,
            "hash": lnurl_hash,
            "tag": tag,
            "params": params,
            "api_key_id": bleskomat.api_key_id,
            "initial_uses": uses,
            "remaining_uses": uses,
            "created_time": now,
            "updated_time": now,
        },
    )
    bleskomat_lnurl = await get_bleskomat_lnurl(secret)
    assert bleskomat_lnurl, "Newly created bleskomat LNURL couldn't be retrieved"
    return bleskomat_lnurl


async def get_bleskomat_lnurl(secret: str) -> Optional[BleskomatLnurl]:
    lnurl_hash = generate_bleskomat_lnurl_hash(secret)
    row = await db.fetchone(
        "SELECT * FROM bleskomat.bleskomat_lnurls WHERE hash = :hash",
        {"hash": lnurl_hash},
    )
    return BleskomatLnurl(**row) if row else None
