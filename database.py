from peewee import *
from datetime import datetime
import pytz

DB = Proxy()

local_time_zone = pytz.timezone("America/New_York")


class ValidationError(Exception):
    pass


class Currency(Model):
    class Meta:
        database = DB

    name = CharField(max_length=50, null=False)

    derivation_path = CharField(max_length=100, null=True)

    unit_large = CharField(max_length=20, null=False)

    unit_small = CharField(max_length=20, null=False)

    digits_after_decimal = IntegerField(null=False)

    usd_per_large = FloatField(null=True)

    notes = CharField(max_length=500, null=True)

    url_public_website = CharField(max_length=500, null=True)

    url_source_code = CharField(max_length=500, null=True)

    url_market_value = CharField(max_length=500, null=True)

    url_block_info = CharField(max_length=500, null=True)

    url_tx_info = CharField(max_length=500, null=True)

    url_addr_info = CharField(max_length=500, null=True)

    def format_large(self, small_amount):
        fmt = "{} {:." + str(self.digits_after_decimal) + "f}"
        return fmt.format(self.unit_large, small_amount / (10**self.digits_after_decimal))
        # dsh -0.02460000

    def format_small(self, small_amount):
        fmt = "{} {:<3}"
        return fmt.format(small_amount, self.unit_small)
        # -2460000 sat

    def __str__(self):
        return "Currency #%s" % self.id


class Identity(Model):
    class Meta:
        database = DB
        db_table = 'ident'

    name = CharField(max_length=50, null=False)

    notes = CharField(max_length=500, null=True)

    def __str__(self):
        return "Ident #%s" % self.id


class DeterministicSeed(Model):
    class Meta:
        database = DB
        db_table = 'seed'

    name = CharField(max_length=50, null=False)

    paper_local = CharField(max_length=500, null=True)

    paper_offsite_1 = CharField(max_length=500, null=True)

    paper_offsite_2 = CharField(max_length=500, null=True)

    level_of_trust = CharField(max_length=500, null=True)

    notes = CharField(max_length=500, null=True)

    identity = ForeignKeyField(
        Identity,
        null=False, on_update='CASCADE')

    def __str__(self):
        return "Seed #%s" % self.id


class Wallet(Model):
    class Meta:
        database = DB
        db_table = 'wallet'

    seed = ForeignKeyField(
        DeterministicSeed,
        null=False, on_update='CASCADE')

    currency = ForeignKeyField(
        Currency,
        null=False, on_update='CASCADE')

    passphrase = IntegerField(null=True)

    public_key = CharField(max_length=500, null=True)

    def __str__(self):
        return "Wallet #%s" % self.id

    def str_short(self):
        return "#%s(%s)" % (self.id, self.currency.unit_large)

    def str_long(self):
        t = "%s > %s > %s (%s)" % (self.identity.name, self.seed.name, self.currency.unit_large, self.currency.name)
        if self.passphrase:
            t += (" > Pw%s" % self.passphrase)
        return t


class Transaction(Model):
    class Meta:
        database = DB
        db_table = 'trans'
        constraints = [
            # Database constraints will ensure that every wallet reference is accompanied by an amount
            # It also verifies the +/- of the amount column
            Check('(from_wallet_id is null and from_amount is null) or (from_wallet_id is not null and from_amount < 0)'),
            Check('(to_wallet_id is null and to_amount is null) or (to_wallet_id is not null and to_amount > 0)'),
            Check('(fee_wallet_id is null and fee_amount is null) or (fee_wallet_id is not null and fee_amount < 0)'),
        ]

    # date (stored as UTC)
    date = DateTimeField(null=False)

    @property
    def date_utc(self):
        return self.date.replace(tzinfo=pytz.utc)

    @property
    def date_local(self):
        return self.date_utc.astimezone(local_time_zone)

    # trans_type
    trans_type = CharField(null=False, max_length=100)
    TRANSFER = "Transfer"
    EXCHANGE = "Exchange"
    INC_MINING = "INC-Mining"
    INC_AIRDROP = "INC-Airdrop/Fork"
    INC_GIFT = "INC-Gift"
    EXP_PURCHASE = "EXP-Purchase"
    EXP_GIFT = "EXP-Gift"
    must_have_from_and_to = [TRANSFER, EXCHANGE]
    may_not_have_fee = [INC_MINING, INC_AIRDROP, INC_GIFT]
    all_trans_types = [TRANSFER, EXCHANGE, INC_MINING, INC_AIRDROP, INC_GIFT, EXP_PURCHASE, EXP_GIFT]

    # from_wallet
    from_wallet = ForeignKeyField(
        Wallet, related_name='transaction_from',
        null=True, on_update='CASCADE')

    @property
    def from_wallet_str(self):
        if self.from_wallet:
            return self.from_wallet.str_short()
        return ""

    # to_wallet
    to_wallet = ForeignKeyField(
        Wallet, related_name='transaction_to',
        null=True, on_update='CASCADE')

    @property
    def to_wallet_str(self):
        if self.to_wallet:
            return self.to_wallet.str_short()
        return ""

    # fee_wallet
    fee_wallet = ForeignKeyField(
        Wallet, related_name='transaction_fee',
        null=True, on_update='CASCADE')

    @property
    def fee_wallet_str(self):
        if self.fee_wallet:
            return self.fee_wallet.str_short()
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
            return self.to_wallet.currency.format_large(self.to_amount)
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

    # Must call this manually, since PeeWee doesn't support field validation
    def validate_fields(self):
        if self.trans_type in Transaction.must_have_from_and_to:
            if self.from_wallet is None or self.to_wallet is None:
                raise ValidationError("Transaction type %s must have both a from and a to wallet")
        else:
            if self.from_wallet is not None and self.to_wallet is not None:
                raise ValidationError("Transaction type %s may not have both a from and a to wallet")
        if self.trans_type in Transaction.may_not_have_fee:
            if self.fee_wallet is not None:
                raise ValidationError("Transaction type %s may not have a fee specified")

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

    def __str__(self):
        return "Tx #%s" % self.id


class Pair(Model):
    class Meta:
        database = DB
        db_table = 'pair'

    name = CharField(max_length=200, null=False)

    currency = ForeignKeyField(
        Currency, related_name='pair',
        null=False, on_update='CASCADE')

    ref_currency = ForeignKeyField(
        Currency, related_name='pair_ref',
        null=False, on_update='CASCADE')

    price_source = CharField(max_length=50, null=False)

    last_update = DateTimeField(null=False)

    def __str__(self):
        return "Pair #%s" % self.id


class Price(Model):
    class Meta:
        database = DB
        db_table = 'price'
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

    def __str__(self):
        return "Price #%s" % self.id


ALL_TABLES = [
    Currency, DeterministicSeed, Identity, Wallet, Transaction, Pair, Price
]
