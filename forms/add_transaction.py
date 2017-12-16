import tkinter as tk
from tkinter import ttk


class AddTransactionForm():  # tk.Frame):
    def __init__(self):
        # super().__init__(tk.Tk())
        # self.master.title('Add Transaction')
        # self.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S), padx=10, pady=10)
        # self.create_widgets()
        self.root = tk.Tk()
        self.root.title('Add Transaction')
        self.frame_main = ttk.Frame(self.root, padding="3 3 12 12")
        self.frame_main.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S), padx=10, pady=10)
        self.frame_main.columnconfigure(0, weight=1)
        self.frame_main.rowconfigure(0, weight=1)
        self.create_widgets(self.frame_main)
        # self.frame_main.configure(background='red')

    def mainloop(self):
        self.root.mainloop()

    def create_widgets(self, parent):
        self.btn_hi = o = ttk.Button(
            parent,
            text="Hello World\n(click me)",
            command=self.say_hi)
        o.grid(column=0, row=0)

        self.btn_exit = o = tk.Button(
            parent, text="Exit")
            # command=self.master.destroy)
        o.grid(column=1, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))

        # Transaction frame
        self.frame_transaction = f = ttk.Frame(parent, borderwidth=5, relief="sunken")
        self.create_transaction_frame(f)
        f.grid(column=0, row=2, columnspan=2, sticky=(tk.N, tk.W, tk.E, tk.S), padx=10, pady=10)

        # Wallet frame
        self.frame_wallets = f = tk.Frame(parent, borderwidth=5, relief="sunken")
        self.create_wallet_frame(f)
        f.grid(column=0, row=3, columnspan=2, sticky=(tk.N, tk.W, tk.E, tk.S), padx=10, pady=10)

        # Currency frame

    def create_transaction_frame(self, parent):
        self.lst_transactions2 = o = tk.Listbox(parent)
        for x in range(10):
            o.insert(x, "test " + str(x))
        o.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))

    def create_wallet_frame(self, parent):
        self.lst_transactions3 = o = tk.Listbox(parent)
        for x in range(10):
            o.insert(x, "test " + str(x))
        o.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))

    def say_hi(self):
        print("hi there, everyone!")
