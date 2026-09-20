from flask import Flask, request, jsonify, render_template
import csv
import os

app = Flask(__name__)

CSV_FILE = r"C:\Users\User\OneDrive\Documents\Myproject\DigitalWalletExpenseSplitter\expenses.csv"

FIELDNAMES = [
    "id",
    "expense_name",
    "amount",
    "paid_by",
    "participants",
    "date",
    "category"
]


def read_expenses():

    expenses = []

    if not os.path.exists(CSV_FILE):
        return expenses

    with open(CSV_FILE, mode="r", newline="", encoding="utf-8") as file:

        reader = csv.DictReader(file)

        for row in reader:

            # Skip completely blank rows
            if not row or all(v is None or str(v).strip() == "" for v in row.values()):
                continue

            # Skip rows that are missing required fields or have extra
            # columns (DictReader puts extras under the None key, and
            # missing columns show up as None values) — these break
            # jsonify() with a TypeError, so we filter them out here.
            if None in row or None in row.values():
                print(f"Skipping malformed CSV row: {row}")
                continue

            # Make sure every expected field exists and is a clean string
            clean_row = {}
            valid = True

            for field in FIELDNAMES:
                value = row.get(field)

                if value is None or str(value).strip() == "":
                    valid = False
                    break

                clean_row[field] = str(value).strip()

            if not valid:
                print(f"Skipping incomplete CSV row: {row}")
                continue

            expenses.append(clean_row)

    return expenses


def add_expense(expense):

    file_exists = os.path.exists(CSV_FILE) and os.path.getsize(CSV_FILE) > 0

    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as file:

        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)

        if not file_exists:
            writer.writeheader()

        writer.writerow(expense)

def calculate_split(expense):
    amount = float(expense["amount"])

    participants = expense["participants"].split("|")

    number_of_people = len(participants)

    share = amount / number_of_people

    result = []

    for person in participants:

        if person == expense["paid_by"]:
            paid = amount
        else:
            paid = 0

        balance = paid - share

        result.append({
            "person": person,
            "paid": paid,
            "share": share,
            "balance": balance
        })

    return result

def calculate_split(expense):

    amount = float(expense["amount"])

    participants = [p.strip() for p in expense["participants"].split("|") if p.strip()]

    number_of_people = len(participants)

    share = amount / number_of_people

    balances = {}

    for person in participants:

        if person == expense["paid_by"]:
            balances[person] = round(amount - share, 2)
        else:
            balances[person] = round(-share, 2)

    return {
        "expense_name": expense["expense_name"],
        "total_amount": amount,
        "paid_by": expense["paid_by"],
        "participants": participants,
        "share_per_person": round(share, 2),
        "balances": balances
    }


def calculate_owes(balances):

    receivers = []
    payers = []

    for person, balance in balances.items():

        if balance > 0:
            receivers.append([person, balance])

        elif balance < 0:
            payers.append([person, -balance])

    transactions = []

    i = 0
    j = 0

    while i < len(payers) and j < len(receivers):

        payer = payers[i]
        receiver = receivers[j]

        amount = min(payer[1], receiver[1])

        transactions.append({
            "from": payer[0],
            "to": receiver[0],
            "amount": round(amount, 2)
        })

        payers[i][1] -= amount
        receivers[j][1] -= amount

        if payers[i][1] <= 0.01:
            i += 1

        if receivers[j][1] <= 0.01:
            j += 1

    return transactions


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/expenses", methods=["GET"])
def get_expenses():

    expenses = read_expenses()

    return jsonify(expenses)


@app.route("/api/expenses", methods=["POST"])
def create_expense():

    data = request.get_json()

    if not data:
        return jsonify({"error": "No data received"}), 400

    for field in FIELDNAMES:
        if field == "id":
            continue
        if field not in data or str(data[field]).strip() == "":
            return jsonify({"error": f"Missing field: {field}"}), 400

    expenses = read_expenses()

    new_id = len(expenses) + 1

    new_expense = {
        "id": str(new_id),
        "expense_name": str(data["expense_name"]).strip(),
        "amount": str(data["amount"]).strip(),
        "paid_by": str(data["paid_by"]).strip(),
        "participants": str(data["participants"]).strip(),
        "date": str(data["date"]).strip(),
        "category": str(data["category"]).strip()
    }

    add_expense(new_expense)

    return jsonify({
        "message": "Expense added successfully",
        "expense": new_expense
    }), 201


@app.route("/api/expenses/<int:expense_id>/split", methods=["GET"])
def get_expense_split(expense_id):

    expenses = read_expenses()

    for expense in expenses:
        if int(expense["id"]) == expense_id:
            return jsonify(calculate_split(expense))

    return jsonify({"error": "Expense not found"}), 404


@app.route("/api/expenses/<int:expense_id>/owes", methods=["GET"])
def get_expense_owes(expense_id):

    expenses = read_expenses()

    for expense in expenses:
        if int(expense["id"]) == expense_id:
            split_result = calculate_split(expense)
            transactions = calculate_owes(split_result["balances"])
            return jsonify({
                "expense_name": expense["expense_name"],
                "transactions": transactions
            })

    return jsonify({"error": "Expense not found"}), 404


if __name__ == "__main__":
    app.run(debug=True)