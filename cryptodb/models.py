from peewee import *

DB = Proxy()


class Currency(Model):
    class Meta:
        database = DB

    name = CharField(max_length=50, null=False)

    unit_large = CharField(max_length=20, null=False)

    unit_small = CharField(max_length=20, null=False)

    digits_after_decimal = IntegerField(null=False)

    usd_per_large = FloatField(null=True)

    value_url = CharField(max_length=500, null=True)

    notes = CharField(max_length=500, null=True)

    info_block = CharField(max_length=500, null=True)

    info_tx = CharField(max_length=500, null=True)

    info_addr = CharField(max_length=500, null=True)

    def format_large(self, small_amount):
        fmt = "{} {:."+str(self.digits_after_decimal)+"f}"
        return fmt.format(self.unit_large, small_amount/(10**self.digits_after_decimal))
        # dsh -0.02460000

    def format_small(self, small_amount):
        fmt = "{} {:<3}"
        return fmt.format(small_amount, self.unit_small)
        # -2460000 sat


class Wallet(Model):
    class Meta:
        database = DB

    name = CharField(max_length=50, null=False)

    currency = ForeignKeyField(
        Currency,
        null=False, on_update='CASCADE')

    location = CharField(max_length=50, null=True)

    paper_local = CharField(max_length=500, null=True)

    paper_offsite_1 = CharField(max_length=500, null=True)

    paper_offsite_2 = CharField(max_length=500, null=True)

    level_of_trust = CharField(max_length=500, null=True)

    notes = CharField(max_length=500, null=True)

    group = IntegerField(null=True)

    public_key = CharField(max_length=500, null=True)


class Transaction(Model):
    class Meta:
        database = DB
        db_table = 'trans'

    # date_utc
    date_utc = DateTimeField(null=False)

    # trans_type
    trans_type_enum = {
        "?": "Unknown",
        "GFT": "Purchase",
        "PUR": "Purchase",
        "TRX": "Transfer",
        "EXC": "Exchange",
        "AIR": "Airdrop",
    }
    trans_type = FixedCharField(null=False, max_length=3)

    @property
    def trans_type_str(self):
        return Transaction.trans_type_enum[self.trans_type]

    # from_wallet
    from_wallet = ForeignKeyField(
        Wallet, related_name='transaction_from',
        null=True, on_update='CASCADE')

    @property
    def from_wallet_str(self):
        if self.from_wallet:
            return self.from_wallet.name
        return ""

    # to_wallet
    to_wallet = ForeignKeyField(
        Wallet, related_name='transaction_to',
        null=True, on_update='CASCADE')

    @property
    def to_wallet_str(self):
        if self.to_wallet:
            return self.to_wallet.name
        return ""

    # fee_wallet
    fee_wallet = ForeignKeyField(
        Wallet, related_name='transaction_fee',
        null=True, on_update='CASCADE')

    @property
    def fee_wallet_str(self):
        if self.fee_wallet:
            return self.fee_wallet.name
        return ""

    # from_amount
    from_amount = BigIntegerField(null=True)

    @property
    def from_amount_str(self):
        if self.from_wallet:
            return self.from_wallet.currency.format_large(-self.from_amount)
        return ""

    # to_amount
    to_amount = BigIntegerField(null=True)

    @property
    def to_amount_str(self):
        if self.to_wallet:
            return self.to_wallet.currency.format_large(-self.to_amount)
        return ""

    # fee_amount
    fee_amount = BigIntegerField(null=True)

    @property
    def fee_amount_str(self):
        if self.fee_wallet:
            return self.fee_wallet.currency.format_large(-self.fee_amount)
        return ""

    # notes
    notes = CharField(null=True, max_length=500)

    # from_txid
    from_txid = CharField(null=True, max_length=100)

    # to_txid
    to_txid = CharField(null=True, max_length=100)


class Pair(Model):
    class Meta:
        database = DB

    name = CharField(max_length=200, null=False)

    currency = ForeignKeyField(
        Currency, related_name='pair',
        null=False, on_update='CASCADE')

    ref_currency = ForeignKeyField(
        Currency, related_name='pair_ref',
        null=False, on_update='CASCADE')

    price_source = CharField(max_length=50, null=False)

    last_update = DateTimeField(null=False)


class Price(Model):
    class Meta:
        database = DB
        primary_key = CompositeKey('pair', 'date')

    pair = ForeignKeyField(
        Pair,
        null=False, on_update='CASCADE')

    date = DateField(null=False)

    price_open = FloatField(null=False)

    price_high = FloatField(null=False)

    price_low = FloatField(null=False)

    price_close = FloatField(null=False)


all_tables = [
    Currency, Wallet, Transaction, Pair, Price
]
