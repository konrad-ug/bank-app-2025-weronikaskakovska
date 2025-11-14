class BuisnessAccount:
    def __init__(self, company_name, nip):
        self.company_name = company_name
        self.balance = 0
        self.history = []

        if len(nip) != 10:
            self.nip = "Invalid"
        else:
            self.nip = nip

    def deposit(self, amount):
        self.balance += amount
        self.history.append(amount)

    def withdraw(self, amount):
        if amount > self.balance:
            raise ValueError("Za mało środków")
        self.balance -= amount
        self.history.append(-amount)

    def express_transfer(self, amount):
        if amount > self.balance:
            raise ValueError("Brak środków")
        self.balance -= (amount + 5)
        self.history.append(-amount)
        self.history.append(-5)

