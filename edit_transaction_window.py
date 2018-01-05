# Built-ins
import wx

# Our stuff
from database import *
from common import *


# class DateValidator(wx.Validator):
#     def __init__(self):
#         super().__init__()

#     def Clone(self):
#         return DateValidator()

#     def TransferToWindow(self):
#         return True  # Prevent wxDialog from complaining.

#     def TransferFromWindow(self):
#         return True  # Prevent wxDialog from complaining.

#     def Validate(self, parent):
#         t = self.GetWindow()
#         v = t.GetValue()
#         if v and (v != 'a'):
#             wx.MessageBox("Invalid date")
#             t.SetFocus()
#             return False
#         return True


class EditTransactionWindow(wx.Dialog):
    EXTERIOR_GAP = 14
    GAP = 10

    def __init__(self, parent, trans=None):
        title = "Edit Transaction" if trans else "Add Transaction"
        super().__init__(parent=parent, title=title, size=wx.Size(1000, 1000),
                         style=wx.CAPTION | wx.CLOSE_BOX | wx.RESIZE_BORDER)

        self.wallet_combos = []
        self.init_gui()

    def init_gui(self):
        with Wrapper(wx.BoxSizer(wx.VERTICAL)) as perimeter:
            # Main area
            with Wrapper(wx.FlexGridSizer(cols=2, vgap=self.GAP, hgap=self.GAP)) as mainarea:
                mainarea.AddGrowableCol(0, proportion=0)
                mainarea.AddGrowableCol(1, proportion=1)

                # Top row
                mainarea.Add(wx.StaticText(self, label='Date (UTC):'))
                with Wrapper(wx.BoxSizer(wx.HORIZONTAL)) as s:
                    s.Add(wx.TextCtrl(self), proportion=0.5, flag=wx.EXPAND)

                    s.Add(wx.StaticText(self, label='Date (local):'), proportion=0.5, flag=wx.EXPAND | wx.LEFT, border=self.GAP)

                    s.Add(wx.TextCtrl(self), proportion=0.5, flag=wx.EXPAND | wx.LEFT, border=self.GAP)

                    s.Add(wx.StaticText(self, label='Type:'), flag=wx.EXPAND | wx.LEFT, border=self.GAP)

                    self.cb_trans_type = wx.ComboBox(self, style=wx.CB_READONLY, choices=Transaction.all_trans_types)
                    s.Add(self.cb_trans_type, proportion=1, flag=wx.EXPAND | wx.LEFT, border=self.GAP)
                mainarea.Add(s, flag=wx.EXPAND)

                # Inputs/outputs
                subitems = ['From wallet:', 'To wallet:', 'Fee wallet:']
                for subitem in subitems:
                    mainarea.Add(wx.StaticText(self, label=subitem))

                    with Wrapper(wx.BoxSizer(wx.HORIZONTAL)) as s:
                        cb = wx.ComboBox(self, style=wx.CB_READONLY)
                        cb.Bind(wx.EVT_COMBOBOX, self.choose_wallet, id=0)
                        s.Add(cb, flag=wx.EXPAND)
                        self.wallet_combos.append(cb)

                        s.Add(wx.StaticText(self, label='Amount:'), flag=wx.EXPAND | wx.LEFT, border=self.GAP)

                        s.Add(wx.TextCtrl(self), flag=wx.EXPAND | wx.LEFT, border=self.GAP)

                        s.Add(wx.StaticText(self, label='Tx ID:'), flag=wx.EXPAND | wx.LEFT, border=self.GAP)

                        s.Add(wx.TextCtrl(self), proportion=1, flag=wx.EXPAND | wx.LEFT, border=self.GAP)
                    mainarea.Add(s, flag=wx.EXPAND)

                # Populate all the combo boxes in one step
                self.populate_wallet_lists()

                # Notes row
                mainarea.Add(wx.StaticText(self, label='Notes:'))
                mainarea.Add(wx.TextCtrl(self), flag=wx.EXPAND)
            perimeter.Add(mainarea, proportion=1, flag=wx.EXPAND | wx.ALL, border=self.GAP)

            # Button row
            buttonrow = self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL)
            perimeter.Add(buttonrow, proportion=0, flag=wx.EXPAND | wx.ALL, border=self.EXTERIOR_GAP)
        self.SetSizerAndFit(perimeter)

    def choose_wallet(self, id):
        # chosen_wallet[id] =
        msg("")

    def populate_wallet_lists(self):
        wallets = list(prefetch(
            # Main table to load:
            Wallet.select(),
            # Additional tables to prefetch:
            Currency.select(),
            DeterministicSeed.select(),
            Identity.select()
        ))
        for w in wallets:
            for cb in self.wallet_combos:
                new_indox = cb.Append(w.str_long())

    def OnClose(self, e):
        self.Destroy()
