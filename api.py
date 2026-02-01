import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from flask import Flask, request, jsonify
from src.account import Account, AccountsRegistry
app = Flask(__name__)
registry = AccountsRegistry()


def account_to_dict(acc: Account):
    return {
        "name": acc.first_name,
        "surname": acc.last_name,
        "pesel": acc.pesel,
        "balance": acc.balance,
    }


@app.route("/api/accounts", methods=["POST"])
def create_account():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON"}), 400

    if not all(k in data for k in ("name", "surname", "pesel")):
        return jsonify({"error": "Missing fields"}), 400

    acc = Account(data["name"], data["surname"], data["pesel"])
    try:
        registry.add_account(acc)
    except ValueError:
        return jsonify({"error": "Pesel already exists"}), 409

    return "", 201


@app.route("/api/accounts", methods=["GET"])
def get_all_accounts():
    return jsonify([account_to_dict(a) for a in registry.get_all_accounts()]), 200


@app.route("/api/accounts/<pesel>", methods=["GET", "PATCH", "DELETE"])
def account_detail(pesel):
    if request.method == "GET":
        acc = registry.find_by_pesel(pesel)
        if acc is None:
            return jsonify({"error": "Not found"}), 404
        return jsonify(account_to_dict(acc)), 200

    if request.method == "PATCH":
        acc = registry.find_by_pesel(pesel)
        if acc is None:
            return jsonify({"error": "Not found"}), 404

        data = request.get_json(silent=True)
        if data is None or not isinstance(data, dict):
            return jsonify({"error": "Invalid JSON"}), 400

        if "name" in data:
            acc.first_name = data["name"]
        if "surname" in data:
            acc.last_name = data["surname"]

        return "", 200

    # DELETE
    acc = registry.find_by_pesel(pesel)
    if acc is None:
        return jsonify({"error": "Not found"}), 404
    registry.delete_by_pesel(pesel)
    return "", 200


@app.route("/api/accounts/count", methods=["GET"])
def get_count():
    return jsonify({"count": registry.count_accounts()}), 200


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

    if t not in ("incoming", "outgoing", "express"):
        return jsonify({"error": "Unknown transfer type"}), 400

    try:
        if t == "incoming":
            acc.deposit(amount)
        elif t == "outgoing":
            acc.withdraw(amount)
        elif t == "express":
            acc.express_transfer(amount)
    except ValueError as e:
        return jsonify({"error": str(e)}), 422

    return jsonify({"message": "Zlecenie przyjęto do realizacji"}), 200