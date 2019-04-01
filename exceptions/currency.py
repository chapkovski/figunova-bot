class NoSuchCurrency(Exception):
    def __init__(self):
        default_message = 'No info about this currency!'
        super().__init__(default_message)
