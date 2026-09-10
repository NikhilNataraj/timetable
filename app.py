import json
from datetime import datetime, date, timedelta
from collections import defaultdict
from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Class Calendar</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-100 min-h-screen p-4 md:p-6 font-sans text-slate-800">
    <div class="max-w-[1500px] mx-auto">
        <div class="bg-white rounded-2xl shadow-sm border border-slate-200 p-4 md:p-6">
            <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-6">
                <div>
                    <h1 class="text-2xl font-bold">Class Calendar</h1>
                    <p class="text-sm text-slate-500 mt-1">1 September 2026 to 30 November 2026</p>
                </div>
                <div class="flex flex-wrap gap-2 text-xs font-semibold">
                    {% for subject, style in subject_styles.items() %}
                    <span class="flex items-center gap-1.5 px-2 py-1 rounded-full bg-slate-50">
                        <span class="w-2.5 h-2.5 rounded-full {{ style.dot }}"></span>
                        {{ subject }}
                    </span>
                    {% endfor %}
                </div>
            </div>

            {% for month in months %}
            <section class="mb-8 last:mb-0">
                <div class="flex items-center justify-between mb-3">
                    <h2 class="text-lg font-bold">{{ month.title }}</h2>
                    <span class="text-xs text-slate-400">{{ month.class_count }} classes</span>
                </div>

                <div class="overflow-x-auto rounded-xl border border-slate-200">
                    <div class="min-w-[980px]">
                        <div class="grid grid-cols-7 bg-slate-50 border-b border-slate-200">
                            {% for day_name in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"] %}
                            <div class="px-3 py-2 text-xs font-bold uppercase text-center {% if day_name == 'Sunday' %}text-red-600 bg-red-50{% else %}text-slate-500{% endif %}">
                                {{ day_name }}
                            </div>
                            {% endfor %}
                        </div>

                        <div class="grid grid-cols-7 auto-rows-fr">
                            {% for cell in month.cells %}
                            <div class="min-h-[150px] border-r border-b border-slate-200 p-2 {% if cell.is_sunday %}bg-red-50/60{% else %}bg-white{% endif %} {% if not cell.in_range %}bg-slate-50 text-slate-300{% endif %}">
                                <div class="flex items-center justify-between mb-2">
                                    <span class="text-sm font-bold {% if cell.is_sunday and cell.in_range %}text-red-600{% elif not cell.in_range %}text-slate-300{% else %}text-slate-700{% endif %}">
                                        {{ cell.day_number }}
                                    </span>
                                    {% if cell.is_sunday and cell.in_range %}
                                    <span class="text-[9px] font-bold uppercase tracking-wide text-red-500 bg-red-100 px-1.5 py-0.5 rounded">Sunday</span>
                                    {% endif %}
                                </div>

                                <div class="space-y-1.5">
                                    {% for session in cell.sessions %}
                                    <div class="rounded-lg border p-2 {{ session.style.bg }} {{ session.style.border }} {{ session.style.text }}">
                                        <div class="text-[10px] font-semibold opacity-70 mb-0.5">{{ session.time }}</div>
                                        <div class="text-xs font-bold leading-tight">{{ session.subject }}</div>
                                    </div>
                                    {% endfor %}
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                </div>
            </section>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

SUBJECT_STYLES = {
    "Financial Modeling using Excel": {"bg": "bg-blue-50", "border": "border-blue-200", "text": "text-blue-900", "dot": "bg-blue-500"},
    "Sales and Distribution Management": {"bg": "bg-purple-50", "border": "border-purple-200", "text": "text-purple-900", "dot": "bg-purple-500"},
    "Gales of Creative Destruction - Managing Innovation": {"bg": "bg-yellow-50", "border": "border-yellow-200", "text": "text-yellow-900", "dot": "bg-yellow-500"},
    "International Business Models for the Circular Economy": {"bg": "bg-green-50", "border": "border-green-200", "text": "text-green-900", "dot": "bg-green-500"}
}
DEFAULT_STYLE = {"bg": "bg-slate-50", "border": "border-slate-200", "text": "text-slate-800", "dot": "bg-slate-500"}

def parse_day(value):
    value = value.replace("Sept", "Sep")
    return datetime.strptime(value, "%a, %d %b %Y").date()


def month_start(d):
    return d.replace(day=1)

def next_month(d):
    return d.replace(year=d.year + (1 if d.month == 12 else 0), month=1 if d.month == 12 else d.month + 1, day=1)

def build_month_cells(year, month, sessions_by_date, start_date, end_date):
    first = date(year, month, 1)
    next_first = next_month(first)
    days_in_month = (next_first - first).days
    leading_blank_days = first.weekday()
    total_cells = ((leading_blank_days + days_in_month + 6) // 7) * 7
    cells = []

    for i in range(total_cells):
        day_offset = i - leading_blank_days
        cell_date = first + timedelta(days=day_offset)
        in_month = 0 <= day_offset < days_in_month
        in_range = start_date <= cell_date <= end_date
        sessions = []

        if in_month and in_range:
            for item in sessions_by_date.get(cell_date, []):
                sessions.append({
                    "time": item["time"],
                    "subject": item["subject"],
                    "style": SUBJECT_STYLES.get(item["subject"], DEFAULT_STYLE)
                })

        cells.append({
            "day_number": cell_date.day,
            "is_sunday": cell_date.weekday() == 6,
            "in_range": in_range and in_month,
            "sessions": sessions
        })
    return cells

@app.route("/")
def index():
    try:
        with open("timetable.json", "r", encoding="utf-8") as f:
            items = json.load(f)
    except FileNotFoundError:
        items = []

    sessions_by_date = defaultdict(list)
    for item in items:
        try:
            sessions_by_date[parse_day(item["day"])].append(item)
        except (KeyError, ValueError):
            continue

    if sessions_by_date:
        earliest = min(sessions_by_date)
        latest = max(sessions_by_date)
        start_date = min(month_start(earliest), date(2026, 9, 1))
        end_date = max(next_month(month_start(latest)) - timedelta(days=1), date(2026, 11, 30))
    else:
        start_date, end_date = date(2026, 9, 1), date(2026, 11, 30)

    for sessions in sessions_by_date.values():
        sessions.sort(key=lambda x: x.get("time", ""))

    months = []
    cursor = start_date
    while cursor <= end_date:
        cells = build_month_cells(cursor.year, cursor.month, sessions_by_date, start_date, end_date)
        months.append({
            "title": cursor.strftime("%B %Y"),
            "cells": cells,
            "class_count": sum(len(c["sessions"]) for c in cells)
        })
        cursor = next_month(cursor)

    return render_template_string(HTML_TEMPLATE, months=months, subject_styles=SUBJECT_STYLES)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)