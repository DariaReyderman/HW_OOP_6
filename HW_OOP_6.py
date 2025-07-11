from abc import ABC, abstractmethod
from typing import override


class ITransfer(ABC):
    @abstractmethod
    def transfer(self, amount: float, to_account: "BankAccount") -> bool:
        """
        Trying to transfer an 'amount' to 'to_account'
        """


class IVerifyCreditCard(ABC):
    @abstractmethod
    def verify_credit_card(self, card_number: str) -> bool:
        """
        Checking, that card_number is the same with a saved one
        """


class IVerifyPayPal(ABC):
    @abstractmethod
    def verify_paypal_email(self, email: str) -> bool:
        """
        Checking, that the email is the same with a saved one
        """


class BankAccount(ITransfer, IVerifyCreditCard, IVerifyPayPal):
    def __init__(self, id: str, balance: float, credit_card_number: str, paypal_email: str):
        self._id = id
        self._balance = balance
        self._credit_card_number = credit_card_number
        self._paypal_email = paypal_email

    @property
    def id(self) -> str:
        return self._id

    @property
    def balance(self) -> float:
        return self._balance

    @balance.setter
    def balance(self, value: float):
        if value < 0:
            raise ValueError("Balance can't be negative")
        self._balance = value

    def transfer(self, amount: float, to_account: "BankAccount") -> bool:
        if amount <= 0:
            return False
        if self._balance < amount:
            print("Insufficient funds")
            return False
        # withdrawal and deposit
        self._balance -= amount
        to_account._balance += amount
        return True

    def verify_credit_card(self, card_number: str) -> bool:
        return card_number == self._credit_card_number

    def verify_paypal_email(self, email: str) -> bool:
        return email.lower() == (self._paypal_email or "").lower()

    @override
    def __str__(self):
        return (f"BankAccount(id={self._id}, balance={self._balance:.2f}, "
                f"card={self._credit_card_number}, paypal={self._paypal_email})")


class Payment(ABC):
    def __init__(self, amount: float, from_account_id: str, to_account_id: str):
        self.amount = amount
        self.from_account_id = from_account_id
        self.to_account_id = to_account_id

    @abstractmethod
    def process(self, accounts: dict[str, BankAccount]) -> bool:
        """
        Makes a payment: finds accounts by id, verifies, makes a transfer.
        """


class CreditCardPayment(Payment):
    def __init__(self, amount, from_account_id, to_account_id, card_number: str):
        super().__init__(amount, from_account_id, to_account_id)
        self.card_number = card_number

    def process(self, accounts: dict[str, BankAccount]) -> bool:
        # 1) We take the sender and the receiver object
        sender = accounts[self.from_account_id]
        receiver = accounts[self.to_account_id]

        # 2) Verifying: does the sender have the interface IVerifyCreditCard and his card matches
        if not sender.verify_credit_card(self.card_number):
            print("Error: invalid credit card number")
            return False

        # 3) Make a transfer
        success = sender.transfer(self.amount, receiver)
        if not success:
            print("Error: transfer failed")
        return success


class PayPalPayment(Payment):
    def __init__(self, amount, from_account_id, to_account_id, email: str):
        super().__init__(amount, from_account_id, to_account_id)
        self.email = email

    def process(self, accounts: dict[str, BankAccount]) -> bool:
        sender = accounts[self.from_account_id]
        receiver = accounts[self.to_account_id]

        if not sender.verify_paypal_email(self.email):
            print("Error: invalid PayPal-email")
            return False

        success = sender.transfer(self.amount, receiver)
        if not success:
            print("Error: transfer failed")
        return success


def main():
    accounts = {
        "A001": BankAccount("A001", 1000.0,
                            credit_card_number="1234567890123456",
                            paypal_email="user1@example.com"),
        "A002": BankAccount("A002", 500.0,
                            credit_card_number="1111222233334444",
                            paypal_email="user2@example.com"),
    }

    payments = [
        CreditCardPayment(200.0, "A001", "A002", card_number="1234567890123456"),
        PayPalPayment(300.0, "A001", "A002", email="wrong@example.com"),
        CreditCardPayment(900.0, "A002", "A001", card_number="1111222233334444"),
    ]

    for payment in payments:
        print("Successfully?", payment.process(accounts))
        print("-" * 30)

    for acc in accounts.values():
        print(acc)


if __name__ == "__main__":
    main()
