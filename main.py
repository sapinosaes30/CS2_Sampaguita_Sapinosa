from db.connection import get_connection
from db.init_db import initialize_database
from services.user_systems import *
from services.pickup_service import *
from collections import defaultdict
import datetime
import tkinter as tk
from tkinter import ttk, messagebox

# ================= DATABASE =================


# ================= THEME =================

BG = "#0b1220"
PANEL = "#111827"
FG = "#e5e7eb"
ACCENT = "#22c55e"
ACCENT2 = "#3b82f6"
CARD = "#1f2937"


# ================= ROOT =================

root = tk.Tk()
root.title("Waste Management System")
root.geometry("1200x750")
root.configure(bg=BG)


# ================= LAYOUT =================

nav = tk.Frame(root, bg=PANEL, width=240)
nav.pack(side="left", fill="y")

content = tk.Frame(root, bg=BG)
content.pack(side="right", fill="both", expand=True)

active_btn = None


def set_active(btn):
    global active_btn
    if active_btn:
        active_btn.configure(bg=PANEL)
    btn.configure(bg="#374151")
    active_btn = btn


def clear():
    for w in content.winfo_children():
        w.destroy()


def show(page):
    clear()
    page()


# ================= HEADER =================

def header(text):
    tk.Label(
        content,
        text=text,
        font=("Segoe UI", 22, "bold"),
        bg=BG,
        fg=FG
    ).pack(pady=18)


# ================= NAV BUTTON =================


def nav_button(text, cmd):
    btn = tk.Button(
        nav,
        text=text,
        bg=PANEL,
        fg=FG,
        relief="flat",
        anchor="w",
        padx=20,
        pady=12,
        font=("Segoe UI", 11),
        command=lambda: [set_active(btn), show(cmd)]
    )
    btn.pack(fill="x")
    return btn


# ================= USERS DASHBOARD =================

def users_page():
    header("Users Management")

    # ================= TOP STATS =================
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]
    conn.close()

    stats = tk.Frame(content, bg=BG)
    stats.pack(pady=10)

    stats_label = tk.Label(
        stats,
        text=f"Total Users: {total_users}",
        bg=CARD,
        fg=ACCENT,
        font=("Segoe UI", 14, "bold"),
        padx=15,
        pady=10
    )
    stats_label.pack()

    # ================= SEARCH =================
    search_frame = tk.Frame(content, bg=BG)
    search_frame.pack(pady=10)

    search = tk.Entry(
        search_frame,
        width=40,
        bg=CARD,
        fg=FG,
        insertbackground=FG,
        font=("Segoe UI", 11)
    )
    search.pack(side="left", padx=5)

    # ================= SCROLLABLE AREA =================
    canvas = tk.Canvas(content, bg=BG, highlightthickness=0)
    scrollbar = tk.Scrollbar(content, orient="vertical", command=canvas.yview)

    scroll_frame = tk.Frame(canvas, bg=BG)

    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # ================= LOAD USERS =================
    def load(keyword=""):
        for w in scroll_frame.winfo_children():
            w.destroy()

        conn = get_connection()
        cur = conn.cursor()

        if keyword:
            cur.execute("SELECT * FROM users WHERE name LIKE ?", ('%' + keyword + '%',))
        else:
            cur.execute("SELECT * FROM users ORDER BY user_id DESC")

        users = cur.fetchall()
        conn.close()

        # Update stats
        stats_label.config(text=f"Total Users: {len(users)}")

        if not users:
            tk.Label(scroll_frame,
                     text="No users found",
                     bg=BG, fg=FG,
                     font=("Segoe UI", 12)).pack(pady=20)
            return

        for u in users:
            card = tk.Frame(scroll_frame, bg=CARD, padx=15, pady=10)
            card.pack(fill="x", padx=15, pady=8)

            # LEFT SIDE INFO
            info = tk.Frame(card, bg=CARD)
            info.pack(side="left")

            tk.Label(info,
                     text=f"User #{u['user_id']} - {u['name']}",
                     bg=CARD, fg=FG,
                     font=("Segoe UI", 12, "bold")).pack(anchor="w")

            tk.Label(info,
                     text=f"{u['city']} • {u['barangay']}",
                     bg=CARD, fg="#9ca3af").pack(anchor="w")

            # RIGHT SIDE BUTTONS
            buttons = tk.Frame(card, bg=CARD)
            buttons.pack(side="right")

            def view_details(user=u):
                detail = tk.Toplevel(root)
                detail.title("User Details")
                detail.geometry("350x300")
                detail.configure(bg=BG)

                tk.Label(detail,
                         text=user["name"],
                         bg=BG, fg=ACCENT,
                         font=("Segoe UI", 14, "bold")).pack(pady=10)

                fields = [
                    ("ID", user["user_id"]),
                    ("Province", user["province"]),
                    ("City", user["city"]),
                    ("Barangay", user["barangay"]),
                    ("House ID", user["house_id"]),
                    ("Address", user["address"])
                ]

                for f, v in fields:
                    tk.Label(detail,
                             text=f"{f}: {v}",
                             bg=BG, fg=FG).pack(anchor="w", padx=20)

            def edit_user(user=u):
                edit_win = tk.Toplevel(root)
                edit_win.title("Edit User")
                edit_win.geometry("400x400")
                edit_win.configure(bg=BG)

                tk.Label(edit_win, text="Edit User", bg=BG, fg=ACCENT, font=("Segoe UI", 16, "bold")).pack(pady=10)

                fields = ["Name", "Province", "City", "Barangay", "House ID", "Address"]
                entries = {}

                for i, f in enumerate(fields):
                    tk.Label(edit_win, text=f, bg=BG, fg=FG).pack(anchor="w", padx=20)
                    e = tk.Entry(edit_win, width=40, bg=CARD, fg=FG, insertbackground=FG)
                    e.pack(pady=2, padx=20)
                    e.insert(0, user[f.lower().replace(" ", "_")])
                    entries[f] = e

                def save_edit():
                    if not entries["Name"].get():
                        messagebox.showerror("Error", "Name is required")
                        return

                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute("""
                        UPDATE users
                        SET name=?, province=?, city=?, barangay=?, house_id=?, address=?
                        WHERE user_id=?
                    """, (
                        entries["Name"].get(),
                        entries["Province"].get(),
                        entries["City"].get(),
                        entries["Barangay"].get(),
                        entries["House ID"].get(),
                        entries["Address"].get(),
                        user["user_id"]
                    ))
                    conn.commit()
                    conn.close()

                    messagebox.showinfo("Success", "User updated successfully")
                    edit_win.destroy()
                    load(search.get() if search.get() else "")

                tk.Button(edit_win, text="Save Changes", bg=ACCENT, fg="black", command=save_edit).pack(pady=10)

            def delete_user(user=u):
                if messagebox.askyesno("Confirm", f"Delete user {user['name']}?"):
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute("DELETE FROM users WHERE user_id=?", (user["user_id"],))
                    conn.commit()
                    conn.close()
                    load(search.get() if search.get() else "")

            tk.Button(buttons, text="View", bg=ACCENT2, fg="white", command=view_details).pack(side="left", padx=5)
            tk.Button(buttons, text="Edit", bg=ACCENT, fg="black", command=edit_user).pack(side="left", padx=5)
            tk.Button(buttons, text="Delete", bg="#dc2626", fg="white", command=delete_user).pack(side="left", padx=5)

    # ================= SEARCH BUTTON =================
    def do_search():
        load(search.get())

    tk.Button(
        search_frame,
        text="Search",
        bg=ACCENT2,
        fg="white",
        relief="flat",
        command=do_search
    ).pack(side="left", padx=5)

    # initial load
    load()


