from flask import url_for
from lnurl import Lnurl, LnurlWithdrawResponse, encode as lnurl_encode
from sqlite3 import Row
from typing import NamedTuple

from lnbits.settings import FORCE_HTTPS


class WithdrawLink(NamedTuple):
    id: str
    wallet: str
    title: str
    min_withdrawable: int
    max_withdrawable: int
    uses: int
    wait_time: int
    is_unique: bool
    unique_hash: str
    k1: str
    open_time: int
    used: int

    @classmethod
    def from_row(cls, row: Row) -> "WithdrawLink":
        data = dict(row)
        data["is_unique"] = bool(data["is_unique"])
        return cls(**data)

    @property
    def is_spent(self) -> bool:
        return self.used >= self.uses

    @property
    def lnurl(self) -> Lnurl:
        scheme = "https" if FORCE_HTTPS else None  
        if self.unique_hash.find(","):
            unique_hashs = self.unique_hash.split(",")
            unique_hash = unique_hashs[0]
        else:
            unique_hash = self.unique_hash
        url = url_for("withdraw.api_lnurl_response", unique_hash=unique_hash, _external=True, _scheme=scheme)
        return lnurl_encode(url)

    @property
    def lnurl_response(self) -> LnurlWithdrawResponse:
        scheme = "https" if FORCE_HTTPS else None
        if self.unique_hash.find(","):
            unique_hashs = self.unique_hash.split(",")
            unique_hash = unique_hashs[0]
        else:
            unique_hash = self.unique_hash
        url = url_for("withdraw.api_lnurl_callback", unique_hash=unique_hash, _external=True, _scheme=scheme)

        return LnurlWithdrawResponse(
            callback=url,
            k1=self.k1,
            min_withdrawable=self.min_withdrawable * 1000,
            max_withdrawable=self.max_withdrawable * 1000,
            default_description="#withdraw LNbits LNURL",
        )
