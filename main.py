import customtkinter as ctk
from tkinter import messagebox
from datetime import date
from calendar import month_name

import database
import charts



# Setup


database.create_database()

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


current_year = date.today().year
current_month = date.today().month

current_page = "dashboard"



# Colors


BG_COLOR = "#202326"
SIDEBAR_COLOR = "#17191C"
CARD_COLOR = "#292D32"
TEXT_SECONDARY = "#A8ADB5"
GREEN = "#4ADE80"
RED = "#F87171"
BLUE = "#2F6FED"



# Main window


app = ctk.CTk()

app.title("Finora")
app.geometry("1200x750")
app.minsize(1000, 650)

app.configure(
    fg_color=BG_COLOR
)



# Helper functions


def get_current_transactions():
    return database.get_transactions_for_month(
        current_year,
        current_month
    )


def get_financial_totals():
    transactions = get_current_transactions()

    income = 0
    expenses = 0

    for transaction in transactions:
        amount = transaction[1]

        if transaction[2] == "income":
            income += amount
        else:
            expenses += amount

    return income, expenses, income - expenses


def clear_main_area():
    for widget in main_area.winfo_children():
        widget.destroy()


def format_amount(amount):
    return f"€ {amount:,.2f}"


def refresh():
    show_page(current_page)



# Month navigation


def previous_month():
    global current_year
    global current_month

    current_month -= 1

    if current_month == 0:
        current_month = 12
        current_year -= 1

    refresh()


def next_month():
    global current_year
    global current_month

    current_month += 1

    if current_month == 13:
        current_month = 1
        current_year += 1

    refresh()


def create_month_selector(parent):
    frame = ctk.CTkFrame(
        parent,
        fg_color="transparent"
    )

    frame.pack(
        fill="x",
        pady=(0, 20)
    )

    previous_button = ctk.CTkButton(
        frame,
        text="‹",
        width=40,
        height=35,
        command=previous_month
    )

    previous_button.pack(
        side="left"
    )

    month_label = ctk.CTkLabel(
        frame,
        text=f"{month_name[current_month]} {current_year}",
        font=ctk.CTkFont(
            size=16,
            weight="bold"
        )
    )

    month_label.pack(
        side="left",
        padx=15
    )

    next_button = ctk.CTkButton(
        frame,
        text="›",
        width=40,
        height=35,
        command=next_month
    )

    next_button.pack(
        side="left"
    )

    return frame



# Transaction window


