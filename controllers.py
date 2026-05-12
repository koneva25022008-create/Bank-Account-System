from models import CheckingAccount, SavingsAccount, CreditAccount, BankModel

class BankController:
    """Контроллер банковской системы"""

    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.data_file = "data.json"

    def run(self):
        """Запуск приложения"""
        self.view.show_message("Добро пожаловать в банковскую систему!", is_error=False)

        # Попытка загрузить сохраненные данные
        try:
            if self.model.load_from_json(self.data_file):
                self.view.show_message(f"Данные загружены из {self.data_file}")
        except Exception as e:
            self.view.show_message(f"Не удалось загрузить данные: {e}", is_error=True)

        while True:
            choice = self.view.show_menu()

            if choice == '0':
                self.view.show_message("До свидания!")
                break
            elif choice == '1':
                self.create_account()
            elif choice == '2':
                self.show_accounts()
            elif choice == '3':
                self.deposit()
            elif choice == '4':
                self.withdraw()
            elif choice == '5':
                self.transfer()
            elif choice == '6':
                self.show_transaction_history()
            elif choice == '7':
                self.save_data()
            elif choice == '8':
                self.load_data()
            else:
                self.view.show_message("Неверный выбор. Попробуйте снова.", is_error=True)

    def create_account(self):
        """Создание нового счета"""
        info = self.view.get_account_info()
        if not info:
            return

        acc_type, account_number, owner_name, initial_balance, credit_limit = info

        try:
            if acc_type == 1:
                account = CheckingAccount(account_number, owner_name, initial_balance)
            elif acc_type == 2:
                account = SavingsAccount(account_number, owner_name, initial_balance)
            elif acc_type == 3:
                account = CreditAccount(account_number, owner_name, initial_balance, credit_limit)
            else:
                self.view.show_message("Неверный тип счета", is_error=True)
                return

            self.model.add_account(account)
            self.view.show_message(f"Счет {account_number} успешно создан!")
        except ValueError as e:
            self.view.show_message(str(e), is_error=True)

    def show_accounts(self):
        """Показать все счета"""
        self.view.show_accounts(self.model.accounts)

    def deposit(self):
        """Пополнение счета"""
        account_num = self.view.get_account_number("Введите номер счета: ")
        amount = self.view.get_amount("пополнения")

        if amount is None:
            return

        try:
            account = self.model.get_account(account_num)
            account.deposit(amount)
            self.view.show_message(f"Счет {account_num} пополнен на {amount:.2f}. Новый баланс: {account.balance:.2f}")
        except ValueError as e:
            self.view.show_message(str(e), is_error=True)

    def withdraw(self):
        """Снятие со счета"""
        account_num = self.view.get_account_number("Введите номер счета: ")
        amount = self.view.get_amount("снятия")

        if amount is None:
            return

        try:
            account = self.model.get_account(account_num)
            account.withdraw(amount)
            self.view.show_message(f"Со счета {account_num} снято {amount:.2f}. Новый баланс: {account.balance:.2f}")
        except ValueError as e:
            self.view.show_message(str(e), is_error=True)

    def transfer(self):
        """Перевод между счетами"""
        from_account = self.view.get_account_number("Введите номер счета ОТПРАВИТЕЛЯ: ")
        to_account = self.view.get_account_number("Введите номер счета ПОЛУЧАТЕЛЯ: ")
        amount = self.view.get_amount("перевода")

        if amount is None:
            return

        try:
            if self.model.transfer(from_account, to_account, amount):
                self.view.show_message(f"Переведено {amount:.2f} с {from_account} на {to_account}")
        except ValueError as e:
            self.view.show_message(str(e), is_error=True)

    def show_transaction_history(self):
        """Показать историю транзакций с фильтрацией"""
        account_num = self.view.get_account_number("Введите номер счета: ")

        try:
            account = self.model.get_account(account_num)
            trans_type, start_date, end_date = self.view.get_filter_options()

            transactions = account.get_transaction_history(trans_type, start_date, end_date)
            self.view.show_transaction_history(transactions)
        except ValueError as e:
            self.view.show_message(str(e), is_error=True)

    def save_data(self):
        """Сохранение данных"""
        try:
            self.model.save_to_json(self.data_file)
            self.view.show_message(f"Данные сохранены в {self.data_file}")
        except Exception as e:
            self.view.show_message(f"Ошибка сохранения: {e}", is_error=True)

    def load_data(self):
        """Загрузка данных"""
        try:
            if self.model.load_from_json(self.data_file):
                self.view.show_message(f"Данные загружены из {self.data_file}")
            else:
                self.view.show_message(f"Файл {self.data_file} не найден", is_error=True)
        except Exception as e:
            self.view.show_message(f"Ошибка загрузки: {e}", is_error=True)
