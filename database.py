from peewee import *

DB = Proxy()


class ValidationError(Exception):
    pass

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
        constraints = [
            Check('(from_wallet_id is null and from_amount is null) or (from_wallet_id is not null and from_amount < 0)'),
            Check('(to_wallet_id is null and to_amount is null) or (to_wallet_id is not null and to_amount > 0)'),
            Check('(fee_wallet_id is null and fee_amount is null) or (fee_wallet_id is not null and fee_amount < 0)'),
        ]

    # date_utc
    date_utc = DateTimeField(null=False)

    # trans_type
    TRANS_TYPES = ["Gift", "Income", "Airdrop", "Transfer", "Exchange"]
    trans_type = IntegerField(null=False)

    @property
    def trans_type_str(self):
        return Transaction.TRANS_TYPES[self.trans_type]

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

    # def validate_fields(self):
    #     if self.trans_type < 0 or self.trans_type >= len(Transaction.TRANS_TYPES):
    #         raise ValidationError("Unknown trans_type: %s" % self.trans_type)

    # # Overload the function so we can validate fields
    # def save(self, force_insert=False, only=None):
        
    # # Overload the function so we can validate fields
    # def update(self, __data=None, **update):
    #     self.validate_fields()
    #     return super().update(__data, **update)

    # # Overload the function so we can validate fields
    # def insert(self, __data=None, **insert):
    #     self.validate_fields()
    #     return super().insert(__data, **insert)


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
        constraints = [
            SQL('UNIQUE (pair_id, date)'),
        ]

    pair = ForeignKeyField(
        Pair,
        null=False, on_update='CASCADE')

    date = DateField(null=False)

    price_open = FloatField(null=False)

    price_high = FloatField(null=False)

    price_low = FloatField(null=False)

    price_close = FloatField(null=False)


ALL_TABLES = [
    Currency, Wallet, Transaction, Pair, Price
]
