#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from models import BankModel
from views import BankView
from controllers import BankController

def main():
    """Главная функция приложения"""
    model = BankModel()
    view = BankView()
    controller = BankController(model, view)
    controller.run()

if __name__ == "__main__":
    main()
