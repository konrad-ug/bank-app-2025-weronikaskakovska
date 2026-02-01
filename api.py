from flask import Flask, request, jsonify, current_app
import json
from account import Account, AccountsRegistry

app = Flask(__name__)
registry = AccountsRegistry()


def account_to_dict(acc: Account):
    return {
        "id": acc.pesel,
        "name": acc.first_name,
        "surname": acc.last_name,
        "pesel": acc.pesel,
        "balance": acc.balance
    }


# ------------------------
# ACCOUNTS COLLECTION
# ------------------------
@app.route("/api/accounts", methods=["POST", "GET"])
def accounts():
    if request.method == "POST":
        # try normal json parsing first
        data = request.get_json(silent=True)

        # fallback: try to parse request.data manually (helps when Content-Type missing)
        if data is None:
            raw = request.get_data(as_text=True)
            if raw:
                try:
                    data = json.loads(raw)
                except Exception:
                    # still None / invalid JSON
                    return jsonify({"error": "Invalid JSON"}), 400
            else:
                return jsonify({"error": "Invalid JSON"}), 400

        if not isinstance(data, dict):
            return jsonify({"error": "Invalid JSON"}), 400

        # accept both conventions: "name"/"surname" (tests) or "first_name"/"last_name"
        name = data.get("name") or data.get("first_name")
        surname = data.get("surname") or data.get("last_name")
        pesel = data.get("pesel")

        if not name or not surname or not pesel:
            # helpful debug in logs — do not change the returned error payload shape
            current_app.logger.debug("POST /api/accounts missing fields, payload keys: %s", list(data.keys()))
            return jsonify({"error": "Missing fields"}), 400

        acc = Account(name, surname, pesel)
        try:
            registry.add_account(acc)
        except ValueError:
            return jsonify({"error": "Pesel already exists"}), 409

        return jsonify({"id": pesel}), 201

    # GET ALL
    return jsonify([account_to_dict(a) for a in registry.get_all_accounts()]), 200

# ------------------------
# SINGLE ACCOUNT
# ------------------------
@app.route("/api/accounts/<pesel>", methods=["GET", "PATCH", "DELETE"])
def account_detail(pesel):
    acc = registry.find_by_pesel(pesel)

    if request.method == "GET":
        if acc is None:
            return jsonify({"error": "Not found"}), 404
        return jsonify(account_to_dict(acc)), 200

    if request.method == "PATCH":
        if acc is None:
            return jsonify({"error": "Not found"}), 404

        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"error": "Invalid JSON"}), 400

        # accept both field name styles
        if "name" in data:
            acc.first_name = data["name"]
        if "surname" in data:
            acc.last_name = data["surname"]
        if "first_name" in data:
            acc.first_name = data["first_name"]
        if "last_name" in data:
            acc.last_name = data["last_name"]

        return "", 200

    # DELETE
    if acc is None:
        return jsonify({"error": "Not found"}), 404
    registry.delete_by_pesel(pesel)
    return "", 200


# ------------------------
# COUNT
# ------------------------
@app.route("/api/accounts/count", methods=["GET"])
def count_accounts():
    return jsonify({"count": registry.count_accounts()}), 200


# ------------------------
# TRANSFER
# ------------------------
@app.route("/api/accounts/<pesel>/transfer", methods=["POST"])
def transfer(pesel):
    acc = registry.find_by_pesel(pesel)
    if acc is None:
        return jsonify({"error": "Not found"}), 404

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON"}), 400

    if "amount" not in data or "type" not in data:
        return jsonify({"error": "Missing fields"}), 400

    amount = data["amount"]
    t = data["type"]

    try:
        if t == "incoming":
            acc.deposit(amount)
        elif t == "outgoing":
            acc.withdraw(amount)
        elif t == "express":
            acc.express_transfer(amount)
        else:
            return jsonify({"error": "Unknown transfer type"}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 422

    return jsonify({"message": "Zlecenie przyjęto do realizacji"}), 200

# ------------------------
# SIMPLE DEPOSIT (PERF TEST)
# ------------------------
@app.route("/api/accounts/<pesel>/deposit", methods=["POST"])
def deposit(pesel):
    acc = registry.find_by_pesel(pesel)
    if acc is None:
        return jsonify({"error": "Not found"}), 404

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON"}), 400

    if "amount" not in data:
        return jsonify({"error": "Missing amount"}), 400

    try:
        acc.deposit(data["amount"])
    except ValueError as e:
        return jsonify({"error": str(e)}), 422

    return "", 200