def open_transaction_window(transaction_id=None):

    editing = transaction_id is not None

    window = ctk.CTkToplevel(app)

    window.title(
        "Edit Transaction"
        if editing
        else "Add Transaction"
    )

    window.geometry("450x600")
    window.resizable(False, False)

    window.grab_set()

    existing = None

    if editing:
        existing = database.get_transaction(
            transaction_id
        )

        if not existing:
            window.destroy()
            return


    title = ctk.CTkLabel(
        window,
        text="Edit Transaction"
        if editing
        else "Add Transaction",
        font=ctk.CTkFont(
            size=24,
            weight="bold"
        )
    )

    title.pack(
        pady=(30, 25)
    )


    # Type
    ctk.CTkLabel(
        window,
        text="Type"
    ).pack(
        anchor="w",
        padx=40
    )

    type_menu = ctk.CTkOptionMenu(
        window,
        values=[
            "Expense",
            "Income"
        ],
        width=370
    )

    type_menu.pack(
        padx=40,
        pady=(5, 15)
    )


    # Amount
    ctk.CTkLabel(
        window,
        text="Amount"
    ).pack(
        anchor="w",
        padx=40
    )

    amount_entry = ctk.CTkEntry(
        window,
        width=370,
        placeholder_text="e.g. 49.99"
    )

    amount_entry.pack(
        padx=40,
        pady=(5, 15)
    )


    # Category
    ctk.CTkLabel(
        window,
        text="Category"
    ).pack(
        anchor="w",
        padx=40
    )

    category_menu = ctk.CTkOptionMenu(
        window,
        values=[
            "Food",
            "Housing",
            "Transportation",
            "Entertainment",
            "Shopping",
            "Bills",
            "Health",
            "Salary",
            "Freelance",
            "Gift",
            "Other"
        ],
        width=370
    )

    category_menu.pack(
        padx=40,
        pady=(5, 15)
    )


    # Date
    ctk.CTkLabel(
        window,
        text="Date"
    ).pack(
        anchor="w",
        padx=40
    )

    date_entry = ctk.CTkEntry(
        window,
        width=370
    )

    date_entry.pack(
        padx=40,
        pady=(5, 15)
    )


    # Description
    ctk.CTkLabel(
        window,
        text="Description"
    ).pack(
        anchor="w",
        padx=40
    )

    description_entry = ctk.CTkEntry(
        window,
        width=370,
        placeholder_text="Optional"
    )

    description_entry.pack(
        padx=40,
        pady=(5, 25)
    )


    # Fill existing data
    if existing:
        amount = existing[1]
        transaction_type = existing[2]
        category = existing[3]
        transaction_date = existing[4]
        description = existing[5] or ""

        type_menu.set(
            transaction_type.capitalize()
        )

        amount_entry.insert(
            0,
            str(amount)
        )

        category_menu.set(
            category
        )

        date_entry.insert(
            0,
            transaction_date
        )

        description_entry.insert(
            0,
            description
        )

    else:
        date_entry.insert(
            0,
            date.today().isoformat()
        )


    def save():

        try:
            amount = float(
                amount_entry.get().replace(",", ".")
            )
        except ValueError:
            messagebox.showerror(
                "Invalid amount",
                "Please enter a valid amount."
            )
            return

        if amount <= 0:
            messagebox.showerror(
                "Invalid amount",
                "The amount must be greater than zero."
            )
            return


        transaction_type = type_menu.get().lower()
        category = category_menu.get()
        transaction_date = date_entry.get().strip()
        description = description_entry.get().strip()


        try:
            date.fromisoformat(
                transaction_date
            )
        except ValueError:
            messagebox.showerror(
                "Invalid date",
                "Please use the format YYYY-MM-DD."
            )
            return


        if editing:
            database.update_transaction(
                transaction_id,
                amount,
                transaction_type,
                category,
                transaction_date,
                description
            )
        else:
            database.add_transaction(
                amount,
                transaction_type,
                category,
                transaction_date,
                description
            )


        window.destroy()
        refresh()


    button_text = (
        "Save Changes"
        if editing
        else "Add Transaction"
    )

    ctk.CTkButton(
        window,
        text=button_text,
        width=370,
        height=45,
        command=save
    ).pack(
        padx=40
    )



# Delete transaction


def delete_transaction(transaction_id):

    answer = messagebox.askyesno(
        "Delete Transaction",
        "Are you sure you want to delete this transaction?"
    )

    if not answer:
        return

    database.delete_transaction(
        transaction_id
    )

    refresh()



# Dashboard


def show_dashboard():

    clear_main_area()

    content = ctk.CTkScrollableFrame(
        main_area,
        fg_color="transparent"
    )

    content.pack(
        fill="both",
        expand=True,
        padx=35,
        pady=30
    )


    name = database.get_setting("name")

    if name:
        greeting = f"Hello, {name}!"
    else:
        greeting = "Hello!"


    ctk.CTkLabel(
        content,
        text=greeting,
        font=ctk.CTkFont(
            size=28,
            weight="bold"
        )
    ).pack(
        anchor="w"
    )


    ctk.CTkLabel(
        content,
        text=(
            f"Here's your financial overview for "
            f"{month_name[current_month]} {current_year}"
        ),
        text_color=TEXT_SECONDARY,
        font=ctk.CTkFont(size=15)
    ).pack(
        anchor="w",
        pady=(5, 20)
    )


    create_month_selector(content)


    income, expenses, balance = get_financial_totals()


    cards = ctk.CTkFrame(
        content,
        fg_color="transparent"
    )

    cards.pack(
        fill="x",
        pady=(0, 25)
    )


    create_summary_card(
        cards,
        "CURRENT BALANCE",
        format_amount(balance),
        "#FFFFFF"
    ).pack(
        side="left",
        fill="both",
        expand=True,
        padx=(0, 8)
    )


    create_summary_card(
        cards,
        "INCOME",
        format_amount(income),
        GREEN
    ).pack(
        side="left",
        fill="both",
        expand=True,
        padx=8
    )


    create_summary_card(
        cards,
        "EXPENSES",
        format_amount(expenses),
        RED
    ).pack(
        side="left",
        fill="both",
        expand=True,
        padx=(8, 0)
    )


    # Charts
    chart_frame = ctk.CTkFrame(
        content,
        fg_color="transparent"
    )

    chart_frame.pack(
        fill="both",
        expand=True
    )


    line_frame = ctk.CTkFrame(
        chart_frame,
        fg_color=CARD_COLOR,
        corner_radius=12
    )

    line_frame.pack(
        side="left",
        fill="both",
        expand=True,
        padx=(0, 8)
    )


    ctk.CTkLabel(
        line_frame,
        text="Income vs. Expenses",
        font=ctk.CTkFont(
            size=18,
            weight="bold"
        )
    ).pack(
        anchor="w",
        padx=20,
        pady=(15, 0)
    )


    figure, canvas = charts.create_income_expense_chart(
        line_frame,
        get_current_transactions()
    )

    canvas.get_tk_widget().pack(
        fill="both",
        expand=True,
        padx=10,
        pady=10
    )


    pie_frame = ctk.CTkFrame(
        chart_frame,
        fg_color=CARD_COLOR,
        corner_radius=12
    )

    pie_frame.pack(
        side="left",
        fill="both",
        expand=True,
        padx=(8, 0)
    )


    ctk.CTkLabel(
        pie_frame,
        text="Expenses by Category",
        font=ctk.CTkFont(
            size=18,
            weight="bold"
        )
    ).pack(
        anchor="w",
        padx=20,
        pady=(15, 0)
    )


    figure2, canvas2 = charts.create_category_chart(
        pie_frame,
        get_current_transactions()
    )

    canvas2.get_tk_widget().pack(
        fill="both",
        expand=True,
        padx=10,
        pady=10
    )



