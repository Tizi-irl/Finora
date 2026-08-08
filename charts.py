from collections import defaultdict

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def create_income_expense_chart(parent, transactions):
    income_by_day = defaultdict(float)
    expense_by_day = defaultdict(float)

    for transaction in transactions:
        transaction_date = transaction[4]
        day = int(transaction_date.split("-")[2])

        amount = transaction[1]
        transaction_type = transaction[2]

        if transaction_type == "income":
            income_by_day[day] += amount
        else:
            expense_by_day[day] += amount

    days = sorted(
        set(income_by_day.keys()) |
        set(expense_by_day.keys())
    )

    if not days:
        days = [1]

    income_values = [
        income_by_day.get(day, 0)
        for day in days
    ]

    expense_values = [
        expense_by_day.get(day, 0)
        for day in days
    ]

    figure, axis = plt.subplots(
        figsize=(7, 3.5),
        dpi=100
    )

    figure.patch.set_facecolor("#292D32")
    axis.set_facecolor("#292D32")

    axis.plot(
        days,
        income_values,
        color="#4ADE80",
        linewidth=2.5,
        marker="o",
        markersize=4,
        label="Income"
    )

    axis.plot(
        days,
        expense_values,
        color="#F87171",
        linewidth=2.5,
        marker="o",
        markersize=4,
        label="Expenses"
    )

    axis.set_xlabel(
        "Day",
        color="#A8ADB5"
    )

    axis.set_ylabel(
        "Amount (€)",
        color="#A8ADB5"
    )

    axis.tick_params(
        colors="#A8ADB5"
    )

    for spine in axis.spines.values():
        spine.set_color("#3A3F45")

    axis.grid(
        color="#3A3F45",
        alpha=0.5
    )

    axis.legend(
        facecolor="#292D32",
        edgecolor="#292D32",
        labelcolor="white"
    )

    figure.tight_layout()

    canvas = FigureCanvasTkAgg(
        figure,
        master=parent
    )

    canvas.draw()

    return figure, canvas


def create_category_chart(parent, transactions):
    category_totals = defaultdict(float)

    for transaction in transactions:
        if transaction[2] != "expense":
            continue

        category = transaction[3]
        amount = transaction[1]

        category_totals[category] += amount

    figure, axis = plt.subplots(
        figsize=(5, 3.5),
        dpi=100
    )

    figure.patch.set_facecolor("#292D32")
    axis.set_facecolor("#292D32")

    if not category_totals:
        axis.text(
            0.5,
            0.5,
            "No expenses yet",
            color="#A8ADB5",
            ha="center",
            va="center",
            fontsize=12
        )

        axis.axis("off")

    else:
        labels = list(category_totals.keys())
        values = list(category_totals.values())

        colors = [
            "#4F7CFF",
            "#8B5CF6",
            "#06B6D4",
            "#22C55E",
            "#F59E0B",
            "#EF4444",
            "#EC4899",
            "#14B8A6",
            "#F97316",
            "#64748B"
        ]

        axis.pie(
            values,
            labels=labels,
            colors=colors[:len(values)],
            autopct="%1.0f%%",
            startangle=90,
            textprops={
                "color": "white"
            }
        )

    figure.tight_layout()

    canvas = FigureCanvasTkAgg(
        figure,
        master=parent
    )

    canvas.draw()

    return figure, canvas