# ================= ADD USER (RESTORED + FIXED) =================

def add_user_page():
    header("Add New User")

    form = tk.Frame(content, bg=BG)
    form.pack()

    fields = ["Name", "Province", "City", "Barangay", "House ID", "Address"]
    entries = {}

    for i, f in enumerate(fields):
        tk.Label(form, text=f, bg=BG, fg=FG, font=("Segoe UI", 10)).grid(row=i, column=0, sticky="w", pady=5)

        e = tk.Entry(form, width=45, bg=CARD, fg=FG, insertbackground=FG)
        e.grid(row=i, column=1, pady=5, padx=10)
        entries[f] = e

    def save():
        if not entries["Name"].get():
            messagebox.showerror("Error", "Name is required")
            return

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO users (name, province, city, barangay, house_id, address)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            entries["Name"].get(),
            entries["Province"].get(),
            entries["City"].get(),
            entries["Barangay"].get(),
            entries["House ID"].get(),
            entries["Address"].get()
        ))

        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "User Added Successfully")

        for e in entries.values():
            e.delete(0, tk.END)

    tk.Button(
        content,
        text="SAVE USER",
        bg=ACCENT,
        fg="black",
        font=("Segoe UI", 11, "bold"),
        relief="flat",
        padx=25,
        pady=8,
        command=save
    ).pack(pady=15)


# ================= PICKUP PAGE =================

def days_in_month(m):
    if m in [1,3,5,7,8,10,12]:
        return 31
    elif m in [4,6,9,11]:
        return 30
    return 28