# Summary cards


def create_summary_card(
    parent,
    title,
    value,
    color
):
    card = ctk.CTkFrame(
        parent,
        fg_color=CARD_COLOR,
        corner_radius=12,
        height=110
    )

    ctk.CTkLabel(
        card,
        text=title,
        text_color=TEXT_SECONDARY,
        font=ctk.CTkFont(
            size=12,
            weight="bold"
        )
    ).pack(
        anchor="w",
        padx=18,
        pady=(18, 3)
    )


    ctk.CTkLabel(
        card,
        text=value,
        text_color=color,
        font=ctk.CTkFont(
            size=23,
            weight="bold"
        )
    ).pack(
        anchor="w",
        padx=18
    )

    return card



# Transactions page


def show_transactions():

    clear_main_area()

    content = ctk.CTkFrame(
        main_area,
        fg_color="transparent"
    )

    content.pack(
        fill="both",
        expand=True,
        padx=35,
        pady=30
    )


    ctk.CTkLabel(
        content,
        text="Transactions",
        font=ctk.CTkFont(
            size=28,
            weight="bold"
        )
    ).pack(
        anchor="w"
    )


    ctk.CTkLabel(
        content,
        text=(
            f"Transactions for "
            f"{month_name[current_month]} {current_year}"
        ),
        text_color=TEXT_SECONDARY
    ).pack(
        anchor="w",
        pady=(5, 15)
    )


    top = ctk.CTkFrame(
        content,
        fg_color="transparent"
    )

    top.pack(
        fill="x"
    )


    create_month_selector(top)


    ctk.CTkButton(
        top,
        text="+ Add Transaction",
        width=170,
        command=open_transaction_window
    ).pack(
        side="right",
        pady=(0, 20)
    )


    list_frame = ctk.CTkScrollableFrame(
        content,
        fg_color="transparent"
    )

    list_frame.pack(
        fill="both",
        expand=True
    )


    transactions = get_current_transactions()


    if not transactions:
        ctk.CTkLabel(
            list_frame,
            text="No transactions for this month.",
            text_color=TEXT_SECONDARY,
            font=ctk.CTkFont(size=15)
        ).pack(
            pady=50
        )

        return


    for transaction in transactions:

        create_transaction_row(
            list_frame,
            transaction
        )


def create_transaction_row(
    parent,
    transaction
):

    transaction_id = transaction[0]
    amount = transaction[1]
    transaction_type = transaction[2]
    category = transaction[3]
    transaction_date = transaction[4]
    description = transaction[5]


    row = ctk.CTkFrame(
        parent,
        fg_color=CARD_COLOR,
        corner_radius=10,
        height=70
    )

    row.pack(
        fill="x",
        pady=5
    )


    name = description or category


    ctk.CTkLabel(
        row,
        text=name,
        font=ctk.CTkFont(
            size=14,
            weight="bold"
        )
    ).pack(
        side="left",
        padx=15
    )


    ctk.CTkLabel(
        row,
        text=category,
        text_color=TEXT_SECONDARY
    ).pack(
        side="left",
        padx=15
    )


    ctk.CTkLabel(
        row,
        text=transaction_date,
        text_color=TEXT_SECONDARY
    ).pack(
        side="left",
        padx=15
    )


    prefix = "+" if transaction_type == "income" else "-"
    color = GREEN if transaction_type == "income" else RED


    ctk.CTkLabel(
        row,
        text=f"{prefix} {format_amount(amount)}",
        text_color=color,
        font=ctk.CTkFont(
            size=14,
            weight="bold"
        )
    ).pack(
        side="right",
        padx=15
    )


    ctk.CTkButton(
        row,
        text="Delete",
        width=70,
        height=30,
        fg_color="#7F1D1D",
        hover_color="#991B1B",
        command=lambda: delete_transaction(
            transaction_id
        )
    ).pack(
        side="right",
        padx=5
    )


    ctk.CTkButton(
        row,
        text="Edit",
        width=60,
        height=30,
        command=lambda: open_transaction_window(
            transaction_id
        )
    ).pack(
        side="right",
        padx=5
    )



