import json
from datetime import datetime
from collections import deque
from abc import ABC, abstractmethod

class Transaction:
    """Класс транзакции"""
    def __init__(self, transaction_type, amount, date=None, from_account=None, to_account=None):
        self.transaction_type = transaction_type  # 'deposit', 'withdraw', 'transfer_out', 'transfer_in'
        self.amount = amount
        self.date = date or datetime.now().isoformat()
        self.from_account = from_account
        self.to_account = to_account

    def to_dict(self):
        return {
            'transaction_type': self.transaction_type,
            'amount': self.amount,
            'date': self.date,
            'from_account': self.from_account,
            'to_account': self.to_account
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data['transaction_type'],
            data['amount'],
            data['date'],
            data.get('from_account'),
            data.get('to_account')
        )

    def __str__(self):
        if self.transaction_type == 'transfer_out':
            return f"[{self.date[:19]}] Переведено: {self.amount:.2f} -> {self.to_account}"
        elif self.transaction_type == 'transfer_in':
            return f"[{self.date[:19]}] Получено: {self.amount:.2f} от {self.from_account}"
        else:
            return f"[{self.date[:19]}] {self.transaction_type}: {self.amount:.2f}"

class Account(ABC):
    """Базовый класс счета"""
    def __init__(self, account_number, owner_name, balance=0):
        self.account_number = account_number
        self.owner_name = owner_name
        self.balance = balance
        self.transactions = deque()  # Очередь транзакций
        self._max_transaction_history = 100

    @abstractmethod
    def get_account_type(self):
        pass

    def deposit(self, amount):
        """Пополнение счета"""
        if amount <= 0:
            raise ValueError("Сумма должна быть положительной")
        self.balance += amount
        self._add_transaction(Transaction('deposit', amount))
        return True

    def withdraw(self, amount):
        """Снятие со счета"""
        if amount <= 0:
            raise ValueError("Сумма должна быть положительной")
        if amount > self.balance:
            raise ValueError("Недостаточно средств")
        self.balance -= amount
        self._add_transaction(Transaction('withdraw', amount))
        return True

    def _add_transaction(self, transaction):
        """Добавление транзакции в очередь"""
        self.transactions.append(transaction)
        if len(self.transactions) > self._max_transaction_history:
            self.transactions.popleft()

    def get_transaction_history(self, transaction_type=None, start_date=None, end_date=None):
        """Получение истории транзакций с фильтрацией"""
        filtered = list(self.transactions)

        if transaction_type:
            filtered = [t for t in filtered if t.transaction_type == transaction_type]

        if start_date:
            filtered = [t for t in filtered if t.date >= start_date]

        if end_date:
            filtered = [t for t in filtered if t.date <= end_date]

        return filtered

    def to_dict(self):
        return {
            'account_number': self.account_number,
            'owner_name': self.owner_name,
            'balance': self.balance,
            'account_type': self.get_account_type(),
            'transactions': [t.to_dict() for t in self.transactions]
        }

    @classmethod
    def from_dict(cls, data):
        if data['account_type'] == 'Checking':
            account = CheckingAccount(data['account_number'], data['owner_name'], data['balance'])
        elif data['account_type'] == 'Savings':
            account = SavingsAccount(data['account_number'], data['owner_name'], data['balance'])
        elif data['account_type'] == 'Credit':
            account = CreditAccount(data['account_number'], data['owner_name'], data['balance'])
        else:
            raise ValueError(f"Unknown account type: {data['account_type']}")

        for trans_data in data['transactions']:
            account.transactions.append(Transaction.from_dict(trans_data))

        return account

class CheckingAccount(Account):
    """Расчетный счет"""
    def get_account_type(self):
        return "Checking"

class SavingsAccount(Account):
    """Сберегательный счет"""
    def get_account_type(self):
        return "Savings"

class CreditAccount(Account):
    """Кредитный счет (с овердрафтом)"""
    def __init__(self, account_number, owner_name, balance=0, credit_limit=1000):
        super().__init__(account_number, owner_name, balance)
        self.credit_limit = credit_limit

    def withdraw(self, amount):
        """Снятие с учетом кредитного лимита"""
        if amount <= 0:
            raise ValueError("Сумма должна быть положительной")
        if amount > self.balance + self.credit_limit:
            raise ValueError("Превышен кредитный лимит")
        self.balance -= amount
        self._add_transaction(Transaction('withdraw', amount))
        return True

    def get_account_type(self):
        return "Credit"

    def to_dict(self):
        data = super().to_dict()
        data['credit_limit'] = self.credit_limit
        return data

    @classmethod
    def from_dict(cls, data):
        account = CreditAccount(data['account_number'], data['owner_name'],
                                data['balance'], data.get('credit_limit', 1000))
        for trans_data in data['transactions']:
            account.transactions.append(Transaction.from_dict(trans_data))
        return account

class BankModel:
    """Модель банковской системы"""
    def __init__(self):
        self.accounts = {}

    def add_account(self, account):
        """Добавление счета"""
        if account.account_number in self.accounts:
            raise ValueError(f"Счет {account.account_number} уже существует")
        self.accounts[account.account_number] = account

    def get_account(self, account_number):
        """Получение счета по номеру"""
        if account_number not in self.accounts:
            raise ValueError(f"Счет {account_number} не найден")
        return self.accounts[account_number]

    def transfer(self, from_account_num, to_account_num, amount):
        """Перевод между счетами"""
        if amount <= 0:
            raise ValueError("Сумма перевода должна быть положительной")

        from_account = self.get_account(from_account_num)
        to_account = self.get_account(to_account_num)

        # Выполняем перевод
        if from_account.withdraw(amount):
            to_account.deposit(amount)

            # Добавляем транзакции перевода
            from_account._add_transaction(Transaction('transfer_out', amount,
                                                       from_account=from_account_num,
                                                       to_account=to_account_num))
            to_account._add_transaction(Transaction('transfer_in', amount,
                                                     from_account=from_account_num,
                                                     to_account=to_account_num))
            return True
        return False

    def save_to_json(self, filename):
        """Сохранение данных в JSON"""
        data = {
            'accounts': [acc.to_dict() for acc in self.accounts.values()]
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_from_json(self, filename):
        """Загрузка данных из JSON"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.accounts = {}
            for acc_data in data['accounts']:
                account = self._create_account_from_dict(acc_data)
                self.accounts[account.account_number] = account
            return True
        except FileNotFoundError:
            return False
        except Exception as e:
            raise ValueError(f"Ошибка загрузки данных: {e}")

    def _create_account_from_dict(self, data):
        """Создание счета из словаря"""
        if data['account_type'] == 'Checking':
            return CheckingAccount.from_dict(data)
        elif data['account_type'] == 'Savings':
            return SavingsAccount.from_dict(data)
        elif data['account_type'] == 'Credit':
            return CreditAccount.from_dict(data)
        else:
            raise ValueError(f"Unknown account type: {data['account_type']}")