def pickup_page():
    header("Schedule Pickup Calendar")

    form = tk.Frame(content, bg=BG)
    form.pack()

    tk.Label(form, text="User ID", bg=BG, fg=FG).pack()
    uid = tk.Entry(form, width=30, bg=CARD, fg=FG)
    uid.pack(pady=5)

    tk.Label(form, text="Time (HH:MM)", bg=BG, fg=FG).pack()
    time = tk.Entry(form, width=30, bg=CARD, fg=FG)
    time.pack(pady=5)

    # ===== STATE =====
    YEAR = 2026
    month_var = tk.IntVar(value=1)
    selected_btn = {"btn": None}
    day_var = tk.IntVar(value=1)

    # ===== HEADER NAV =====
    nav_frame = tk.Frame(form, bg=BG)
    nav_frame.pack(pady=10)

    def change_month(delta):
        m = month_var.get() + delta
        if 1 <= m <= 12:
            month_var.set(m)
            build_calendar()

    tk.Button(nav_frame, text="⬅", bg=PANEL, fg=FG,
              command=lambda: change_month(-1)).pack(side="left", padx=5)

    month_label = tk.Label(nav_frame, text="Month", bg=BG, fg=FG,
                           font=("Segoe UI", 12, "bold"))
    month_label.pack(side="left", padx=10)

    tk.Button(nav_frame, text="➡", bg=PANEL, fg=FG,
              command=lambda: change_month(1)).pack(side="left", padx=5)

    # ===== CALENDAR FRAME =====
    cal_frame = tk.Frame(form, bg=BG)
    cal_frame.pack(pady=10)

    def clear_selection():
        if selected_btn["btn"]:
            selected_btn["btn"].config(bg=CARD)

    def select_day(btn, day):
        clear_selection()
        btn.config(bg=ACCENT)
        selected_btn["btn"] = btn
        day_var.set(day)

    def build_calendar():
        for w in cal_frame.winfo_children():
            w.destroy()

        m = month_var.get()
        month_label.config(text=f"2026 - Month {m}")

        days = days_in_month(m)

        # Calculate starting weekday (0=Monday)
        start_weekday = datetime.date(YEAR, m, 1).weekday()

        row, col = 1, start_weekday  # Start from row 1, col based on weekday

        # weekday headers (visual improvement)
        for d in ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]:
            tk.Label(cal_frame, text=d, bg=BG, fg=FG,
                     width=5, font=("Segoe UI", 9, "bold")).grid(row=0, column=col)
            col += 1

        row = 1
        col = start_weekday

        for d in range(1, days + 1):
            btn = tk.Button(
                cal_frame,
                text=str(d),
                width=5,
                height=2,
                bg=CARD,
                fg=FG,
                relief="flat"
            )

            btn.config(command=lambda b=btn, day=d: select_day(b, day))

            btn.grid(row=row, column=col, padx=3, pady=3)

            col += 1
            if col > 6:
                col = 0
                row += 1

    tk.Button(form, text="LOAD CALENDAR",
              bg=ACCENT2, fg="white",
              command=build_calendar).pack(pady=5)

    build_calendar()

    # ===== SUBMIT =====
    def add():
        if not uid.get() or not time.get():
            messagebox.showerror("Error", "Fill all fields")
            return

        # Check if user exists
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE user_id=?", (uid.get(),))
        user = cur.fetchone()
        if not user:
            conn.close()
            messagebox.showerror("Error", "User ID does not exist")
            return

        date = f"{YEAR}-{month_var.get():02d}-{day_var.get():02d}"

        cur.execute("""
            INSERT INTO pickups (user_id, date, time)
            VALUES (?, ?, ?)
        """, (uid.get(), date, time.get()))

        conn.commit()
        conn.close()

        messagebox.showinfo("Success", f"Pickup scheduled: {date}")

        uid.delete(0, tk.END)
        time.delete(0, tk.END)

    tk.Button(content, text="SCHEDULE PICKUP",
              bg=ACCENT, fg="black",
              command=add).pack(pady=10)


# ================= VIEW PICKUPS =================