# Analytics page


def show_analytics():

    clear_main_area()

    content = ctk.CTkScrollableFrame(
        main_area,
        fg_color="transparent"
    )

    content.pack(
        fill="both",
        expand=True,
        padx=35,
        pady=30
    )


    ctk.CTkLabel(
        content,
        text="Analytics",
        font=ctk.CTkFont(
            size=28,
            weight="bold"
        )
    ).pack(
        anchor="w"
    )


    ctk.CTkLabel(
        content,
        text=(
            f"Financial analysis for "
            f"{month_name[current_month]} {current_year}"
        ),
        text_color=TEXT_SECONDARY
    ).pack(
        anchor="w",
        pady=(5, 20)
    )


    create_month_selector(content)


    transactions = get_current_transactions()

    income, expenses, balance = get_financial_totals()


    stats = ctk.CTkFrame(
        content,
        fg_color="transparent"
    )

    stats.pack(
        fill="x",
        pady=(0, 20)
    )


    create_summary_card(
        stats,
        "INCOME",
        format_amount(income),
        GREEN
    ).pack(
        side="left",
        fill="both",
        expand=True,
        padx=(0, 8)
    )


    create_summary_card(
        stats,
        "EXPENSES",
        format_amount(expenses),
        RED
    ).pack(
        side="left",
        fill="both",
        expand=True,
        padx=8
    )


    create_summary_card(
        stats,
        "BALANCE",
        format_amount(balance),
        "#FFFFFF"
    ).pack(
        side="left",
        fill="both",
        expand=True,
        padx=(8, 0)
    )


    chart_box = ctk.CTkFrame(
        content,
        fg_color=CARD_COLOR,
        corner_radius=12
    )

    chart_box.pack(
        fill="both",
        expand=True
    )


    ctk.CTkLabel(
        chart_box,
        text="Income vs. Expenses",
        font=ctk.CTkFont(
            size=18,
            weight="bold"
        )
    ).pack(
        anchor="w",
        padx=20,
        pady=(15, 0)
    )


    figure, canvas = charts.create_income_expense_chart(
        chart_box,
        transactions
    )

    canvas.get_tk_widget().pack(
        fill="both",
        expand=True,
        padx=10,
        pady=10
    )



# Settings


