Telegram bot that registers our expenditure
===========================================

Uses django as backend db, python-telegram-bot as a delivery
service.
It also creates a naive copy of expenditures in google sheets.


Currency rates are stored in `CurrencyQuote` model. If there are no rates requested
today, the new quote is requested from `quote_requester` module.

The procedure is the following: If a user has no currency records, we create one with
RUB name. RUB records are not getting converted.
If there are records we retrieve the most recent.  If it is not RUB record we request
the rate from the most CurrencyQuote.

So when a person makes a payment we check if there there is non-RUB record.