import wx
import wx.lib.mixins.listctrl as listctrlmixins


def print_flush(s):
    """In wxPython programs, print output doesn't show on the screen until the program quits. This fixes that."""
    print(s)
    sys.stdout.flush()


def msg(s):
    wx.MessageBox(s, "Alert", wx.ICON_INFORMATION | wx.CENTRE)


class Wrapper():
    """Nifty little class to improve the indenting of your wxPython widget initialization"""
    def __init__(self, cls):
        self.cls = cls

    def __enter__(self):
        return self.cls

    def __exit__(self, type, value, traceback):
        pass


class CustomListCtrl(wx.ListCtrl, listctrlmixins.ListCtrlAutoWidthMixin):
    def __init__(self, *args, **kwargs):
        wx.ListCtrl.__init__(self, *args, **kwargs)
        listctrlmixins.ListCtrlAutoWidthMixin.__init__(self)

    def bulk_add_columns(self, *columns):
        """Shortcut for calling InsertColumn"""
        n = 0
        for c in columns:
            self.InsertColumn(n, c)
            n += 1

    def autosize_all_columns(self):
        for n in range(self.GetColumnCount()):
            self.SetColumnWidth(n, wx.LIST_AUTOSIZE)