def show_settings():

    clear_main_area()

    content = ctk.CTkFrame(
        main_area,
        fg_color="transparent"
    )

    content.pack(
        fill="both",
        expand=True,
        padx=35,
        pady=30
    )


    ctk.CTkLabel(
        content,
        text="Settings",
        font=ctk.CTkFont(
            size=28,
            weight="bold"
        )
    ).pack(
        anchor="w"
    )


    ctk.CTkLabel(
        content,
        text="Customize your Finora experience.",
        text_color=TEXT_SECONDARY
    ).pack(
        anchor="w",
        pady=(5, 25)
    )


    # Profile
    profile = ctk.CTkFrame(
        content,
        fg_color=CARD_COLOR,
        corner_radius=12
    )

    profile.pack(
        fill="x",
        pady=(0, 15)
    )


    ctk.CTkLabel(
        profile,
        text="Profile",
        font=ctk.CTkFont(
            size=18,
            weight="bold"
        )
    ).pack(
        anchor="w",
        padx=20,
        pady=(20, 10)
    )


    ctk.CTkLabel(
        profile,
        text="Your name",
        text_color=TEXT_SECONDARY
    ).pack(
        anchor="w",
        padx=20
    )


    name_entry = ctk.CTkEntry(
        profile,
        width=350
    )

    name_entry.pack(
        anchor="w",
        padx=20,
        pady=8
    )


    current_name = database.get_setting("name")

    if current_name:
        name_entry.insert(
            0,
            current_name
        )


    def save_name():

        name = name_entry.get().strip()

        if not name:
            messagebox.showerror(
                "Invalid name",
                "Please enter your name."
            )
            return

        database.save_setting(
            "name",
            name
        )

        messagebox.showinfo(
            "Saved",
            "Your name has been saved."
        )


    ctk.CTkButton(
        profile,
        text="Save Name",
        width=140,
        command=save_name
    ).pack(
        anchor="w",
        padx=20,
        pady=(0, 20)
    )


    # Appearance
    appearance = ctk.CTkFrame(
        content,
        fg_color=CARD_COLOR,
        corner_radius=12
    )

    appearance.pack(
        fill="x"
    )


    ctk.CTkLabel(
        appearance,
        text="Appearance",
        font=ctk.CTkFont(
            size=18,
            weight="bold"
        )
    ).pack(
        anchor="w",
        padx=20,
        pady=(20, 10)
    )


    ctk.CTkLabel(
        appearance,
        text="Theme",
        text_color=TEXT_SECONDARY
    ).pack(
        anchor="w",
        padx=20
    )


    theme_menu = ctk.CTkOptionMenu(
        appearance,
        values=[
            "Dark",
            "Light",
            "System"
        ],
        width=200
    )

    theme_menu.pack(
        anchor="w",
        padx=20,
        pady=8
    )


    saved_theme = database.get_setting("theme")

    if saved_theme:
        theme_menu.set(
            saved_theme.capitalize()
        )
    else:
        theme_menu.set("Dark")


    def change_theme(value):

        database.save_setting(
            "theme",
            value.lower()
        )

        ctk.set_appearance_mode(
            value
        )


    theme_menu.configure(
        command=change_theme
    )



# First launch


def check_first_launch():

    name = database.get_setting("name")

    if name:
        return


    window = ctk.CTkToplevel(app)

    window.title("Welcome to Finora")
    window.geometry("450x300")
    window.resizable(False, False)

    window.grab_set()


    ctk.CTkLabel(
        window,
        text="Welcome to Finora",
        font=ctk.CTkFont(
            size=25,
            weight="bold"
        )
    ).pack(
        pady=(40, 10)
    )


    ctk.CTkLabel(
        window,
        text="What should Finora call you?"
    ).pack(
        pady=5
    )


    name_entry = ctk.CTkEntry(
        window,
        width=320,
        placeholder_text="Your name"
    )

    name_entry.pack(
        pady=15
    )


    def save():

        name = name_entry.get().strip()

        if not name:
            messagebox.showerror(
                "Missing name",
                "Please enter your name."
            )
            return


        database.save_setting(
            "name",
            name
        )

        window.destroy()

        show_dashboard()


    ctk.CTkButton(
        window,
        text="Continue",
        width=320,
        height=40,
        command=save
    ).pack(
        pady=10
    )



# Page navigation

def show_page(page):

    global current_page

    current_page = page

    if page == "dashboard":
        show_dashboard()

    elif page == "transactions":
        show_transactions()

    elif page == "analytics":
        show_analytics()

    elif page == "settings":
        show_settings()



# Sidebar


sidebar = ctk.CTkFrame(
    app,
    width=220,
    corner_radius=0,
    fg_color=SIDEBAR_COLOR
)

sidebar.pack(
    side="left",
    fill="y"
)

sidebar.pack_propagate(False)


ctk.CTkLabel(
    sidebar,
    text="FINORA",
    font=ctk.CTkFont(
        size=24,
        weight="bold"
    )
).pack(
    pady=(35, 45)
)


def sidebar_button(
    text,
    page
):
    return ctk.CTkButton(
        sidebar,
        text=text,
        anchor="w",
        height=45,
        corner_radius=8,
        fg_color="transparent",
        hover_color="#25282C",
        command=lambda: show_page(page)
    )


sidebar_button(
    "  Dashboard",
    "dashboard"
).pack(
    fill="x",
    padx=20,
    pady=5
)


sidebar_button(
    "  Transactions",
    "transactions"
).pack(
    fill="x",
    padx=20,
    pady=5
)


sidebar_button(
    "  Analytics",
    "analytics"
).pack(
    fill="x",
    padx=20,
    pady=5
)


sidebar_button(
    "  Settings",
    "settings"
).pack(
    side="bottom",
    fill="x",
    padx=20,
    pady=25
)



# Main area


main_area = ctk.CTkFrame(
    app,
    corner_radius=0,
    fg_color=BG_COLOR
)

main_area.pack(
    side="left",
    fill="both",
    expand=True
)



# Start


show_dashboard()

app.after(
    300,
    check_first_launch
)

app.mainloop()