# Built-ins
import wx

# Extra packages
from peewee import MySQLDatabase, SqliteDatabase, prefetch

# Our stuff
from config import Config
from common import *
from database import *
from edit_transaction_window import EditTransactionWindow


class MainWindow(wx.Frame):
    EXTERIOR_GAP = 14
    GAP = 10

    def __init__(self):
        super().__init__(None, -1, 'Crypto Tracker')

        self.database_connected = False
        self.sub_windows = []

        self.init_gui()

        self.connect_to_database()
        self.populate_transaction_list()
        self.populate_wallet_list()
        self.populate_currency_list()

        # self.Maximize()
        self.SetSize(1950, 100, 1850, 1000)
        self.lst_transactions.SetFocus()
        self.Show()

        # self.add_transaction()

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
                                       wx.ICON_QUESTION | wx.YES_NO | wx.CENTRE) == wx.YES)
                        asked = True
                    if quit_anyway:
                        w.Destroy()
                else:
                    w.Destroy()
            except Exception as e:
                if Config.DEBUG:
                    print_flush(e)

        if asked and not quit_anyway:
            event.Veto()
            return

        self.Destroy()
        if Config.DEBUG:
            print("Called Destroy()")

    # ======================================================================= #

    def init_gui(self):
        # Generic stuff about the window
        self.SetIcon(wx.Icon('app.png', wx.BITMAP_TYPE_PNG, 32, 32))
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_FRAMEBK))
        self.Bind(wx.EVT_CLOSE, self.on_close)

        # Status bar
        self.status_bar = self.CreateStatusBar(number=4, style=wx.STB_SIZEGRIP)

        # Main area with a border
        with Wrapper(wx.BoxSizer(wx.VERTICAL)) as perimeter:
            with Wrapper(wx.GridBagSizer(vgap=self.GAP, hgap=self.GAP)) as mainsizer:
                ####################################################################################
                # Transactions
                ####################################################################################
                with Wrapper(wx.StaticBoxSizer(wx.VERTICAL, self, "Transactions:")) as sizer:
                    with Wrapper(wx.BoxSizer(wx.HORIZONTAL)) as buttonrow:
                        self.lbl_transaction_count = wx.StaticText(self)
                        self.lbl_transaction_count.SetMinSize(wx.Size(70, -1))
                        buttonrow.Add(self.lbl_transaction_count, proportion=1, flag=wx.ALIGN_BOTTOM | wx.LEFT, border=5)

                        buttonrow.AddSpacer(self.GAP)

                        b = wx.Button(self, label="Add")
                        b.Bind(wx.EVT_BUTTON, self.add_transaction)
                        buttonrow.Add(b, flag=wx.EXPAND)

                        buttonrow.AddSpacer(self.GAP)

                        buttonrow.Add(wx.Button(self, label="Edit"), flag=wx.EXPAND)

                        buttonrow.AddSpacer(self.GAP)

                        buttonrow.Add(wx.Button(self, label="Delete"), flag=wx.EXPAND)

                        buttonrow.AddSpacer(self.GAP * 4)

                        b = wx.Button(self, label="Refresh")
                        b.Bind(wx.EVT_BUTTON, self.populate_transaction_list)
                        buttonrow.Add(b, flag=wx.EXPAND)
                    sizer.Add(buttonrow, flag=wx.EXPAND)

                    sizer.AddSpacer(self.GAP)

                    self.lst_transactions = CustomListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES | wx.LC_VRULES)
                    self.lst_transactions.bulk_add_columns('Date (utc)', 'Date (local)', 'Type', 'Wallets involved', 'Explanation of money movement', 'Notes')
                    self.lst_transactions.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.edit_transaction)
                    sizer.Add(self.lst_transactions, proportion=1, flag=wx.EXPAND)
                mainsizer.Add(sizer, pos=(0, 0), span=(1, 2), flag=wx.EXPAND)

                ####################################################################################
                # Wallets
                ####################################################################################
                with Wrapper(wx.StaticBoxSizer(wx.VERTICAL, self, "Wallets:")) as sizer:
                    with Wrapper(wx.BoxSizer(wx.HORIZONTAL)) as buttonrow:
                        self.lbl_wallet_count = wx.StaticText(self)
                        self.lbl_wallet_count.SetMinSize(wx.Size(70, -1))
                        buttonrow.Add(self.lbl_wallet_count, proportion=1, flag=wx.ALIGN_BOTTOM | wx.LEFT, border=5)

                        buttonrow.AddSpacer(self.GAP)

                        b = wx.Button(self, label="Refresh")
                        b.Bind(wx.EVT_BUTTON, self.populate_wallet_list)
                        buttonrow.Add(b, flag=wx.EXPAND)
                    sizer.Add(buttonrow, flag=wx.EXPAND)

                    sizer.AddSpacer(self.GAP)

                    self.lst_wallets = CustomListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES | wx.LC_VRULES)
                    self.lst_wallets.bulk_add_columns('Description', 'Level of trust')
                    sizer.Add(self.lst_wallets, proportion=1, flag=wx.EXPAND)
                mainsizer.Add(sizer, pos=(1, 0), flag=wx.EXPAND)

                ####################################################################################
                # Currencies
                ####################################################################################
                with Wrapper(wx.StaticBoxSizer(wx.VERTICAL, self, "Currencies:")) as sizer:
                    with Wrapper(wx.BoxSizer(wx.HORIZONTAL)) as buttonrow:
                        self.lbl_currency_count = wx.StaticText(self)
                        self.lbl_currency_count.SetMinSize(wx.Size(70, -1))
                        buttonrow.Add(self.lbl_currency_count, proportion=1, flag=wx.ALIGN_BOTTOM | wx.LEFT, border=5)

                        buttonrow.AddSpacer(self.GAP)

                        b = wx.Button(self, label="Refresh")
                        b.Bind(wx.EVT_BUTTON, self.populate_currency_list)
                        buttonrow.Add(b, flag=wx.EXPAND)
                    sizer.Add(buttonrow, flag=wx.EXPAND)

                    sizer.AddSpacer(self.GAP)

                    self.lst_currencies = CustomListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES | wx.LC_VRULES)
                    self.lst_currencies.bulk_add_columns('Symbol', 'Name', 'Derivation path', 'Notes')
                    sizer.Add(self.lst_currencies, proportion=1, flag=wx.EXPAND)
                mainsizer.Add(sizer, pos=(1, 1), flag=wx.EXPAND)

                mainsizer.AddGrowableRow(0)
                mainsizer.AddGrowableRow(1)
                mainsizer.AddGrowableCol(0)
                mainsizer.AddGrowableCol(1)
            perimeter.Add(mainsizer, proportion=1, flag=wx.EXPAND | wx.ALL, border=self.EXTERIOR_GAP)
        self.SetSizerAndFit(perimeter)

    # ======================================================================= #

    def update_status(self, status):
        if Config.DEBUG:
            print_flush(status)
        self.status_bar.SetStatusText(status, 0)

    def ready_status(self):
        self.update_status("Ready")

    def connect_to_database(self):
        self.update_status("Connecting to database...")

        if Config.DB_TYPE == 'sqlite':
            DB.initialize(SqliteDatabase(Config.DB_NAME))
            DB.create_tables(ALL_TABLES, safe=True)
        elif Config.DB_TYPE == 'mysql':
            DB.initialize(MySQLDatabase(
                Config.DB_NAME,
                host=Config.DB_HOST,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD
            ))
            DB.create_tables(ALL_TABLES, safe=True)
        else:
            raise Exception("Invalid DB_TYPE")

        if False:
            from starter_data import add_starter_data
            add_starter_data()

        self.database_connected = True
        self.ready_status()

    def populate_transaction_list(self, event=None):
        self.update_status("Updating transactions...")

        # Hard-coded colors for various transaction types
        CLR_EXCHANGE = wx.Colour(255, 255, 206)     # Yellow
        CLR_INCOME = wx.Colour(198, 255, 198)       # Green
        CLR_EXPENSE = wx.Colour(255, 214, 193)      # Red
        CLR_ERROR = wx.Colour(255, 0, 0)        # Bright red

        # Query the database (come back to this later to make the queries more efficient)
        self.transaction_list = prefetch(
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

        for t in self.transaction_list:
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
            self.lst_transactions.SetItemData(new_index, t.id)
            if clr:
                self.lst_transactions.SetItemBackgroundColour(new_index, clr)
            item_count += 1

        # Scroll to the bottom
        if new_index:
            self.lst_transactions.EnsureVisible(new_index)
            self.lst_transactions.SetItemState(new_index, wx.LIST_STATE_FOCUSED, wx.LIST_STATE_FOCUSED)

        # Autosize all the columns
        self.lst_transactions.autosize_all_columns()

        # Update the label
        self.lbl_transaction_count.SetLabel("%s transactions" % item_count)

        self.ready_status()

    def populate_wallet_list(self, event=None):
        self.update_status("Updating wallets...")

        # Query the database (come back to this later to make the queries more efficient)
        self.wallet_list = prefetch(
            # Main table to load:
            Wallet.select(),
            # Additional tables to prefetch:
            Currency.select(),
            DeterministicSeed.select(),
            Identity.select()
        )

        # Initialize the listbox
        self.lst_wallets.DeleteAllItems()
        item_count = 0

        for w in self.wallet_list:
            # Add the item to the listbox
            new_index = self.lst_wallets.Append((
                w.str_long(),
                w.seed.level_of_trust,
            ))
            self.lst_wallets.SetItemData(new_index, w.id)
            item_count += 1

        # def fs(item1, item2):
        #     print(item1, item2)
        #     return (item1 > item2) - (item1 < item2)

        # self.lst_wallets.SortItems(fs)

        # Autosize all the columns
        self.lst_wallets.autosize_all_columns()

        # Update the label
        self.lbl_wallet_count.SetLabel("%s wallets" % item_count)

        self.ready_status()

    def populate_currency_list(self, event=None):
        self.update_status("Updating currencies...")

        # Query the database (come back to this later to make the queries more efficient)
        self.currency_list = Currency.select().order_by(Currency.name)

        # Initialize the listbox
        self.lst_currencies.DeleteAllItems()
        item_count = 0

        for c in self.currency_list:
            # Add the item to the listbox
            new_index = self.lst_currencies.Append((
                c.symbol,
                c.name,
                c.derivation_path,
                c.notes,
            ))
            self.lst_currencies.SetItemData(new_index, c.id)
            item_count += 1

        # Autosize all the columns
        self.lst_currencies.autosize_all_columns()

        # Update the label
        self.lbl_currency_count.SetLabel("%s currencies" % item_count)

        self.ready_status()

    def edit_transaction(self, event):
        try:
            t = Transaction.get(id=event.Item.GetData())
        except Exception as e:
            return False
        self.show_sub_window(EditTransactionWindow(parent=self, wallet_list=self.wallet_list, instance=t), False)
        self.ready_status()

    def add_transaction(self, event):
        self.update_status("Button clicked")
        self.show_sub_window(EditTransactionWindow(parent=self, wallet_list=self.wallet_list), False)
        self.ready_status()

    def show_sub_window(self, window, modal=True):
        self.sub_windows.append(window)
        if modal:
            window.ShowModal()
            window.Destroy()
            self.sub_windows.remove(window)
        else:
            window.Show(True)
