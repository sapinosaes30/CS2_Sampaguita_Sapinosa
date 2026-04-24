import calendar
import datetime
import tkinter as tk
from tkinter import ttk, messagebox

from db.init_db import initialize_database
from services.pickup_service import (
    STATUS_FLOW,
    PRIORITY_OPTIONS,
    create_pickup,
    get_all_pickups,
    get_pickups_by_date,
    get_pickups_by_month,
    get_high_priority_count,
    get_pending_pickup_count,
    get_pickup_count,
    update_pickup_status,
    soft_delete_pickup,
)
from services.user_service import (
    create_user,
    get_active_user_options,
    get_all_users,
    get_cities,
    get_user_by_id,
    get_user_count,
    soft_delete_user,
    update_user,
)
from utils.audit import log_action
from utils.validation import (
    validate_date,
    validate_time,
    validate_priority,
    required,
)


class WasteSystemApp:
    BG = "#0b1220"
    NAV_BG = "#111827"
    CARD_BG = "#1f2937"
    HEADER_FONT = ("Segoe UI", 22, "bold")
    LABEL_FONT = ("Segoe UI", 11)
    BUTTON_FONT = ("Segoe UI", 10)
    TEXT_COLOR = "white"

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Waste Management System")
        self.root.geometry("1250x800")
        self.root.configure(bg=self.BG)

        self.nav = tk.Frame(self.root, bg=self.NAV_BG, width=250)
        self.nav.pack(side="left", fill="y")

        self.content = tk.Frame(self.root, bg=self.BG)
        self.content.pack(side="right", fill="both", expand=True)

        self.selected_date = datetime.date.today()
        self.user_sort_by = "user_id"
        self.user_sort_ascending = False
        self.search_query = tk.StringVar()
        self.city_filter = tk.StringVar(value="All")

        self.active_user_combo = None
        self.pickup_tree = None
        self.user_tree = None
        self.selected_date_label = None
        self.calendar_frame = None
        self.toast_widget = None

        self._setup_styles()
        self._build_sidebar()
        initialize_database()
        self.show(self.dashboard_page)

    def _setup_styles(self):
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Treeview", background="#1f2937", foreground="white", fieldbackground="#1f2937", rowheight=26)
        style.configure("Treeview.Heading", background="#111827", foreground="white", font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[("selected", "#2563eb")], foreground=[("selected", "white")])

    def _build_sidebar(self):
        brand = tk.Label(
            self.nav,
            text="Waste System",
            font=("Segoe UI", 18, "bold"),
            bg=self.NAV_BG,
            fg=self.TEXT_COLOR,
            pady=20,
        )
        brand.pack(fill="x")

        self._nav_button("Dashboard", self.dashboard_page)
        self._nav_button("Users", self.users_page)
        self._nav_button("Add User", self.new_user_page)
        self._nav_button("Pickups", self.pickups_page)

    def _nav_button(self, text, page):
        btn = tk.Button(
            self.nav,
            text=text,
            bg=self.NAV_BG,
            fg=self.TEXT_COLOR,
            relief="flat",
            anchor="w",
            padx=20,
            pady=15,
            command=lambda: self.show(page),
            font=self.BUTTON_FONT,
            activebackground="#1f2937",
        )
        btn.pack(fill="x")
        return btn

    def clear(self):
        for child in self.content.winfo_children():
            child.destroy()

    def show(self, page):
        self.clear()
        page()

    def header(self, title):
        tk.Label(
            self.content,
            text=title,
            font=self.HEADER_FONT,
            bg=self.BG,
            fg=self.TEXT_COLOR,
        ).pack(pady=20)

    def card(self, parent, **kwargs):
        options = {
            "bg": self.CARD_BG,
            "padx": 18,
            "pady": 18,
            "bd": 0,
            "highlightthickness": 0,
        }
        options.update(kwargs)
        frame = tk.Frame(parent, **options)
        return frame

    def show_toast(self, message, duration=2200):
        if self.toast_widget and self.toast_widget.winfo_exists():
            self.toast_widget.destroy()
        self.toast_widget = tk.Label(
            self.root,
            text=message,
            bg="#111827",
            fg="white",
            font=self.LABEL_FONT,
            padx=12,
            pady=8,
            bd=0,
        )
        self.toast_widget.place(relx=0.98, rely=0.96, anchor="se")
        self.root.after(duration, lambda: self.toast_widget.destroy())

    def confirm_delete(self, action):
        if messagebox.askyesno("Confirm", "Are you sure you want to continue?"):
            action()

    def dashboard_page(self):
        self.header("Admin Dashboard")

        summary_frame = self.card(self.content)
        summary_frame.pack(fill="x", padx=20, pady=(0, 20))

        stats = [
            ("Users", get_user_count(), "#38bdf8"),
            ("Pickups", get_pickup_count(), "#34d399"),
            ("Pending", get_pending_pickup_count(), "#fbbf24"),
            ("High Priority", get_high_priority_count(), "#f87171"),
        ]

        for index, (label_text, value, color) in enumerate(stats):
            card = self.card(summary_frame, padx=20, pady=20)
            card.grid(row=0, column=index, padx=10, pady=10, sticky="nsew")
            summary_frame.grid_columnconfigure(index, weight=1)
            tk.Label(card, text=label_text, font=("Segoe UI", 12), bg=self.CARD_BG, fg="#94a3b8").pack(anchor="w")
            tk.Label(card, text=str(value), font=("Segoe UI", 24, "bold"), bg=self.CARD_BG, fg=color).pack(anchor="w", pady=(10, 0))

        action_frame = self.card(self.content)
        action_frame.pack(fill="x", padx=20, pady=(0, 20))
        tk.Label(action_frame, text="Quick Actions", font=("Segoe UI", 14, "bold"), bg=self.CARD_BG, fg=self.TEXT_COLOR).pack(anchor="w")
        button_frame = tk.Frame(action_frame, bg=self.CARD_BG)
        button_frame.pack(fill="x", pady=10)
        tk.Button(button_frame, text="Manage Users", command=lambda: self.show(self.users_page), bg="#2563eb", fg="white", relief="flat", padx=14, pady=10).pack(side="left", padx=10)
        tk.Button(button_frame, text="Schedule Pickup", command=lambda: self.show(self.pickups_page), bg="#14b8a6", fg="white", relief="flat", padx=14, pady=10).pack(side="left", padx=10)

        self.show_toast("Welcome to the Waste Management Dashboard", duration=2000)

    def users_page(self):
        self.header("Users Dashboard")

        search_card = self.card(self.content)
        search_card.pack(fill="x", padx=20, pady=(0, 20))

        tk.Label(search_card, text="Search users", bg=self.CARD_BG, fg=self.TEXT_COLOR, font=self.LABEL_FONT).grid(row=0, column=0, sticky="w")
        search_entry = tk.Entry(search_card, textvariable=self.search_query, font=self.LABEL_FONT, bg="#111827", fg="white", insertbackground="white", relief="flat")
        search_entry.grid(row=1, column=0, sticky="ew", pady=10, padx=(0, 10))
        search_entry.bind("<Return>", lambda event: self.load_user_table())

        tk.Label(search_card, text="City", bg=self.CARD_BG, fg=self.TEXT_COLOR, font=self.LABEL_FONT).grid(row=0, column=1, sticky="w")
        cities = ["All"] + get_cities()
        city_combo = ttk.Combobox(search_card, values=cities, textvariable=self.city_filter, state="readonly", font=self.LABEL_FONT)
        city_combo.grid(row=1, column=1, sticky="ew", pady=10, padx=(0, 10))
        city_combo.bind("<<ComboboxSelected>>", lambda event: self.load_user_table())

        tk.Button(search_card, text="Search", command=self.load_user_table, bg="#2563eb", fg="white", relief="flat", padx=12, pady=10).grid(row=1, column=2, padx=(0, 10))
        tk.Button(search_card, text="Add User", command=lambda: self.show(self.new_user_page), bg="#10b981", fg="white", relief="flat", padx=12, pady=10).grid(row=1, column=3)

        search_card.grid_columnconfigure(0, weight=2)
        search_card.grid_columnconfigure(1, weight=1)
        search_card.grid_columnconfigure(2, weight=0)
        search_card.grid_columnconfigure(3, weight=0)

        table_card = self.card(self.content)
        table_card.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        columns = ("ID", "Name", "City", "Barangay", "House ID")
        self.user_tree = ttk.Treeview(table_card, columns=columns, show="headings", selectmode="browse")
        for column in columns:
            self.user_tree.heading(column, text=column, command=lambda c=column: self.sort_users(c))
            self.user_tree.column(column, anchor="center", width=140)
        self.user_tree.pack(fill="both", expand=True)
        self.user_tree.bind("<Double-1>", lambda event: self.edit_selected_user())

        action_controls = tk.Frame(table_card, bg=self.CARD_BG)
        action_controls.pack(fill="x", pady=(10, 0))
        tk.Button(action_controls, text="Edit Selected", command=self.edit_selected_user, bg="#2563eb", fg="white", relief="flat", padx=14, pady=10).pack(side="left")
        tk.Button(action_controls, text="Delete Selected", command=self.delete_selected_user, bg="#ef4444", fg="white", relief="flat", padx=14, pady=10).pack(side="left", padx=10)

        self.load_user_table()

    def sort_users(self, column_name):
        mapping = {
            "ID": "user_id",
            "Name": "name",
            "City": "city",
            "Barangay": "barangay",
            "House ID": "house_id",
        }
        key = mapping.get(column_name, "user_id")
        if self.user_sort_by == key:
            self.user_sort_ascending = not self.user_sort_ascending
        else:
            self.user_sort_ascending = False
        self.user_sort_by = key
        self.load_user_table()

    def load_user_table(self):
        self.user_tree.delete(*self.user_tree.get_children())
        search_text = self.search_query.get().strip() or None
        city_filter = self.city_filter.get()
        if city_filter == "All":
            city_filter = None
        users = get_all_users(search_text=search_text, city_filter=city_filter, sort_by=self.user_sort_by, ascending=self.user_sort_ascending)
        for user in users:
            self.user_tree.insert(
                "",
                "end",
                values=(
                    user["user_id"],
                    user["name"],
                    user["city"],
                    user["barangay"],
                    user["house_id"],
                ),
            )

    def _build_user_form(self, parent, initial_data=None):
        fields = [
            ("Name", "name"),
            ("Province", "province"),
            ("City", "city"),
            ("Barangay", "barangay"),
            ("House ID", "house_id"),
            ("Address", "address"),
        ]
        values = {}
        for index, (label_text, field_name) in enumerate(fields):
            tk.Label(parent, text=label_text, bg=self.CARD_BG, fg=self.TEXT_COLOR, font=self.LABEL_FONT).grid(row=index, column=0, sticky="w", pady=(0, 6))
            entry = tk.Entry(parent, bg="#111827", fg="white", insertbackground="white", relief="flat", font=self.LABEL_FONT)
            entry.grid(row=index, column=1, sticky="ew", pady=(0, 6), padx=(10, 0))
            values[field_name] = entry
            if initial_data and field_name in initial_data:
                entry.insert(0, initial_data[field_name] or "")
        parent.grid_columnconfigure(1, weight=1)
        return values

    def new_user_page(self):
        self.header("Create New User")
        card = self.card(self.content)
        card.pack(fill="x", padx=20, pady=(0, 20))

        fields = self._build_user_form(card)

        def save():
            data = {name: entry.get().strip() for name, entry in fields.items()}
            if not required(data["name"]):
                messagebox.showerror("Validation", "Name is required.")
                return
            if not required(data["house_id"]):
                messagebox.showerror("Validation", "House ID is required.")
                return
            success, message = create_user(
                data["name"],
                data["province"],
                data["city"],
                data["barangay"],
                data["house_id"],
                data["address"],
            )
            if success:
                self.show_toast("User created successfully")
                self.show(self.users_page)
            else:
                messagebox.showerror("Error", message)

        tk.Button(card, text="Save User", command=save, bg="#10b981", fg="white", relief="flat", padx=14, pady=12).pack(anchor="e")

    def edit_selected_user(self):
        selected = self.user_tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a user first.")
            return
        item = self.user_tree.item(selected[0])
        user_id = item["values"][0]
        self.edit_user_window(user_id)

    def edit_user_window(self, user_id):
        user = get_user_by_id(user_id)
        if not user:
            messagebox.showerror("Error", "User not found.")
            return
        win = tk.Toplevel(self.root)
        win.title("Edit User")
        win.configure(bg=self.BG)
        win.geometry("520x420")
        win.transient(self.root)
        win.grab_set()

        card = self.card(win)
        card.pack(fill="both", expand=True, padx=20, pady=20)
        tk.Label(card, text="Edit User", bg=self.CARD_BG, fg=self.TEXT_COLOR, font=self.HEADER_FONT).pack(anchor="w", pady=(0, 10))
        form = self.card(card, bg=self.CARD_BG)
        form.pack(fill="both", expand=True)
        fields = self._build_user_form(form, initial_data=user)

        def save():
            data = {name: entry.get().strip() for name, entry in fields.items()}
            if not required(data["name"]):
                messagebox.showerror("Validation", "Name is required.")
                return
            if not required(data["house_id"]):
                messagebox.showerror("Validation", "House ID is required.")
                return
            success, message = update_user(
                user_id,
                data["name"],
                data["province"],
                data["city"],
                data["barangay"],
                data["house_id"],
                data["address"],
            )
            if success:
                win.destroy()
                self.show_toast("User updated successfully")
                self.load_user_table()
            else:
                messagebox.showerror("Error", message)

        tk.Button(card, text="Save Changes", command=save, bg="#2563eb", fg="white", relief="flat", padx=14, pady=12).pack(anchor="e", pady=10)

    def delete_selected_user(self):
        selected = self.user_tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a user first.")
            return
        user_id = self.user_tree.item(selected[0])["values"][0]

        def action():
            soft_delete_user(user_id)
            self.load_user_table()
            self.show_toast("User deleted")

        self.confirm_delete(action)

    def pickups_page(self):
        self.header("Pickup Scheduler")

        picker_card = self.card(self.content)
        picker_card.pack(fill="x", padx=20, pady=(0, 20))

        tk.Label(picker_card, text="Schedule date", bg=self.CARD_BG, fg=self.TEXT_COLOR, font=self.LABEL_FONT).grid(row=0, column=0, sticky="w")
        self.month_var = tk.IntVar(value=self.selected_date.month)
        self.year_var = tk.IntVar(value=self.selected_date.year)
        month_combo = ttk.Combobox(picker_card, values=list(range(1, 13)), textvariable=self.month_var, state="readonly", width=6)
        month_combo.grid(row=1, column=0, sticky="w", pady=10)
        year_combo = ttk.Combobox(picker_card, values=[self.selected_date.year, self.selected_date.year + 1], textvariable=self.year_var, state="readonly", width=8)
        year_combo.grid(row=1, column=1, sticky="w", padx=10, pady=10)
        tk.Button(picker_card, text="Refresh Calendar", command=self.build_calendar, bg="#2563eb", fg="white", relief="flat", padx=12, pady=10).grid(row=1, column=2, padx=10)
        picker_card.grid_columnconfigure(0, weight=0)
        picker_card.grid_columnconfigure(1, weight=0)
        picker_card.grid_columnconfigure(2, weight=1)

        calendar_container = self.card(self.content)
        calendar_container.pack(fill="x", padx=20, pady=(0, 20))
        self.calendar_frame = tk.Frame(calendar_container, bg=self.CARD_BG)
        self.calendar_frame.pack(fill="x")
        self.selected_date_label = tk.Label(calendar_container, text=f"Selected: {self.selected_date.isoformat()}", bg=self.CARD_BG, fg=self.TEXT_COLOR, font=self.LABEL_FONT)
        self.selected_date_label.pack(anchor="w", pady=(10, 0))
        self.build_calendar()

        booking_card = self.card(self.content)
        booking_card.pack(fill="x", padx=20, pady=(0, 20))
        tk.Label(booking_card, text="Schedule Pickup", bg=self.CARD_BG, fg=self.TEXT_COLOR, font=("Segoe UI", 16, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        tk.Label(booking_card, text="Selected Date:", bg=self.CARD_BG, fg=self.TEXT_COLOR, font=self.LABEL_FONT).grid(row=1, column=0, sticky="w", pady=(0, 6))
        self.selected_date_display = tk.Label(booking_card, text=self.selected_date.isoformat(), bg=self.CARD_BG, fg="#60a5fa", font=self.LABEL_FONT)
        self.selected_date_display.grid(row=1, column=1, sticky="w", pady=(0, 6))

        tk.Label(booking_card, text="User", bg=self.CARD_BG, fg=self.TEXT_COLOR, font=self.LABEL_FONT).grid(row=2, column=0, sticky="w", pady=(0, 6))
        self.user_selection = tk.StringVar()
        active_users = get_active_user_options()
        user_options = [f"{uid} - {name}" for uid, name in active_users]
        self.active_user_combo = ttk.Combobox(booking_card, values=user_options, textvariable=self.user_selection, state="readonly", font=self.LABEL_FONT)
        self.active_user_combo.grid(row=2, column=1, sticky="ew", pady=(0, 6), padx=(0, 10))

        tk.Label(booking_card, text="Time", bg=self.CARD_BG, fg=self.TEXT_COLOR, font=self.LABEL_FONT).grid(row=3, column=0, sticky="w", pady=(0, 6))
        self.time_entry = tk.Entry(booking_card, bg="#111827", fg="white", insertbackground="white", relief="flat", font=self.LABEL_FONT)
        self.time_entry.insert(0, "09:00")
        self.time_entry.grid(row=3, column=1, sticky="ew", pady=(0, 6))

        tk.Label(booking_card, text="Priority", bg=self.CARD_BG, fg=self.TEXT_COLOR, font=self.LABEL_FONT).grid(row=4, column=0, sticky="w", pady=(0, 6))
        self.priority_selection = tk.StringVar(value=PRIORITY_OPTIONS[0])
        ttk.Combobox(booking_card, values=PRIORITY_OPTIONS, textvariable=self.priority_selection, state="readonly", font=self.LABEL_FONT).grid(row=4, column=1, sticky="ew", pady=(0, 6))

        tk.Label(booking_card, text="Notes", bg=self.CARD_BG, fg=self.TEXT_COLOR, font=self.LABEL_FONT).grid(row=5, column=0, sticky="nw", pady=(0, 6))
        self.notes_entry = tk.Text(booking_card, height=4, bg="#111827", fg="white", insertbackground="white", relief="flat", font=self.LABEL_FONT)
        self.notes_entry.grid(row=5, column=1, sticky="ew", pady=(0, 6))

        tk.Button(booking_card, text="Schedule Pickup", command=self.schedule_pickup, bg="#10b981", fg="white", relief="flat", padx=14, pady=12).grid(row=6, column=1, sticky="e", pady=(10, 0))
        booking_card.grid_columnconfigure(1, weight=1)

        list_card = self.card(self.content)
        list_card.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        tk.Label(list_card, text="Scheduled Pickups", bg=self.CARD_BG, fg=self.TEXT_COLOR, font=self.HEADER_FONT).pack(anchor="w", pady=(0, 10))

        columns = ("ID", "User", "Time", "Priority", "Status")
        self.pickup_tree = ttk.Treeview(list_card, columns=columns, show="headings", selectmode="browse")
        for column in columns:
            self.pickup_tree.heading(column, text=column)
            self.pickup_tree.column(column, anchor="center", width=120)
        self.pickup_tree.pack(fill="both", expand=True)

        tree_actions = tk.Frame(list_card, bg=self.CARD_BG)
        tree_actions.pack(fill="x", pady=(10, 0))
        tk.Button(tree_actions, text="Update Status", command=self.update_selected_pickup_status, bg="#2563eb", fg="white", relief="flat", padx=14, pady=10).pack(side="left")
        tk.Button(tree_actions, text="Delete Pickup", command=self.delete_selected_pickup, bg="#ef4444", fg="white", relief="flat", padx=14, pady=10).pack(side="left", padx=10)

        self.load_pickup_table()

    def build_calendar(self):
        year = self.year_var.get()
        month = self.month_var.get()
        today = datetime.date.today()
        self.selected_date = self.selected_date if self.selected_date.month == month and self.selected_date.year == year else datetime.date(year, month, min(today.day, calendar.monthrange(year, month)[1]))
        self.selected_date_display.config(text=self.selected_date.isoformat())
        self.selected_date_label.config(text=f"Selected: {self.selected_date.isoformat()}")

        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for col, day_name in enumerate(days_of_week):
            tk.Label(self.calendar_frame, text=day_name, bg=self.CARD_BG, fg="#94a3b8", font=self.LABEL_FONT).grid(row=0, column=col, padx=4, pady=4)

        year = self.year_var.get()
        month = self.month_var.get()
        first_weekday, total_days = calendar.monthrange(year, month)
        month_dates = {row["date"]: [] for row in get_pickups_by_month(year, month)}
        for pickup in get_pickups_by_month(year, month):
            month_dates.setdefault(pickup["date"], []).append(pickup)

        day = 1
        row = 1
        for cell in range(first_weekday + total_days):
            column = cell % 7
            if cell < first_weekday:
                placeholder = tk.Label(self.calendar_frame, text="", bg=self.CARD_BG)
                placeholder.grid(row=row, column=column, padx=4, pady=4, sticky="nsew")
            else:
                current_date = datetime.date(year, month, day)
                date_key = current_date.isoformat()
                pickups = month_dates.get(date_key, [])
                color = self._color_for_day(pickups)
                text = str(day)
                button = tk.Button(
                    self.calendar_frame,
                    text=text,
                    bg=color,
                    fg="white",
                    width=4,
                    height=2,
                    relief="flat",
                    command=lambda d=day: self.select_date(year, month, d),
                )
                if current_date == self.selected_date:
                    button.configure(highlightthickness=2, highlightbackground="#2563eb")
                button.grid(row=row, column=column, padx=4, pady=4, sticky="nsew")
                day += 1
            if column == 6:
                row += 1

        for col in range(7):
            self.calendar_frame.grid_columnconfigure(col, weight=1)

    def _color_for_day(self, pickups):
        if not pickups:
            return "#10b981"
        statuses = {pickup["status"] for pickup in pickups}
        if "Pending" in statuses:
            return "#fbbf24"
        return "#ef4444"

    def select_date(self, year, month, day):
        self.selected_date = datetime.date(year, month, day)
        self.selected_date_display.config(text=self.selected_date.isoformat())
        self.selected_date_label.config(text=f"Selected: {self.selected_date.isoformat()}")
        self.build_calendar()
        self.load_pickup_table()

    def schedule_pickup(self):
        date_str = self.selected_date.isoformat()
        user_value = self.user_selection.get()
        if not user_value:
            messagebox.showwarning("Validation", "Please select a user.")
            return
        try:
            user_id = int(user_value.split(" - ")[0])
        except (ValueError, IndexError):
            messagebox.showwarning("Validation", "Please choose a valid user.")
            return

        time_value = self.time_entry.get().strip()
        if not validate_time(time_value):
            messagebox.showwarning("Validation", "Enter time as HH:MM.")
            return

        priority = self.priority_selection.get()
        if not validate_priority(priority):
            messagebox.showwarning("Validation", "Select a valid priority.")
            return

        notes = self.notes_entry.get("1.0", "end").strip()
        success, message = create_pickup(user_id, date_str, time_value, priority, notes)
        if success:
            self.show_toast("Pickup scheduled successfully")
            self.build_calendar()
            self.load_pickup_table()
            self.notes_entry.delete("1.0", "end")
        else:
            messagebox.showerror("Error", message)

    def load_pickup_table(self):
        if not self.pickup_tree:
            return
        self.pickup_tree.delete(*self.pickup_tree.get_children())
        date_str = self.selected_date.isoformat()
        pickups = get_pickups_by_date(date_str)
        for pickup in pickups:
            self.pickup_tree.insert(
                "",
                "end",
                values=(
                    pickup["pickup_id"],
                    pickup["user_name"],
                    pickup["time"],
                    pickup["priority"],
                    pickup["status"],
                ),
            )

    def update_selected_pickup_status(self):
        selected = self.pickup_tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a pickup first.")
            return
        item = self.pickup_tree.item(selected[0])["values"]
        pickup_id, _, _, _, current_status = item
        current_index = STATUS_FLOW.index(current_status)
        if current_index >= len(STATUS_FLOW) - 1:
            messagebox.showinfo("Status", "This pickup is already completed.")
            return

        allowed = STATUS_FLOW[current_index + 1:]
        win = tk.Toplevel(self.root)
        win.title("Update Status")
        win.configure(bg=self.BG)
        win.geometry("360x180")
        win.transient(self.root)
        win.grab_set()

        card = self.card(win)
        card.pack(fill="both", expand=True, padx=20, pady=20)
        tk.Label(card, text="Update Pickup Status", bg=self.CARD_BG, fg=self.TEXT_COLOR, font=self.HEADER_FONT).pack(anchor="w", pady=(0, 10))
        status_var = tk.StringVar(value=allowed[0])
        ttk.Combobox(card, values=allowed, textvariable=status_var, state="readonly", font=self.LABEL_FONT).pack(fill="x", pady=(0, 10))

        def save():
            new_status = status_var.get()
            success, message = update_pickup_status(pickup_id, new_status)
            if success:
                win.destroy()
                self.show_toast("Pickup status updated")
                self.load_pickup_table()
                self.build_calendar()
            else:
                messagebox.showerror("Error", message)

        tk.Button(card, text="Save", command=save, bg="#2563eb", fg="white", relief="flat", padx=14, pady=10).pack(anchor="e")

    def delete_selected_pickup(self):
        selected = self.pickup_tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a pickup first.")
            return
        pickup_id = self.pickup_tree.item(selected[0])["values"][0]

        def action():
            soft_delete_pickup(pickup_id)
            self.load_pickup_table()
            self.build_calendar()
            self.show_toast("Pickup deleted")

        self.confirm_delete(action)

    def start(self):
        self.root.mainloop()


def run_app():
    WasteSystemApp().start()
