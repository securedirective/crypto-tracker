from peewee import *
from playhouse.migrate import MySQLMigrator, migrate


class DBWrapper(Proxy):
    def migrate_initial(self, migrator):
        migrate()

    def migrate_pair_add_last_update(self, migrator):
        migrate(
            migrator.add_column(
                'pair', 'last_update',
                IntegerField(null=False, default=0))
        )

    def apply_all_migrations(self):
        from .models import all_tables  # Late binding
        self.create_tables(
            all_tables,
            safe=True)

        applied_migrations = [x.name for x in DBMigration.select()]
        for m in dir(self):
            if m.startswith('migrate_'):
                if m not in applied_migrations:
                    print("Applying '%s'..." % m)
                    with self.transaction():
                        migrator = MySQLMigrator(self)
                        getattr(self, m)(migrator)
                    DBMigration.create(name=m)

DB = DBWrapper()


class DBMigration(Model):
    class Meta:
        database = DB

    name = CharField(max_length=200, null=False, primary_key=True)


class Currency(Model):
    class Meta:
        database = DB

    name = CharField(max_length=50, null=False)

    unit_large = CharField(max_length=20, null=False)

    unit_small = CharField(max_length=20, null=False)

    digits_after_decimal = IntegerField(null=False)

    usd_per_large = IntegerField(null=True, default=None)

    value_url = CharField(max_length=500, null=True, default=None)

    notes = CharField(max_length=500, null=True, default=None)

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

    location = CharField(max_length=50, null=True, default=None)

    protection = CharField(max_length=500, null=True, default=None)

    notes = CharField(max_length=500, null=True, default=None)

    public_key = CharField(max_length=500, null=True, default=None)


class Transaction(Model):
    class Meta:
        database = DB
        db_table = 'trans'

    # date_utc
    date_utc = DateTimeField(null=False)

    # trans_type
    INCOME = 'INC'
    TRANSFER = 'TRX'
    EXCHANGE = 'EXC'
    AIRDROP = 'AIR'
    trans_type_enum = {
        INCOME: "Income",
        TRANSFER: "Transfer",
        EXCHANGE: "Exchange",
        AIRDROP: "Airdrop",
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
        null=False, on_update='CASCADE')

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
    from_amount = BigIntegerField(null=True, default=None)

    @property
    def from_amount_str(self):
        if self.from_wallet:
            return self.from_wallet.currency.format_large(-self.from_amount)
        return ""

    # to_amount
    to_amount = BigIntegerField(null=False)

    @property
    def to_amount_str(self):
        if self.to_wallet:
            return self.to_wallet.currency.format_large(-self.to_amount)
        return ""

    # fee_amount
    fee_amount = BigIntegerField(null=True, default=None)

    @property
    def fee_amount_str(self):
        if self.fee_wallet:
            return self.fee_wallet.currency.format_large(-self.fee_amount)
        return ""

    # from_txid
    from_txid = CharField(null=True, max_length=100)

    # to_txid
    to_txid = CharField(null=True, max_length=100)

    # notes
    notes = CharField(null=True, default=None, max_length=500)


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
    DBMigration, Currency, Wallet, Transaction, Pair, Price
]
