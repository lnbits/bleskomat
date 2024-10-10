import secrets
import time
from typing import List, Optional, Union
from uuid import uuid4

from .db import db
from .helpers import generate_bleskomat_lnurl_hash
from .models import Bleskomat, BleskomatLnurl, CreateBleskomat


async def create_bleskomat(data: CreateBleskomat, wallet_id: str) -> Bleskomat:
    bleskomat_id = uuid4().hex
    api_key_id = secrets.token_hex(8)
    api_key_secret = secrets.token_hex(32)
    api_key_encoding = "hex"
    bleskomat = Bleskomat(
        id=bleskomat_id,
        wallet=wallet_id,
        api_key_id=api_key_id,
        api_key_secret=api_key_secret,
        api_key_encoding=api_key_encoding,
        **data.dict(),
    )
    await db.insert("bleskomat.bleskomats", bleskomat)
    return bleskomat


async def get_bleskomat(bleskomat_id: str) -> Optional[Bleskomat]:
    return await db.fetchone(
        "SELECT * FROM bleskomat.bleskomats WHERE id = :id",
        {"id": bleskomat_id},
        Bleskomat,
    )


async def get_bleskomat_by_api_key_id(api_key_id: str) -> Optional[Bleskomat]:
    return await db.fetchone(
        "SELECT * FROM bleskomat.bleskomats WHERE api_key_id = :id",
        {"id": api_key_id},
        Bleskomat,
    )


async def get_bleskomats(wallet_ids: Union[str, List[str]]) -> List[Bleskomat]:
    if isinstance(wallet_ids, str):
        wallet_ids = [wallet_ids]
    q = ",".join([f"'{wallet_id}'" for wallet_id in wallet_ids])
    return await db.fetchall(
        f"SELECT * FROM bleskomat.bleskomats WHERE wallet IN ({q})",
        model=Bleskomat,
    )


async def update_bleskomat(bleskomat: Bleskomat) -> Bleskomat:
    await db.update("bleskomat.bleskomats", bleskomat)
    return bleskomat


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
    bleskomat_lnurl = BleskomatLnurl(
        id=bleskomat_lnurl_id,
        bleskomat=bleskomat.id,
        wallet=bleskomat.wallet,
        hash=lnurl_hash,
        tag=tag,
        params=params,
        api_key_id=bleskomat.api_key_id,
        initial_uses=uses,
        remaining_uses=uses,
        created_time=now,
        updated_time=now,
    )
    await db.insert("bleskomat.bleskomat_lnurls", bleskomat_lnurl)
    return bleskomat_lnurl


async def get_bleskomat_lnurl(secret: str) -> Optional[BleskomatLnurl]:
    lnurl_hash = generate_bleskomat_lnurl_hash(secret)
    return await db.fetchone(
        "SELECT * FROM bleskomat.bleskomat_lnurls WHERE hash = :hash",
        {"hash": lnurl_hash},
        BleskomatLnurl,
    )
