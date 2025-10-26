class Account:
    def __init__(self, first_name, last_name, pesel, promo_code = None):
        self.first_name = first_name
        self.last_name = last_name

        if len(pesel) == 11:
            self.pesel = pesel
        else:
            self.pesel = "Invalid"

        self.balance = 0

        if self._promo_code_validation(promo_code) and self._age_validation():
            self.balance += 50

    def _promo_code_validation(self, promo_code):
        if promo_code is None:
            return False
        else:
            return promo_code.startswith("PROM_")

    def _age_validation(self):
        if self.pesel == "Invalid":
            return False

        year = int(self.pesel[0:2])
        month = int(self.pesel[2:4])

        if 1 <= month <= 12:
            year += 1900
        elif 21 <= month <=32:
            year += 2000
        elif 41 <= month <=52:
            year += 2100
        elif 61 <= month <=72:
            year += 2200
        elif 81 <= month <=92:
            year += 1800
        else:
            return False
        return year > 1960