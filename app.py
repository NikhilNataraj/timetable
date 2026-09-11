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
    <style>
        /* Hide scrollbar for Chrome, Safari and Opera */
        .no-scrollbar::-webkit-scrollbar {
            display: none;
        }
        /* Hide scrollbar for IE, Edge and Firefox */
        .no-scrollbar {
            -ms-overflow-style: none;  /* IE and Edge */
            scrollbar-width: none;  /* Firefox */
        }
    </style>
</head>
<body class="bg-slate-100 min-h-screen p-4 md:p-6 font-sans text-slate-800">
    <div class="max-w-[1500px] mx-auto">
        <div class="bg-white rounded-2xl shadow-sm border border-slate-200 p-4 md:p-6">
            <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-6">
                <div>
                    <h1 class="text-2xl font-bold">Class Calendar</h1>
                    <p class="text-sm text-slate-500 mt-1">{{ subtitle_range }}</p>
                </div>
                <div class="flex flex-wrap gap-2 text-xs font-semibold">
                    {% for subject, style in subject_styles.items() %}
                    <span class="flex items-center gap-1.5 px-2 py-1 rounded-full bg-slate-50 border border-slate-200">
                        <span class="w-2.5 h-2.5 rounded-full {{ style.dot }}"></span>
                        {{ subject }}
                    </span>
                    {% endfor %}
                </div>
            </div>

            {% for month in months %}
            <section class="mb-10 last:mb-0">
                <div class="flex items-center justify-between mb-3">
                    <h2 class="text-lg font-bold text-slate-800">{{ month.title }}</h2>
                    <span class="text-xs text-slate-400">{{ month.class_count }} classes</span>
                </div>

                <!-- Desktop View (Original Grid Layout) -->
                <div class="hidden md:block overflow-x-auto rounded-xl border border-slate-200">
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
                            <div class="min-h-[150px] border-r border-b border-slate-200 p-2 
                                {% if cell.is_today %}bg-amber-50/70 ring-2 ring-amber-400 ring-inset
                                {% elif cell.is_sunday %}bg-red-50/60
                                {% else %}bg-white{% endif %} 
                                {% if not cell.in_range %}bg-slate-50 text-slate-300{% endif %}">
                                <div class="flex items-center justify-between mb-2">
                                    <div class="flex items-center gap-1.5">
                                        <span class="text-sm font-bold {% if cell.is_sunday and cell.in_range %}text-red-600{% elif not cell.in_range %}text-slate-300{% else %}text-slate-700{% endif %}">
                                            {{ cell.day_number }}
                                        </span>
                                        {% if cell.is_today %}
                                        <span class="text-[9px] font-bold uppercase tracking-wide text-amber-700 bg-amber-200 px-1.5 py-0.5 rounded">Today</span>
                                        {% endif %}
                                    </div>
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

                <!-- Mobile View: Week-by-Week Horizontal Scroll -->
                <div class="md:hidden space-y-4">
                    {% for week_obj in month.weeks %}
                    <div {% if week_obj.is_current %}id="current-week"{% endif %} class="bg-slate-50/70 border {% if week_obj.is_current %}border-blue-400 ring-2 ring-blue-100{% else %}border-slate-200{% endif %} rounded-xl p-3">
                        <div class="flex items-center justify-between mb-2">
                            <span class="text-xs font-bold {% if week_obj.is_current %}text-blue-600{% else %}text-slate-400{% endif %} uppercase tracking-wider">
                                Week {{ loop.index }} {% if week_obj.is_current %}(Current){% endif %}
                            </span>
                        </div>
                        <div class="flex gap-2.5 overflow-x-auto no-scrollbar pb-1 snap-x">
                            {% for cell in week_obj.cells %}
                            <div class="min-w-[130px] w-[130px] flex-shrink-0 snap-start rounded-lg border p-2.5 flex flex-col justify-between 
                                {% if cell.is_today %}bg-amber-50/95 border-amber-400 ring-2 ring-amber-200
                                {% elif cell.is_sunday %}bg-red-50/80 border-red-200
                                {% else %}bg-white border-slate-200{% endif %} 
                                {% if not cell.in_range %}opacity-40 bg-slate-100{% endif %}">
                                <div>
                                    <div class="flex items-center justify-between mb-2">
                                        <span class="text-xs font-bold {% if cell.is_today %}text-amber-700{% else %}text-slate-500{% endif %} uppercase">{{ cell.day_short }}</span>
                                        <div class="flex items-center gap-1">
                                            {% if cell.is_today %}
                                            <span class="text-[9px] font-extrabold uppercase tracking-wide text-amber-800 bg-amber-200 px-1 py-0.5 rounded">Today</span>
                                            {% endif %}
                                            <span class="text-sm font-bold {% if cell.is_sunday %}text-red-600{% else %}text-slate-800{% endif %}">{{ cell.day_number }}</span>
                                        </div>
                                    </div>
                                    <div class="space-y-1.5">
                                        {% if cell.sessions %}
                                            {% for session in cell.sessions %}
                                            <div class="rounded border p-1.5 {{ session.style.bg }} {{ session.style.border }} {{ session.style.text }}">
                                                <div class="text-[9px] font-semibold opacity-70 leading-none mb-1">{{ session.time }}</div>
                                                <div class="text-[11px] font-bold leading-tight line-clamp-3">{{ session.subject }}</div>
                                            </div>
                                            {% endfor %}
                                        {% else %}
                                            <div class="text-[10px] text-slate-400 italic py-3 text-center">No classes</div>
                                        {% endif %}
                                    </div>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                    {% endfor %}
                </div>

            </section>
            {% endfor %}
        </div>
    </div>

    <script>
        // Automatically scroll to the current week on mobile view when page loads
        document.addEventListener("DOMContentLoaded", function() {
            const currentWeekEl = document.getElementById("current-week");
            if (currentWeekEl && window.innerWidth < 768) {
                setTimeout(() => {
                    currentWeekEl.scrollIntoView({ behavior: "smooth", block: "start" });
                }, 100);
            }
        });
    </script>
