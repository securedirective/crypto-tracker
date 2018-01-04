# Built-ins
import wx

# Our stuff
from database import *


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

        self.init_widgets()

    def init_widgets(self):
        perimeter = wx.BoxSizer(wx.VERTICAL)

        # Main area
        controlsizer = wx.FlexGridSizer(cols=2, vgap=self.GAP, hgap=self.GAP)
        controlsizer.AddGrowableCol(0, proportion=0)
        controlsizer.AddGrowableCol(1, proportion=1)

        controlsizer.Add(wx.StaticText(self, label='Date (UTC):'))
        s = wx.BoxSizer(wx.HORIZONTAL)
        s.Add(wx.TextCtrl(self), proportion=0.5, flag=wx.EXPAND)
        s.Add(wx.StaticText(self, label='Date (local):'), proportion=0.5, flag=wx.EXPAND | wx.LEFT, border=self.GAP)
        s.Add(wx.TextCtrl(self), proportion=0.5, flag=wx.EXPAND | wx.LEFT, border=self.GAP)
        s.Add(wx.StaticText(self, label='Type:'), flag=wx.EXPAND | wx.LEFT, border=self.GAP)
        self.cb_trans_type = wx.ComboBox(self, style=wx.CB_READONLY, choices=Transaction.all_trans_types)
        s.Add(self.cb_trans_type, proportion=1, flag=wx.EXPAND | wx.LEFT, border=self.GAP)
        controlsizer.Add(s, flag=wx.EXPAND)

        controlsizer.Add(wx.StaticText(self, label='Notes:'))
        controlsizer.Add(wx.TextCtrl(self), flag=wx.EXPAND)

        controlsizer.Add(wx.StaticText(self, label='From wallet:'))
        s = wx.BoxSizer(wx.HORIZONTAL)
        self.cb_wallet_from = wx.ComboBox(self, style=wx.CB_READONLY)
        s.Add(self.cb_wallet_from, flag=wx.EXPAND)
        s.Add(wx.StaticText(self, label='Amount:'), flag=wx.EXPAND | wx.LEFT, border=self.GAP)
        s.Add(wx.TextCtrl(self), flag=wx.EXPAND | wx.LEFT, border=self.GAP)
        s.Add(wx.StaticText(self, label='Tx ID:'), flag=wx.EXPAND | wx.LEFT, border=self.GAP)
        s.Add(wx.TextCtrl(self), proportion=1, flag=wx.EXPAND | wx.LEFT, border=self.GAP)
        controlsizer.Add(s, flag=wx.EXPAND)

        controlsizer.Add(wx.StaticText(self, label='To wallet:'))
        s = wx.BoxSizer(wx.HORIZONTAL)
        self.cb_wallet_to = wx.ComboBox(self, style=wx.CB_READONLY)
        s.Add(self.cb_wallet_to, flag=wx.EXPAND)
        s.Add(wx.StaticText(self, label='Amount:'), flag=wx.EXPAND | wx.LEFT, border=self.GAP)
        s.Add(wx.TextCtrl(self), flag=wx.EXPAND | wx.LEFT, border=self.GAP)
        s.Add(wx.StaticText(self, label='Tx ID:'), flag=wx.EXPAND | wx.LEFT, border=self.GAP)
        s.Add(wx.TextCtrl(self), proportion=1, flag=wx.EXPAND | wx.LEFT, border=self.GAP)
        controlsizer.Add(s, flag=wx.EXPAND)

        controlsizer.Add(wx.StaticText(self, label='Fee wallet:'))
        s = wx.BoxSizer(wx.HORIZONTAL)
        self.cb_wallet_fee = wx.ComboBox(self, style=wx.CB_READONLY)
        s.Add(self.cb_wallet_fee, flag=wx.EXPAND)
        s.Add(wx.StaticText(self, label='Amount:'), flag=wx.EXPAND | wx.LEFT, border=self.GAP)
        s.Add(wx.TextCtrl(self), flag=wx.EXPAND | wx.LEFT, border=self.GAP)
        s.Add(wx.StaticText(self, label='Tx ID:'), flag=wx.EXPAND | wx.LEFT, border=self.GAP)
        s.Add(wx.TextCtrl(self), proportion=1, flag=wx.EXPAND | wx.LEFT, border=self.GAP)
        controlsizer.Add(s, flag=wx.EXPAND)

        self.populate_wallet_lists()

        perimeter.Add(controlsizer, proportion=1, flag=wx.ALL | wx.EXPAND, border=self.GAP)

        # Button row
        buttonrow = self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL)
        perimeter.Add(buttonrow, proportion=0, flag=wx.ALL | wx.EXPAND, border=self.EXTERIOR_GAP)

        self.SetSizerAndFit(perimeter)

    def populate_wallet_lists(self):
        cb_list = [self.cb_wallet_from, self.cb_wallet_to, self.cb_wallet_fee]
        for w in Wallet.select().order_by(Wallet.name.asc()):
            for cb in cb_list:
                cb.Append(w.name)

    def OnClose(self, e):
        self.Destroy()