def view_pickups_page():
    header("Pickup Calendar")

    YEAR = 2026

    top = tk.Frame(content, bg=BG)
    top.pack(pady=10)

    month_var = tk.StringVar(value="1")

    tk.Label(top, text="Month:", bg=BG, fg=FG).pack(side="left")

    month_menu = tk.OptionMenu(top, month_var, *[str(i) for i in range(1,13)])
    month_menu.pack(side="left", padx=10)

    # Main container
    main_frame = tk.Frame(content, bg=BG)
    main_frame.pack(fill="both", expand=True)

    # Calendar frame
    cal_frame = tk.Frame(main_frame, bg=BG)
    cal_frame.pack(side="left", fill="both", expand=True)

    # Info frame for selected day
    info_frame = tk.Frame(main_frame, bg=BG, width=300)
    info_frame.pack(side="right", fill="y")
    info_frame.pack_propagate(False)

    info_box = tk.Frame(info_frame, bg=CARD, padx=10, pady=10)
    info_box.pack(fill="both", expand=True)

    tk.Label(info_box, text="Select a day to view pickups",
             bg=CARD, fg=FG, font=("Segoe UI", 12)).pack(pady=20)

    def load_calendar():
        for w in cal_frame.winfo_children():
            w.destroy()

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM pickups")
        pickups = cur.fetchall()
        conn.close()

        month = int(month_var.get())

        # Create pickup map
        pickup_map = {}
        for p in pickups:
            date = p["date"]
            if date not in pickup_map:
                pickup_map[date] = []
            pickup_map[date].append(p)

        days = 31 if month in [1,3,5,7,8,10,12] else \
               30 if month in [4,6,9,11] else 28

        # GRID HEADER
        days_name = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]

        for i, d in enumerate(days_name):
            tk.Label(cal_frame, text=d, bg=PANEL, fg=FG, width=10).grid(row=0, column=i)

        row = 1
        col = 0

        for d in range(1, days+1):
            date_str = f"2026-{month:02d}-{d:02d}"

            # check if pickup exists
            has_pickup = date_str in pickup_map

            color = ACCENT if has_pickup else CARD

            cell = tk.Frame(cal_frame, bg=color, width=100, height=60)
            cell.grid(row=row, column=col, padx=3, pady=3)
            cell.grid_propagate(False)

            btn = tk.Button(cell, text=str(d), bg=color, fg=FG, relief="flat",
                           command=lambda ds=date_str, pm=pickup_map: show_day(ds, pm))
            btn.pack(fill="both", expand=True)

            col += 1
            if col > 6:
                col = 0
                row += 1

    def show_day(date, pickup_map):
        for w in info_box.winfo_children():
            w.destroy()

        tk.Label(info_box, text=f"Pickups on {date}",
                 bg=CARD, fg=ACCENT,
                 font=("Segoe UI", 12, "bold")).pack(pady=10)

        if date not in pickup_map:
            tk.Label(info_box, text="No pickups",
                     bg=CARD, fg=FG).pack(pady=20)
            return

        for p in pickup_map[date]:
            row = tk.Frame(info_box, bg=CARD, pady=5, padx=5)
            row.pack(fill="x", pady=2)

            tk.Label(row,
                     text=f"User {p['user_id']} | {p['time']} | Status: {p['status']}",
                     bg=CARD, fg=FG).pack(side="left")

            # Buttons for update status and delete
            def update_status(pickup=p):
                def set_status(status):
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute("UPDATE pickups SET status=? WHERE pickup_id=?", (status, pickup["pickup_id"]))
                    conn.commit()
                    conn.close()
                    # Refresh the view
                    view_pickups_page()

                status_win = tk.Toplevel(root)
                status_win.title("Update Status")
                status_win.geometry("200x150")
                status_win.configure(bg=BG)

                tk.Label(status_win, text="Set Status", bg=BG, fg=FG).pack(pady=10)

                for st in ["Pending", "Driver Assigned", "Completed"]:
                    tk.Button(status_win, text=st, bg=ACCENT2, fg="white",
                              command=lambda s=st: [set_status(s), status_win.destroy()]).pack(pady=2)

            def delete_pickup(pickup=p):
                if messagebox.askyesno("Confirm", "Delete this pickup?"):
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute("DELETE FROM pickups WHERE pickup_id=?", (pickup["pickup_id"],))
                    conn.commit()
                    conn.close()
                    view_pickups_page()

            tk.Button(row, text="Update", bg=ACCENT, fg="black", command=update_status).pack(side="right", padx=5)
            tk.Button(row, text="Delete", bg="#dc2626", fg="white", command=delete_pickup).pack(side="right", padx=5)

    tk.Button(top, text="Load Calendar", bg=ACCENT2,
              fg="white", command=load_calendar).pack(side="left")

    load_calendar()

# ================= DASHBOARD =================

def dashboard_page():
    header("Dashboard Overview")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM users")
    users_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM pickups")
    pickup_count = cur.fetchone()[0]

    conn.close()

    card_frame = tk.Frame(content, bg=BG)
    card_frame.pack(pady=20)

    def card(title, value, color):
        box = tk.Frame(card_frame, bg=CARD, padx=20, pady=15)
        box.pack(side="left", padx=15)

        tk.Label(box, text=title, bg=CARD, fg=FG).pack()
        tk.Label(box, text=str(value), bg=CARD, fg=color,
                 font=("Segoe UI", 22, "bold")).pack()

    card("Total Users", users_count, ACCENT)
    card("Total Pickups", pickup_count, ACCENT2)


# ================= START =================

# Create navigation buttons
nav_button("Dashboard", dashboard_page)
nav_button("Users", users_page)
nav_button("Add User", add_user_page)
nav_button("Schedule Pickup", pickup_page)
nav_button("View Pickups", view_pickups_page)

initialize_database()
show(dashboard_page)

# START
root.mainloop()