from flask import Flask, request, redirect, render_template_string
import sqlite3

app = Flask(__name__)

def get_db():
    return sqlite3.connect("subscriptions.db")

def create_table():
    con = get_db()
    con.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            cycle TEXT NOT NULL,
            renewal TEXT NOT NULL
        )
    """)
    con.commit()
    con.close()

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Subscription Manager</title>
    <style>
        body {
            font-family: Arial;
            background: #101827;
            color: white;
            padding: 30px;
        }
        .container {
            max-width: 850px;
            margin: auto;
        }
        h1 { color: #60a5fa; }
        .card {
            background: #1e293b;
            padding: 22px;
            border-radius: 12px;
            margin: 18px 0;
        }
        input, select, button {
            padding: 12px;
            margin: 6px 0;
            border: none;
            border-radius: 6px;
        }
        input, select { width: 95%; }
        button {
            background: #3b82f6;
            color: white;
            cursor: pointer;
        }
        .delete { background: #dc4444; }
        .item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #475569;
            padding: 12px 0;
        }
    </style>
</head>
<body>
<div class="container">
    <h1>Subscription Management System</h1>
    <p>Manage all your subscriptions in one place.</p>

    <div class="card">
        <h2>Monthly Spending</h2>
        <h1>₹{{ "%.2f"|format(total) }}</h1>
    </div>

    <div class="card">
        <h2>Add New Subscription</h2>
        <form method="POST" action="/add">
            <input name="name" placeholder="Subscription name" required>
            <input name="amount" type="number" step="0.01"
                   min="0.01" placeholder="Amount in ₹" required>
            <select name="cycle">
                <option value="Monthly">Monthly</option>
                <option value="Yearly">Yearly</option>
            </select>
            <label>Next renewal date:</label>
            <input name="renewal" type="date" required>
            <button type="submit">Add Subscription</button>
        </form>
    </div>

    <div class="card">
        <h2>My Subscriptions</h2>
        {% for s in subscriptions %}
        <div class="item">
            <div>
                <strong>{{ s[1] }}</strong><br>
                ₹{{ "%.2f"|format(s[2]) }} / {{ s[3] }}<br>
                <small>Renewal: {{ s[4] }}</small>
            </div>
            <form method="POST" action="/delete/{{ s[0] }}">
                <button class="delete">Delete</button>
            </form>
        </div>
        {% else %}
        <p>No subscriptions added yet.</p>
        {% endfor %}
    </div>
</div>
</body>
</html>
"""

@app.route("/")
def home():
    con = get_db()
    subscriptions = con.execute(
        "SELECT * FROM subscriptions ORDER BY renewal"
    ).fetchall()

    total = sum(
        s[2] if s[3] == "Monthly" else s[2] / 12
        for s in subscriptions
    )

    con.close()
    return render_template_string(
        HTML, subscriptions=subscriptions, total=total
    )

@app.route("/add", methods=["POST"])
def add():
    name = request.form["name"].strip()
    amount = float(request.form["amount"])
    cycle = request.form["cycle"]
    renewal = request.form["renewal"]

    if not name or amount <= 0 or cycle not in ["Monthly", "Yearly"]:
        return "Invalid subscription details", 400

    con = get_db()
    con.execute(
        "INSERT INTO subscriptions (name, amount, cycle, renewal) VALUES (?, ?, ?, ?)",
        (name, amount, cycle, renewal)
    )
    con.commit()
    con.close()
    return redirect("/")

@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    con = get_db()
    con.execute("DELETE FROM subscriptions WHERE id = ?", (id,))
    con.commit()
    con.close()
    return redirect("/")

if __name__ == "__main__":
    create_table()
    app.run(debug=True, port=5000)