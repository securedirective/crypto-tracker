import os
import sys
import datetime
import time
import signal
import logging
from peewee import MySQLDatabase, prefetch

import exchanges.kraken as krakenex
from config import Config
from cryptodb import *


def show_transactions():
    # We have to use prefetch here because PeeWee's optimization only
    # recognizes the first FK to wallet. The second and third link cause N+2
    # additional queries to wallet table.
    # But by using prefetch, we lose the ability to use the SQL WHERE clause
    # on wallet attributes (for example obtaining only BCH transactions). We'll
    # have to do this on the Python side instead.
    transactions = prefetch((
        Transaction.select()
        # Transaction.select(Transaction, Wallet)
        # .join(Wallet)
        # .order_by(Transaction.date_utc)
    ), (
        Wallet.select()
    ), (
        Currency.select()
    ))
    for t in transactions:
        print('{date!s:<19} | {trans_type:<8} | {from_wallet:<18}{from_amount:>16} | {to_wallet:<18}{to_amount:>16} | {notes}'.format(
            date=t.date_utc, trans_type=t.trans_type_str,
            notes=t.notes,
            from_wallet=t.from_wallet_str,
            from_amount=t.from_amount_str,
            to_wallet=t.to_wallet_str,
            to_amount=t.to_amount_str,
            ))


def show_balances():
    pass


def kraken_get_pairs():
    k = krakenex.API(key=Config.KRAKEN_API_KEY)

    ret = k.query_public('AssetPairs', data={
        'info': 'fees',
    })
    if ret['error']:
        logger.ERROR(ret['error'])
    else:
        for pair, info in ret['result'].items():
            print(pair)


def kraken_update_prices():
    pairs = Pair.select().where(Pair.price_source == "Kraken")

    print("Existing status:")
    for pair in pairs:
        print("- %s: %s" % (pair.name, pair.last_update))
    reupdate_time = datetime.datetime.now() - datetime.timedelta(days=2)

    for pair in pairs:
        if pair.last_update and pair.last_update > reupdate_time:
            continue

        print("------------------------------------")
        print("Updating '%s'..." % pair.name)
        sys.stdout.flush()

        with DB.transaction():
            try:
                k = krakenex.API(key=Config.KRAKEN_API_KEY)
                ret = k.query_public('OHLC', data={
                    'pair': pair.name,
                    'interval': 1440,   # Per day
                    'since': int(pair.last_update.timestamp()) if pair.last_update else 0,
                }, timeout=30)

                data = ret['result'][pair.name]
                # limit = len(data)-2
                # i = 0
                for row in data:
                    # if i > limit:
                    #     break
                    print("Checking if it exists...")
                    input()
                    price = Price.select().where(
                        Price.pair==pair,
                        Price.date==datetime.date.fromtimestamp(row[0]),
                    ).limit(1)

                    if len(price) == 1:
                        print("Yes")
                        input()
                        price = price[0]
                    else:
                        print("No")
                        input()
                        price = Price(
                            pair=pair,
                            date=datetime.date.fromtimestamp(row[0]),
                        )
                    print("Updating")
                    input()
                    price.price_open = float(row[1])
                    price.price_high = float(row[2])
                    price.price_low = float(row[3])
                    price.price_close = float(row[4])
                    print("Saving (if dirty)")
                    input()
                    price.save() #only=price.dirty_fields)

                    # price = Price()
                    # price.pair = pair
                    # price.date = datetime.date.fromtimestamp(row[0])
                    # price.price_open = float(row[1])
                    # price.price_high = float(row[2])
                    # price.price_low = float(row[3])
                    # price.price_close = float(row[4])
                    # price.save()
                    # i += 1

                pair.last_update = datetime.datetime.fromtimestamp(
                    ret['result']['last'])
                pair.save()
            except Exception as e:
                logging.error("Failed to update '%s': %s", pair.name, e)

    print("New status:")
    for pair in pairs:
        print("- %s: %s" % (pair.name, pair.last_update))


def add_transaction():
    from forms.add_transaction import AddTransactionForm
    form = AddTransactionForm()
    form.mainloop()


if __name__ == "__main__":
    # Configure logging
    verbose = False
    for arg in sys.argv:
        if arg.lower() == '-v':
            verbose = True
    logging.basicConfig(
        format='%(asctime)s %(levelname)s - %(message)s',
        level=logging.DEBUG if verbose else logging.WARNING
    )

    # Connect to database
    db_config = MySQLDatabase(
        Config.DB_NAME,
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD
    )
    DB.initialize(db_config)
    DB.connect()
    DB.apply_all_migrations()

    # Import starter data (CAREFUL!)
    if False:
        from cryptodb.starter_data import StarterData
        StarterData.import_data()
        print("Added starter data")

    # Initialize menu
    menu = [
        ('p', 'Kraken: Pull latest prices for all pairs', kraken_update_prices),
        ('c', 'Kraken: Query all available currency pairs', kraken_get_pairs),
        ('t', 'Show transactions', show_transactions),
        ('b', 'Show balances', show_balances),
        ('a', 'Add transaction', add_transaction),
    ]
    while True:
        print('-------------------------------------')
        for m in menu:
            print("%s: %s" % (m[0].upper(), m[1]))
        # k = input()
        k = 'a'
        print('-------------------------------------')
        sys.stdout.flush()
        for m in menu:
            if m[0] == k:
                logging.info("User selected '%s: %s'", m[0].upper(), m[1])
                func = m[2]
                # try:
                func()
                # except Exception as e:
                #     print('--------------- ERROR ---------------')
                #     print(e)
                continue
        print('')
        break   # TEMP
