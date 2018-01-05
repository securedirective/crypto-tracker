import sys
import logging
try:
    import wx
except ImportError:
    raise ImportError("The wxPython module is required to run this program")

from main_window import MainWindow
from config import Config

if __name__ == "__main__":
    # Configure logging
    for arg in sys.argv:
        if arg.lower() == '-v':
            Config.DEBUG = True
    logging.basicConfig(
        format='%(asctime)s %(levelname)s - %(message)s',
        level=logging.DEBUG if Config.DEBUG else logging.WARNING
    )

    app = wx.App()
    # app = wx.App(redirect=True)   # Error messages go to popup window
    form = MainWindow()
    app.MainLoop()
