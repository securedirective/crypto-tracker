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

    def __init__(self, parent, wallet_list, instance=None):
        title = "Edit Transaction" if instance else "Add Transaction"
        super().__init__(parent=parent, title=title, size=wx.Size(1000, 1000),
                         style=wx.CAPTION | wx.CLOSE_BOX | wx.RESIZE_BORDER)

        self.instance = instance
        self.wallet_combos = []
        self.wallet_list = wallet_list
        self.init_gui()

    def init_gui(self):
        # print_flush("init_gui")
        with Wrapper(wx.BoxSizer(wx.VERTICAL)) as perimeter:
            # Main area
            with Wrapper(wx.FlexGridSizer(cols=2, vgap=self.GAP, hgap=self.GAP)) as mainarea:
                mainarea.AddGrowableCol(0, proportion=0)
                mainarea.AddGrowableCol(1, proportion=1)

                # Top row
                mainarea.Add(wx.StaticText(self, label='Date (UTC):'))
                with Wrapper(wx.BoxSizer(wx.HORIZONTAL)) as s:
                    self.txt_date_utc = wx.TextCtrl(self)
                    s.Add(self.txt_date_utc, proportion=0.5, flag=wx.EXPAND)

                    s.Add(wx.StaticText(self, label='Date (local):'), proportion=0.5, flag=wx.EXPAND | wx.LEFT, border=self.GAP)

                    self.txt_date_local = wx.TextCtrl(self)
                    s.Add(self.txt_date_local, proportion=0.5, flag=wx.EXPAND | wx.LEFT, border=self.GAP)

                    s.Add(wx.StaticText(self, label='Type:'), flag=wx.EXPAND | wx.LEFT, border=self.GAP)

                    self.cb_trans_type = wx.ComboBox(self, style=wx.CB_READONLY, choices=Transaction.all_trans_types)
                    s.Add(self.cb_trans_type, proportion=1, flag=wx.EXPAND | wx.LEFT, border=self.GAP)
                mainarea.Add(s, flag=wx.EXPAND)

                # Inputs/outputs
                n = 0
                for subitem in ['From wallet:', 'To wallet:', 'Fee wallet:']:
                    mainarea.Add(wx.StaticText(self, label=subitem))

                    with Wrapper(wx.BoxSizer(wx.HORIZONTAL)) as s:
                        cb = wx.ComboBox(self, style=wx.CB_READONLY)
                        cb.Bind(wx.EVT_COMBOBOX, self.wallet_combo_item_select, id=n)
                        s.Add(cb, flag=wx.EXPAND)
                        self.wallet_combos.append(cb)

                        s.Add(wx.StaticText(self, label='Amount:'), flag=wx.EXPAND | wx.LEFT, border=self.GAP)

                        s.Add(wx.TextCtrl(self), flag=wx.EXPAND | wx.LEFT, border=self.GAP)

                        s.Add(wx.StaticText(self, label='Tx ID:'), flag=wx.EXPAND | wx.LEFT, border=self.GAP)

                        s.Add(wx.TextCtrl(self), proportion=1, flag=wx.EXPAND | wx.LEFT, border=self.GAP)
                    mainarea.Add(s, flag=wx.EXPAND)

                    n += 1

                # Populate all the combo boxes in one step
                self.populate_wallet_lists()

                # Notes row
                mainarea.Add(wx.StaticText(self, label='Notes:'))
                mainarea.Add(wx.TextCtrl(self), flag=wx.EXPAND)
            perimeter.Add(mainarea, proportion=1, flag=wx.EXPAND | wx.ALL, border=self.GAP)

            # Button row
            buttonrow = self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL)
            if buttonrow:   # It might be None on some platforms when the buttons are created outside the window
                perimeter.Add(buttonrow, proportion=0, flag=wx.EXPAND | wx.ALL, border=self.EXTERIOR_GAP)
        self.SetSizerAndFit(perimeter)

    def populate_wallet_lists(self):
        # print_flush("populate_wallet_lists")
        for w in self.wallet_list:
            for cb in self.wallet_combos:
                new_indox = cb.Append(w.str_long())

    def wallet_combo_item_select(self, event, id):
        # print_flush("wallet_combo_item_select")
        # chosen_wallet[id] =
        msg(event)

    def TransferDataFromWindow(self):
        # print_flush("TransferDataFromWindow")
        # print_flush("Selection: %s" % self.wallet_combos[0].GetValue())
        # print_flush("Selection: %s" % self.wallet_combos[1].GetValue())
        # print_flush("Selection: %s" % self.wallet_combos[2].GetValue())
        return True

    def TransferDataToWindow(self):
        # print_flush("TransferDataToWindow")
        if self.instance:
            self.txt_date_utc.SetValue(str(self.instance.date_utc))
            if self.instance.from_wallet:
                self.wallet_combos[0].SetValue(self.instance.from_wallet.str_long())
            if self.instance.to_wallet:
                self.wallet_combos[1].SetValue(self.instance.to_wallet.str_long())
            if self.instance.fee_wallet:
                self.wallet_combos[2].SetValue(self.instance.fee_wallet.str_long())

        else:
            self.wallet_combos[0].SetValue("K&A > Electrum Phone > BTC (Bitcoin)")
            self.wallet_combos[1].SetValue("K&A > Electrum Christmas > BTC (Bitcoin)")
            self.wallet_combos[2].SetValue("K&A > Electrum Phone > BTC (Bitcoin)")
        return True

    def Validate(self):
        # print_flush("Validate")
        return True
