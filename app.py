import json
from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Class Schedule & Calendar</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-100 min-h-screen p-6 font-sans">
    <div class="max-w-[1400px] mx-auto bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
        <div class="flex items-center justify-between mb-4">
            <h1 class="text-xl font-bold text-slate-800">Weekly Schedule</h1>
            <div class="flex items-center gap-4 text-xs font-semibold">
                <span class="flex items-center gap-1"><span class="w-3 h-3 bg-yellow-100 border border-yellow-300 rounded"></span> Marketing</span>
                <span class="flex items-center gap-1"><span class="w-3 h-3 bg-purple-100 border border-purple-300 rounded"></span> Management</span>
                <span class="flex items-center gap-1"><span class="w-3 h-3 bg-red-50 border border-red-200 rounded"></span> Weekend</span>
            </div>
        </div>

        <div class="overflow-x-auto relative shadow-inner rounded-xl border border-slate-200">
            <table class="w-full border-collapse border-hidden min-w-[1000px]">
                <thead>
                    <tr>
                        <!-- Sticky SLOTS Header -->
                        <th class="sticky left-0 z-20 p-3 bg-slate-100 border-r border-b border-slate-200 text-xs font-bold uppercase text-slate-600 text-center w-28 shadow-sm">
                            SLOTS
                        </th>
                        {% for day in all_days %}
                            {% set is_weekend = 'SAT' in day.upper() or 'SUN' in day.upper() or 'SATURDAY' in day.upper() or 'SUNDAY' in day.upper() %}
                            <th class="p-3 border-b border-r border-slate-200 text-xs font-bold uppercase text-center w-40 {% if is_weekend %}bg-red-50 text-red-600{% else %}bg-slate-50 text-slate-700{% endif %}">
                                {{ day }}
                            </th>
                        {% endfor %}
                    </tr>
                </thead>
                <tbody>
                    {% for slot in slots %}
                        <tr>
                            <!-- Sticky Time Slot Column -->
                            <td class="sticky left-0 z-10 p-3 border-r border-b border-slate-200 bg-slate-50 text-center font-mono text-xs font-semibold text-slate-600 shadow-sm">
                                {{ slot }}
                            </td>
                            {% for day in all_days %}
                                {% set is_weekend = 'SAT' in day.upper() or 'SUN' in day.upper() or 'SATURDAY' in day.upper() or 'SUNDAY' in day.upper() %}
                                <td class="p-2 border-r border-b border-slate-200 align-top h-24 relative {% if is_weekend %}bg-red-50/20{% else %}bg-white{% endif %}">
                                    {% if grid[day] and grid[day][slot] %}
                                        {% set session = grid[day][slot] %}
                                        <div class="p-2.5 rounded-lg border text-xs h-full flex flex-col justify-between shadow-xs transition-transform hover:scale-[1.02]
                                            {% if 'Marketing' in session.subject %} bg-yellow-100 border-yellow-300 text-yellow-900
                                            {% elif 'Management' in session.subject %} bg-purple-100 border-purple-300 text-purple-900
                                            {% else %} bg-slate-100 border-slate-300 text-slate-800 {% endif %}">
                                            <div class="font-bold leading-tight line-clamp-2">{{ session.subject }}</div>
                                            <div class="mt-2 text-[10px] opacity-75 font-medium flex justify-between">
                                                <span>{{ session.time }}</span>
                                            </div>
                                        </div>
                                    {% endif %}
                                </td>
                            {% endfor %}
                        </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""


@app.route("/")
def index():
    try:
        with open("timetable.json", "r") as f:
            items = json.load(f)
    except FileNotFoundError:
        items = []

    # Standard full week structure
    default_days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]

    # Collect all unique days from scraper while keeping full week order
    scraped_days = list(dict.fromkeys([item["day"] for item in items]))
    all_days = list(dict.fromkeys(scraped_days + default_days))

    # Extract unique time slots
    slots = list(dict.fromkeys([item["time"] for item in items]))
    if not slots:
        slots = ["08:30 to 10:00 AM", "10:20 to 11:50 AM", "12:10 to 01:40 PM", "02:45 to 04:15 PM",
                 "04:30 to 06:00 PM"]

    # Build matrix grid[day][slot]
    grid = {day: {slot: None for slot in slots} for day in all_days}
    for item in items:
        if item["day"] in grid and item["time"] in grid[item["day"]]:
            grid[item["day"]][item["time"]] = item

    return render_template_string(HTML_TEMPLATE, all_days=all_days, slots=slots, grid=grid)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)