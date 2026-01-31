from flask import Flask, request, jsonify
from src.account import Account, AccountsRegistry

app = Flask(__name__)
registry = AccountsRegistry()


@app.route("/api/accounts", methods=["POST"])
def create_account():
    data = request.get_json()

    account = Account(
        data["name"],
        data["surname"],
        data["pesel"]
    )

    registry.add_account(account)
    return jsonify({"message": "Account created"}), 201



@app.route("/api/accounts", methods=["GET"])
def get_all_accounts():
    accounts = registry.get_all_accounts()
    result = [
        {
            "name": acc.first_name,
            "surname": acc.last_name,
            "pesel": acc.pesel,
            "balance": acc.balance
        }
        for acc in accounts
    ]
    return jsonify(result), 200



@app.route("/api/accounts/count", methods=["GET"])
def get_count():
    return jsonify({"count": registry.count_accounts()}), 200



@app.route("/api/accounts/<pesel>", methods=["GET"])
def get_account(pesel):
    acc = registry.find_by_pesel(pesel)

    if acc is None:
        return jsonify({"error": "Not found"}), 404

    return jsonify({
        "name": acc.first_name,
        "surname": acc.last_name,
        "pesel": acc.pesel,
        "balance": acc.balance
    }), 200



@app.route("/api/accounts/<pesel>", methods=["PATCH"])
def update_account(pesel):
    acc = registry.find_by_pesel(pesel)

    if acc is None:
        return jsonify({"error": "Not found"}), 404

    data = request.get_json()

    if "name" in data:
        acc.first_name = data["name"]

    if "surname" in data:
        acc.last_name = data["surname"]

    return jsonify({"message": "Account updated"}), 200



@app.route("/api/accounts/<pesel>", methods=["DELETE"])
def delete_account(pesel):
    success = registry.delete_by_pesel(pesel)

    if not success:
        return jsonify({"error": "Not found"}), 404

    return jsonify({"message": "Account deleted"}), 200


if __name__ == "__main__":
    app.run(debug=True)