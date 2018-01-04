# Built-ins
import os
import sys
import logging
try:
    import wx
except ImportError:
    raise ImportError("The wxPython module is required to run this program")

# Extra packages
from peewee import MySQLDatabase, SqliteDatabase, prefetch

# Our stuff
from config import Config
from database import *

DEBUG = False


def print_flush(s):
    print(s)
    sys.stdout.flush()


class MainWindow(wx.Frame):
    EXTERIOR_GAP = 14
    GAP = 10

    def __init__(self):
        super().__init__(None, -1, 'Crypto Tracker')

        self.database_connected = False
        self.sub_windows = []

        self.init_widgets()
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Maximize()
        self.Show()

        self.connect_to_database()
        self.populate_transaction_list()
        self.populate_wallet_list()
        self.populate_currency_list()

    def on_close(self, event):
        can_veto = event.CanVeto()
        visible_windows = 0
        asked = False
        quit_anyway = False

        for w in self.sub_windows:
            try:
                if w.IsShown() and can_veto:
                    if not asked:
                        quit_anyway = (wx.MessageBox("You still have sub-windows open. Quit anyway?", "Quit",
                                       wx.ICON_QUESTION | wx.YES_NO) == wx.YES)
                        asked = True
                    if quit_anyway:
                        w.Destroy()
                else:
                    w.Destroy()
            except Exception as e:
                if DEBUG:
                    print_flush(e)

        if asked and not quit_anyway:
            event.Veto()
            return

        self.Destroy()
        if DEBUG:
            print("Called Destroy()")

    # ======================================================================= #

    def init_widgets(self):
        mainsizer = wx.GridBagSizer(vgap=self.GAP, hgap=self.GAP)
        mainsizer.Add(
            self.init_transaction_panel(), pos=(0, 0), span=(1, 2),
            flag=wx.EXPAND)   # , flag=wx.SizerFlags().Expand())
        mainsizer.Add(self.init_wallet_panel(), pos=(1, 0), flag=wx.EXPAND)
        mainsizer.Add(self.init_currency_panel(), pos=(1, 1), flag=wx.EXPAND)
        mainsizer.AddGrowableRow(0)
        mainsizer.AddGrowableRow(1)
        mainsizer.AddGrowableCol(0)
        mainsizer.AddGrowableCol(1)

        perimeter = wx.BoxSizer(wx.VERTICAL)  # This one is to have a border
        perimeter.Add(
            mainsizer, proportion=1, border=self.EXTERIOR_GAP,
            flag=wx.EXPAND | wx.ALL)

        self.SetIcon(wx.Icon('app.png', wx.BITMAP_TYPE_PNG, 32, 32))
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_FRAMEBK))
        self.init_menu()
        self.init_statusbar()
        self.SetSizerAndFit(perimeter)

    def init_transaction_panel(self):
        buttonrow = wx.BoxSizer(wx.HORIZONTAL)
        self.lbl_transaction_count = wx.StaticText(self, label="# items")
        self.lbl_transaction_count.SetMinSize(wx.Size(70, -1))
        buttonrow.Add(
            self.lbl_transaction_count, proportion=1, border=5,
            flag=wx.ALIGN_BOTTOM | wx.LEFT)   # Expand to fill remaining space
        buttonrow.AddSpacer(self.GAP)
        b = wx.Button(self, label="Add")
        b.Bind(wx.EVT_BUTTON, self.add_transaction)
        buttonrow.Add(b, flag=wx.EXPAND)
        buttonrow.AddSpacer(self.GAP)
        buttonrow.Add(wx.Button(self, label="Edit"), flag=wx.EXPAND)
        buttonrow.AddSpacer(self.GAP)
        buttonrow.Add(wx.Button(self, label="Delete"), flag=wx.EXPAND)

        sizer = wx.StaticBoxSizer(wx.VERTICAL, self, "Transactions:")
        sizer.Add(buttonrow, flag=wx.EXPAND)
        sizer.AddSpacer(self.GAP)
        self.lst_transactions = wx.ListCtrl(
            self,
            style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES | wx.LC_VRULES)
        self.lst_transactions.InsertColumn(0, 'Date (utc)', width=150)
        self.lst_transactions.InsertColumn(1, 'Date (local)', width=150)
        self.lst_transactions.InsertColumn(2, 'Type', width=150)
        self.lst_transactions.InsertColumn(3, 'Wallets involved', width=280)
        self.lst_transactions.InsertColumn(4, 'Explanation of money movement', width=500)
        self.lst_transactions.InsertColumn(5, 'Notes', width=500)
        self.lst_transactions.SetMinSize(wx.Size(-1, 200))
        sizer.Add(self.lst_transactions, proportion=1, flag=wx.EXPAND)
        return sizer

    def init_wallet_panel(self):
        buttonrow = wx.BoxSizer(wx.HORIZONTAL)
        self.lbl_wallet_count = wx.StaticText(self, label="# items")
        self.lbl_wallet_count.SetMinSize(wx.Size(70, -1))
        buttonrow.Add(
            self.lbl_wallet_count, proportion=1, border=5,
            flag=wx.ALIGN_BOTTOM | wx.LEFT)   # Expand to fill remaining space
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
        buttonrow.Add(
            self.lbl_currency_count, proportion=1, border=5,
            flag=wx.ALIGN_BOTTOM | wx.LEFT)   # Expand to fill remaining space
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
        if DEBUG:
            print_flush(status)
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
            # DB.create_tables(
            #     ALL_TABLES,
            #     safe=True)
        else:
            raise Exception("Invalid DB_TYPE")
        # DB.connect()

        if False:
            from starter_data import add_starter_data
            add_starter_data()

        self.database_connected = True
        self.ready_status()

    def populate_transaction_list(self):
        self.update_status("Updating transactions...")

        # Hard-coded colors for various transaction types
        CLR_EXCHANGE = wx.Colour(255, 255, 206)     # Yellow
        CLR_INCOME = wx.Colour(198, 255, 198)       # Green
        CLR_EXPENSE = wx.Colour(255, 214, 193)      # Red
        CLR_ERROR = wx.Colour(255, 0, 0)        # Bright red

        # Query the database (come back to this later to make the queries more efficient)
        transactions = prefetch(
            # Main table to load:
            Transaction.select().order_by(Transaction.date),
            # Additional tables to prefetch:
            Wallet.select(),
            Currency.select(),
            DeterministicSeed.select(),
            Identity.select()
        )

        # Initialize the listbox
        self.lst_transactions.DeleteAllItems()
        new_index = None
        item_count = 0

        for t in transactions:
            # Show error in notes field if a transaction doesn't validate
            clr = None
            wallet_explanation = "?"
            money_explanation = "?"

            try:
                t.validate_fields()
                notes = t.notes or ""

                # The Wallet/Money columns are customized for the transaction type
                if t.trans_type == Transaction.TRANSFER:
                    wallet_explanation = t.from_wallet.str_short() + " --> " + t.to_wallet.str_short()
                    money_explanation = "Moved " + t.from_amount_str + ", with " + t.fee_amount_str + " fee"
                elif t.trans_type == Transaction.EXCHANGE:
                    clr = CLR_EXCHANGE
                    wallet_explanation = t.from_wallet.str_short() + " --> " + t.to_wallet.str_short()
                    money_explanation = "Exchanged " + t.from_amount_str + " for " + t.to_amount_str + ", with " + t.fee_amount_str + " fee"
                elif t.trans_type.startswith("INC-"):
                    clr = CLR_INCOME
                    wallet_explanation = t.to_wallet.str_short()
                    money_explanation = "Income of " + t.to_amount_str
                elif t.trans_type.startswith("EXP-"):
                    clr = CLR_EXPENSE
                    wallet_explanation = t.from_wallet.str_short()
                    money_explanation = "Expense of " + t.from_amount_str

            except Exception as e:
                notes = "EXCEPTION: " + str(e)
                clr = CLR_ERROR

            # Add the item to the listbox
            new_index = self.lst_transactions.Append((
                t.date_utc,
                t.date_local,
                t.trans_type,
                wallet_explanation,
                money_explanation,
                notes,
            ))
            if clr:
                self.lst_transactions.SetItemBackgroundColour(new_index, clr)

            item_count += 1

        # Scroll to the bottom
        if new_index:
            self.lst_transactions.EnsureVisible(new_index)

        # Update the label
        self.lbl_transaction_count.SetLabel("%s transactions" % item_count)

        self.ready_status()

    def populate_wallet_list(self):
        pass

    def populate_currency_list(self):
        pass

    def add_transaction(self, event):
        self.update_status("Button clicked")
        from edit_transaction_window import EditTransactionWindow
        self.show_sub_window(EditTransactionWindow(parent=self), False)
        self.ready_status()

    def show_sub_window(self, window, modal=True):
        self.sub_windows.append(window)
        if modal:
            window.ShowModal()
            window.Destroy()
            self.sub_windows.remove(window)
        else:
            window.Show(True)


if __name__ == "__main__":
    # Configure logging
    for arg in sys.argv:
        if arg.lower() == '-v':
            DEBUG = True
    logging.basicConfig(
        format='%(asctime)s %(levelname)s - %(message)s',
        level=logging.DEBUG if DEBUG else logging.WARNING
    )

    app = wx.App()
    # app = wx.App(redirect=True)   # Error messages go to popup window
    form = MainWindow()
    app.MainLoop()
