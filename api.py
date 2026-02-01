from flask import Flask, request, jsonify
from src.account import Account, AccountsRegistry

app = Flask(__name__)
registry = AccountsRegistry()


def account_to_dict(acc: Account):
    return {
        "id": acc.pesel,
        "first_name": acc.first_name,
        "last_name": acc.last_name,
        "pesel": acc.pesel,
        "balance": acc.balance,
    }


# CREATE ACCOUNT
@app.route("/accounts", methods=["POST"])
def create_account():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON"}), 400

    if not all(k in data for k in ("first_name", "last_name", "pesel")):
        return jsonify({"error": "Missing fields"}), 400

    acc = Account(data["first_name"], data["last_name"], data["pesel"])

    try:
        registry.add_account(acc)
    except ValueError:
        return jsonify({"error": "Pesel already exists"}), 409

    return jsonify({"id": acc.pesel}), 201


# GET ACCOUNT
@app.route("/accounts/<pesel>", methods=["GET"])
def get_account(pesel):
    acc = registry.find_by_pesel(pesel)
    if acc is None:
        return jsonify({"error": "Not found"}), 404
    return jsonify(account_to_dict(acc)), 200


# DELETE ACCOUNT
@app.route("/accounts/<pesel>", methods=["DELETE"])
def delete_account(pesel):
    acc = registry.find_by_pesel(pesel)
    if acc is None:
        return jsonify({"error": "Not found"}), 404

    registry.delete_by_pesel(pesel)
    return "", 200


# DEPOSIT
@app.route("/accounts/<pesel>/deposit", methods=["POST"])
def deposit(pesel):
    acc = registry.find_by_pesel(pesel)
    if acc is None:
        return jsonify({"error": "Not found"}), 404

    data = request.get_json(silent=True)
    if not isinstance(data, dict) or "amount" not in data:
        return jsonify({"error": "Invalid JSON"}), 400

    try:
        acc.deposit(data["amount"])
    except ValueError as e:
        return jsonify({"error": str(e)}), 422

    return "", 200