from datetime import datetime

class BankView:
    """Класс представления"""

    @staticmethod
    def show_menu():
        """Показать главное меню"""
        print("\n" + "="*50)
        print("        БАНКОВСКАЯ СИСТЕМА")
        print("="*50)
        print("1. Создать новый счет")
        print("2. Просмотреть все счета")
        print("3. Пополнить счет")
        print("4. Снять со счета")
        print("5. Перевести средства")
        print("6. Показать историю транзакций")
        print("7. Сохранить данные")
        print("8. Загрузить данные")
        print("0. Выход")
        print("="*50)
        return input("Выберите действие: ")

    @staticmethod
    def get_account_info():
        """Получить информацию для создания счета"""
        print("\n--- Создание нового счета ---")
        print("Типы счетов:")
        print("1. Расчетный счет")
        print("2. Сберегательный счет")
        print("3. Кредитный счет")

        try:
            acc_type = int(input("Выберите тип счета (1-3): "))
            account_number = input("Номер счета: ")
            owner_name = input("Имя владельца: ")
            initial_balance = float(input("Начальный баланс: "))

            if acc_type == 3:
                credit_limit = float(input("Кредитный лимит (по умолчанию 1000): ") or "1000")
                return acc_type, account_number, owner_name, initial_balance, credit_limit
            return acc_type, account_number, owner_name, initial_balance, None
        except ValueError:
            print("Ошибка: Неверный формат данных!")
            return None

    @staticmethod
    def show_accounts(accounts):
        """Показать все счета"""
        if not accounts:
            print("\nНет доступных счетов.")
            return

        print("\n" + "="*70)
        print(f"{'№ счета':<15} {'Владелец':<20} {'Тип':<12} {'Баланс':<15}")
        print("-"*70)
        for acc_num, acc in accounts.items():
            print(f"{acc_num:<15} {acc.owner_name:<20} {acc.get_account_type():<12} {acc.balance:<15.2f}")
        print("="*70)

    @staticmethod
    def get_amount(operation):
        """Получить сумму операции"""
        try:
            amount = float(input(f"Введите сумму для {operation}: "))
            return amount
        except ValueError:
            print("Ошибка: Неверный формат суммы!")
            return None

    @staticmethod
    def get_account_number(prompt):
        """Получить номер счета"""
        return input(prompt)

    @staticmethod
    def show_message(message, is_error=False):
        """Показать сообщение"""
        if is_error:
            print(f"\n❌ Ошибка: {message}")
        else:
            print(f"\n✅ {message}")

    @staticmethod
    def show_transaction_history(transactions):
        """Показать историю транзакций"""
        if not transactions:
            print("\nНет транзакций для отображения.")
            return

        print("\n" + "="*60)
        print("ИСТОРИЯ ТРАНЗАКЦИЙ")
        print("-"*60)
        for trans in transactions:
            print(trans)
        print("="*60)

    @staticmethod
    def get_filter_options():
        """Получить параметры фильтрации"""
        print("\n--- Фильтрация транзакций ---")
        show_all = input("Показать все транзакции? (y/n): ").lower() == 'y'

        if show_all:
            return None, None, None

        trans_type = None
        print("Типы транзакций: deposit, withdraw, transfer_out, transfer_in")
        filter_type = input("Фильтровать по типу? (y/n): ").lower() == 'y'
        if filter_type:
            trans_type = input("Введите тип транзакции: ")

        start_date = None
        end_date = None

        filter_date = input("Фильтровать по дате? (y/n): ").lower() == 'y'
        if filter_date:
            start_date = input("Начальная дата (ГГГГ-ММ-ДД) [Enter для пропуска]: ")
            end_date = input("Конечная дата (ГГГГ-ММ-ДД) [Enter для пропуска]: ")

            if start_date:
                start_date += "T00:00:00"
            if end_date:
                end_date += "T23:59:59"

        return trans_type, start_date, end_date
