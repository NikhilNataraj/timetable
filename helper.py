import json
from app import app

with app.test_request_context():
    from app import index
    html_content = index()

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("Generated index.html successfully!")