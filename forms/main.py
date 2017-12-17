import tkinter as tk
# from tkinter import tk


class MainForm(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Add Transaction')
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.frame_main = tk.Frame(self)
        self.frame_main.grid(column=0, row=0, sticky='nsew', padx=10, pady=10)

        self.populate_main_frame(self.frame_main)
        # self.update()
        self.minsize(800, 400)

    def populate_main_frame(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)
        parent.rowconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        parent.rowconfigure(2, weight=1)

        # Toolbar frame
        self.frame_toolbar = tk.Frame(parent)  # , background='red')
        self.populate_toolbar_frame(self.frame_toolbar)
        self.frame_toolbar.grid(column=0, row=0, columnspan=2, sticky='nsew')

        # Transaction frame
        self.frame_transaction = tk.Frame(parent)  # , background='yellow')
        self.frame_transaction.grid(column=0, row=1, columnspan=2, sticky='nsew')
        self.populate_transaction_frame(self.frame_transaction)

        # Wallet frame
        self.frame_wallets = tk.Frame(parent)  # , background='green')
        self.frame_wallets.grid(column=0, row=2, sticky='nsew')
        self.populate_wallet_frame(self.frame_wallets)

        # Currency frame
        self.frame_currency = tk.Frame(parent)  # , background='blue')
        self.frame_currency.grid(column=1, row=2, sticky='nsew')
        self.populate_currency_frame(self.frame_currency)

    def populate_toolbar_frame(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)
        parent.rowconfigure(0, weight=1)

        self.btn_hi = tk.Button(
            parent,
            text="Hello World (click me)",
            command=self.say_hi)
        self.btn_hi.grid(column=0, row=0, sticky='nsew')

        self.btn_exit = tk.Button(
            parent, text="Exit")
            # command=self.master.destroy)
        self.btn_exit.grid(column=1, row=0, sticky='nsew')

    def populate_transaction_frame(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)

        self.lst_transactions = o = tk.Listbox(parent)
        o.grid(column=0, row=0, sticky='nsew')
        for x in range(10):
            o.insert(x, "test " + str(x))

    def populate_wallet_frame(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)

        self.lst_wallets = o = tk.Listbox(parent)
        o.grid(column=0, row=0, sticky='nsew')
        for x in range(10):
            o.insert(x, "test " + str(x))

    def populate_currency_frame(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)

        self.lst_currencies = o = tk.Listbox(parent)
        o.grid(column=0, row=0, sticky='nsew')
        for x in range(10):
            o.insert(x, "test " + str(x))

    def say_hi(self):
        print("hi there, everyone!")
