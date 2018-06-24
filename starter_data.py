import datetime
from database import *


def add_starter_data():
    Transaction.delete().execute()
    Wallet.delete().execute()
    Currency.delete().execute()
    c = Currency.create(
        name="Bitcoin",
        unit_large="btc",
        unit_small="sat",
        digits_after_decimal=8,
    )
    w = Wallet.create(
        name="BTC_Elec",
        currency=c,
    )
    Transaction.create(
        date_utc=datetime.datetime(2017, 12, 5, 0, 0, 0),
        trans_type=Transaction.TRANS_TYPES.index("Income"),
        to_wallet=w,
        to_amount=123456,
    )
    Transaction.create(
        date_utc=datetime.datetime(2017, 12, 10, 5, 6, 7),
        trans_type=Transaction.TRANS_TYPES.index("Transfer"),
        to_wallet=w,
        to_amount=30,
    )