</body>
</html>
"""

SUBJECT_STYLES = {
    "Financial Modeling using Excel": {"bg": "bg-blue-50", "border": "border-blue-200", "text": "text-blue-900",
                                       "dot": "bg-blue-500"},
    "Sales and Distribution Management": {"bg": "bg-purple-50", "border": "border-purple-200",
                                          "text": "text-purple-900", "dot": "bg-purple-500"},
    "Gales of Creative Destruction - Managing Innovation": {"bg": "bg-yellow-50", "border": "border-yellow-200",
                                                            "text": "text-yellow-900", "dot": "bg-yellow-500"},
    "International Business Models for the Circular Economy": {"bg": "bg-green-50", "border": "border-green-200",
                                                               "text": "text-green-900", "dot": "bg-green-500"}
}
DEFAULT_STYLE = {"bg": "bg-slate-50", "border": "border-slate-200", "text": "text-slate-800", "dot": "bg-slate-500"}


def parse_day(value):
    value = value.replace("Sept", "Sep")
    return datetime.strptime(value, "%a, %d %b %Y").date()


def month_start(d):
    return d.replace(day=1)


def next_month(d):
    return d.replace(year=d.year + (1 if d.month == 12 else 0), month=1 if d.month == 12 else d.month + 1, day=1)


def build_month_cells(year, month, sessions_by_date, start_date, end_date, today):
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
            "date": cell_date,
            "day_number": cell_date.day,
            "day_short": cell_date.strftime("%a"),
            "is_sunday": cell_date.weekday() == 6,
            "is_today": cell_date == today,
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

    today = date.today()

    if sessions_by_date:
        earliest = min(sessions_by_date)
        latest = max(sessions_by_date)
        # Ensure start and end dates automatically expand to include today's date if necessary
        start_date = min(month_start(earliest), month_start(today))
        end_date = max(next_month(month_start(latest)) - timedelta(days=1), next_month(month_start(today)) - timedelta(days=1))
    else:
        start_date = month_start(today)
        end_date = next_month(month_start(today)) - timedelta(days=1)

    for sessions in sessions_by_date.values():
        sessions.sort(key=lambda x: x.get("time", ""))

    months = []
    cursor = start_date
    while cursor <= end_date:
        cells = build_month_cells(cursor.year, cursor.month, sessions_by_date, start_date, end_date, today)

        # Group cells into chunks of 7 for the week-by-week mobile layout & check for current week
        raw_weeks = [cells[i:i + 7] for i in range(0, len(cells), 7)]
        weeks = []
        for w in raw_weeks:
            is_current = any(c["date"] == today for c in w)
            weeks.append({
                "cells": w,
                "is_current": is_current
            })

        months.append({
            "title": cursor.strftime("%B %Y"),
            "cells": cells,
            "weeks": weeks,
            "class_count": sum(len(c["sessions"]) for c in cells)
        })
        cursor = next_month(cursor)

    subtitle_range = f"{start_date.strftime('%d %B %Y')} to {end_date.strftime('%d %B %Y')}"

    return render_template_string(
        HTML_TEMPLATE,
        months=months,
        subject_styles=SUBJECT_STYLES,
        subtitle_range=subtitle_range
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)