import json
from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Weekly Schedule</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-100 min-h-screen p-6 font-sans">
    <div class="max-w-[1400px] mx-auto bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
        <h1 class="text-xl font-bold text-slate-800 mb-4">Class Schedule Matrix</h1>

        <div class="overflow-x-auto">
            <table class="w-full border-collapse border-hidden min-w-[1000px]">
                <thead>
                    <tr>
                        <th class="p-3 bg-slate-50 border border-slate-200 text-xs font-bold uppercase text-slate-600 text-center w-28">SLOTS</th>
                        {% for day in days %}
                            <th class="p-3 border border-slate-200 text-xs font-bold uppercase text-center w-40 {% if 'SUN' in day or 'Sun' in day %}bg-red-50 text-red-600{% else %}bg-slate-50 text-slate-700{% endif %}">
                                {{ day }}
                            </th>
                        {% endfor %}
                    </tr>
                </thead>
                <tbody>
                    {% for slot in slots %}
                        <tr>
                            <td class="p-3 border border-slate-200 bg-slate-50 text-center font-mono text-xs font-semibold text-slate-600">
                                {{ slot }}
                            </td>
                            {% for day in days %}
                                <td class="p-2 border border-slate-200 bg-white align-top h-24 relative {% if 'SUN' in day or 'Sun' in day %}bg-red-50/20{% endif %}">
                                    {% if grid[day][slot] %}
                                        {% set session = grid[day][slot] %}
                                        <!-- Colored card based on subject hash -->
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

    # Extract unique days and time slots
    days = list(dict.fromkeys([item["day"] for item in items]))
    slots = list(dict.fromkeys([item["time"] for item in items]))

    # Build 2D matrix: grid[day][slot] = session_object
    grid = {day: {slot: None for slot in slots} for day in days}
    for item in items:
        grid[item["day"]][item["time"]] = item

    return render_template_string(HTML_TEMPLATE, days=days, slots=slots, grid=grid)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)