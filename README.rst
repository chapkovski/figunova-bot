Telegram bot that registers our expenditure
===========================================

Uses django as backend db, python-telegram-bot as a delivery
service.
It also creates a naive copy of expenditures in google sheets.


Currency rates are stored in `CurrencyQuote` model. If there are no