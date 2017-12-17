import os
import sys
import datetime
import time
import signal
import logging
from peewee import MySQLDatabase, SqliteDatabase, prefetch

import exchanges.kraken as krakenex
from config import Config
from cryptodb import *


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
                    'since':
                        int(pair.last_update.timestamp())
                        if pair.last_update else 0,
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
                        Price.pair == pair,
                        Price.date == datetime.date.fromtimestamp(row[0]),
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
                    price.save()  # only=price.dirty_fields)

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


if __name__ == "__main__":
    # # Configure logging
    # verbose = False
    # for arg in sys.argv:
    #     if arg.lower() == '-v':
    #         verbose = True
    # logging.basicConfig(
    #     format='%(asctime)s %(levelname)s - %(message)s',
    #     level=logging.DEBUG if verbose else logging.WARNING
    # )

    # # Connect to database
    # if Config.DB_TYPE == 'sqlite':
    #     DB.initialize(SqliteDatabase(
    #         Config.DB_NAME
    #     ))
    # elif Config.DB_TYPE == 'mysql':
    #     DB.initialize(MySQLDatabase(
    #         Config.DB_NAME,
    #         host=Config.DB_HOST,
    #         user=Config.DB_USER,
    #         password=Config.DB_PASSWORD
    #     ))
    # else:
    #     raise Exception("Invalid DB_TYPE")
    # DB.connect()
    # # DB.apply_all_migrations()

    # Start main form
    from forms.main import MainForm
    form = MainForm()
    form.mainloop()
