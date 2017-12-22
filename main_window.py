import os
import sys
import logging
from peewee import MySQLDatabase, SqliteDatabase, prefetch

from config import Config
from database import *

try:
    import wx
except ImportError:
    raise ImportError("The wxPython module is required to run this program")

DEBUG = True
VERBOSE = False


class MainForm(wx.Frame):
    EXTERIOR_GAP = 14
    GAP = 10

    database_connected = False

    def __init__(self):
        super().__init__(None, -1, 'Crypto Tracker')

        self.init_widgets()
        self.Show(True)

        self.connect_to_database()
        self.update_transaction_list()

    # ======================================================================= #

    def init_widgets(self):
        mainsizer = wx.GridBagSizer(vgap=self.GAP, hgap=self.GAP)
        mainsizer.Add(self.init_transaction_panel(), pos=(0, 0), span=(1, 2), flag=wx.EXPAND)   # , flag=wx.SizerFlags().Expand())
        mainsizer.Add(self.init_wallet_panel(), pos=(1, 0), flag=wx.EXPAND)
        mainsizer.Add(self.init_currency_panel(), pos=(1, 1), flag=wx.EXPAND)
        mainsizer.AddGrowableRow(0)
        mainsizer.AddGrowableRow(1)
        mainsizer.AddGrowableCol(0)
        mainsizer.AddGrowableCol(1)

        perimeter = wx.BoxSizer(wx.VERTICAL)  # This one is to have a border
        perimeter.Add(mainsizer, proportion=1, flag=wx.EXPAND | wx.ALL, border=self.EXTERIOR_GAP)

        self.SetIcon(wx.Icon('app.png', wx.BITMAP_TYPE_PNG, 32, 32))
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_FRAMEBK))
        self.init_menu()
        self.init_statusbar()
        self.SetSizerAndFit(perimeter)

    def init_transaction_panel(self):
        buttonrow = wx.BoxSizer(wx.HORIZONTAL)
        self.lbl_transaction_count = wx.StaticText(self, label="# items")
        self.lbl_transaction_count.SetMinSize(wx.Size(70, -1))
        buttonrow.Add(self.lbl_transaction_count, proportion=1, flag=wx.ALIGN_BOTTOM)   # Expand to fill remaining space
        buttonrow.AddSpacer(self.GAP)
        buttonrow.Add(wx.Button(self, label="Add"), flag=wx.EXPAND)
        buttonrow.AddSpacer(self.GAP)
        buttonrow.Add(wx.Button(self, label="Edit"), flag=wx.EXPAND)
        buttonrow.AddSpacer(self.GAP)
        buttonrow.Add(wx.Button(self, label="Delete"), flag=wx.EXPAND)

        sizer = wx.StaticBoxSizer(wx.VERTICAL, self, "Transactions:")
        sizer.Add(buttonrow, flag=wx.EXPAND)
        sizer.AddSpacer(self.GAP)
        self.lst_transactions = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES | wx.LC_VRULES)
        self.lst_transactions.InsertColumn(0, 'Type', width=100)
        self.lst_transactions.InsertColumn(1, 'Date', width=150)
        self.lst_transactions.InsertColumn(2, 'From', width=200)
        self.lst_transactions.InsertColumn(3, 'To', width=200)
        self.lst_transactions.InsertColumn(4, 'Notes', width=300)
        self.lst_transactions.SetMinSize(wx.Size(-1, 200))
        sizer.Add(self.lst_transactions, proportion=1, flag=wx.EXPAND)
        return sizer

    def init_wallet_panel(self):
        buttonrow = wx.BoxSizer(wx.HORIZONTAL)
        self.lbl_wallet_count = wx.StaticText(self, label="# items")
        self.lbl_wallet_count.SetMinSize(wx.Size(70, -1))
        buttonrow.Add(self.lbl_wallet_count, proportion=1, flag=wx.ALIGN_BOTTOM)   # Expand to fill remaining space
        buttonrow.AddSpacer(self.GAP)
        buttonrow.Add(wx.Button(self, label="Add"), flag=wx.EXPAND)
        buttonrow.AddSpacer(self.GAP)
        buttonrow.Add(wx.Button(self, label="Edit"), flag=wx.EXPAND)
        buttonrow.AddSpacer(self.GAP)
        buttonrow.Add(wx.Button(self, label="Delete"), flag=wx.EXPAND)

        sizer = wx.StaticBoxSizer(wx.VERTICAL, self, "Wallets:")
        sizer.Add(buttonrow, flag=wx.EXPAND)
        sizer.AddSpacer(self.GAP)
        self.lst_wallets = wx.ListBox(self)
        self.lst_wallets.SetMinSize(wx.Size(-1, 200))
        sizer.Add(self.lst_wallets, proportion=1, flag=wx.EXPAND)
        return sizer

    def init_currency_panel(self):
        buttonrow = wx.BoxSizer(wx.HORIZONTAL)
        self.lbl_currency_count = wx.StaticText(self, label="# items")
        self.lbl_currency_count.SetMinSize(wx.Size(70, -1))
        buttonrow.Add(self.lbl_currency_count, proportion=1, flag=wx.ALIGN_BOTTOM)   # Expand to fill remaining space
        buttonrow.AddSpacer(self.GAP)
        buttonrow.Add(wx.Button(self, label="Add"), flag=wx.EXPAND)
        buttonrow.AddSpacer(self.GAP)
        buttonrow.Add(wx.Button(self, label="Edit"), flag=wx.EXPAND)
        buttonrow.AddSpacer(self.GAP)
        buttonrow.Add(wx.Button(self, label="Delete"), flag=wx.EXPAND)

        sizer = wx.StaticBoxSizer(wx.VERTICAL, self, "Currencies:")
        sizer.Add(buttonrow, flag=wx.EXPAND)
        sizer.AddSpacer(self.GAP)
        self.lst_currencies = wx.ListBox(self)
        self.lst_currencies.SetMinSize(wx.Size(-1, 200))
        sizer.Add(self.lst_currencies, proportion=1, flag=wx.EXPAND)
        return sizer

    def init_menu(self):
        menuBar = wx.MenuBar()

        menu = wx.Menu()
        m_exit = menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Close window and exit program.")
        menuBar.Append(menu, "&File")

        menu = wx.Menu()
        m_about = menu.Append(wx.ID_ABOUT, "&About", "Information about this program")
        menuBar.Append(menu, "&Help")

        self.SetMenuBar(menuBar)

    def init_statusbar(self):
        self.status_bar = self.CreateStatusBar(number=4, style=wx.STB_SIZEGRIP)

    # ======================================================================= #

    def update_status(self, status):
        print(status)
        sys.stdout.flush()
        self.status_bar.SetStatusText(status, 0)

    def ready_status(self):
        self.update_status("Ready")

    def connect_to_database(self):
        self.update_status("Connecting to database...")

        if Config.DB_TYPE == 'sqlite':
            DB.initialize(SqliteDatabase(
                Config.DB_NAME
            ))
            DB.create_tables(
                ALL_TABLES,
                safe=True)
        elif Config.DB_TYPE == 'mysql':
            DB.initialize(MySQLDatabase(
                Config.DB_NAME,
                host=Config.DB_HOST,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD
            ))
        else:
            raise Exception("Invalid DB_TYPE")
        # DB.connect()

        if False:
            from starter_data import add_starter_data
            add_starter_data()

        self.database_connected = True
        self.ready_status()

    def update_transaction_list(self):
        self.update_status("Updating transactions...")

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
            self.lst_transactions.Append((
                t.trans_type_str,
                t.date_utc,
                t.from_wallet_str,
                t.to_wallet_str,
                t.notes,
            ))

        self.ready_status()


if __name__ == "__main__":
    # Configure logging
    for arg in sys.argv:
        if arg.lower() == '-v':
            VERBOSE = True
    logging.basicConfig(
        format='%(asctime)s %(levelname)s - %(message)s',
        level=logging.DEBUG if VERBOSE else logging.WARNING
    )

    app = wx.App()
    # app = wx.App(redirect=True)   # Error messages go to popup window
    form = MainForm()
    app.MainLoop()
