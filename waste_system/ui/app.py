import tkinter as tk
from tkinter import ttk, messagebox
from db.init_db import initialize_database
from services.user_service import *
from services.pickup_service import *

# ================= APP =================
root = tk.Tk()
root.title("Waste System Pro")
root.geometry("1250x800")
root.configure(bg="#0b1220")

nav = tk.Frame(root, bg="#111827", width=250)
nav.pack(side="left", fill="y")

content = tk.Frame(root, bg="#0b1220")
content.pack(side="right", fill="both", expand=True)

def clear():
    for w in content.winfo_children():
        w.destroy()

def header(text):
    tk.Label(content, text=text, font=("Arial", 22, "bold"),
             bg="#0b1220", fg="white").pack(pady=15)

# ================= USERS =================
def users_page():
    clear()
    header("Users")
    tree = ttk.Treeview(content, columns=("ID","Name","City","Barangay"), show="headings")
    for c in ("ID","Name","City","Barangay"):
        tree.heading(c, text=c)
    tree.pack(fill="both", expand=True)
    for u in get_all_users():
        tree.insert("", "end", values=(u["user_id"], u["name"], u["city"], u["barangay"]))

# ================= ADD USER =================
def add_user_page():
    clear()
    header("Add User")
    entries = {}
    fields = ["Name","Province","City","Barangay","House ID","Address"]
    for f in fields:
        tk.Label(content, text=f, bg="#0b1220", fg="white").pack()
        e = tk.Entry(content)
        e.pack()
        entries[f] = e

    def save():
        create_user(
            entries["Name"].get(),
            entries["Province"].get(),
            entries["City"].get(),
            entries["Barangay"].get(),
            entries["House ID"].get(),
            entries["Address"].get()
        )
        messagebox.showinfo("OK","User Added")

    tk.Button(content, text="Save", command=save).pack(pady=10)

# ================= PICKUP CALENDAR =================
def pickup_page():
    clear()
    header("Pickup Calendar 2026")
    year = 2026
    month = tk.IntVar(value=1)
    tk.OptionMenu(content, month, *range(1,13)).pack()

    cal = tk.Frame(content, bg="#0b1220")
    cal.pack()

    def build():
        for w in cal.winfo_children():
            w.destroy()
        days = 30 if month.get() in [4,6,9,11] else 31
        if month.get() == 2:
            days = 28
        for d in range(1, days+1):
            tk.Button(cal, text=str(d), width=4,
                      command=lambda x=d: print(f"{year}-{month.get()}-{x}")
            ).pack(side="left")

    tk.Button(content, text="Load Calendar", command=build).pack()

# ================= NAV =================
tk.Button(nav, text="Users", command=users_page).pack(fill="x")
tk.Button(nav, text="Add User", command=add_user_page).pack(fill="x")
tk.Button(nav, text="Pickup Calendar", command=pickup_page).pack(fill="x")

# ================= START =================
initialize_database()
users_page()
root.mainloop()