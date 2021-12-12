from decimal import Decimal

from api.models import Transaction


class TransactionConversionService():
    """
    Convert transaction amounts to Euros.

    NOTE! The structure of the exchange rate lookup allows the API call to ECB to be done only once
          (per application startup). This could possibly be included directly in the
          FileImportService but having it as a separate module allows it to be run more cleanly
          apart from the file import. In this case, the initial import will attempt to convert all
          transactions that it can, possibly leaving some rows NOT updated with Euro amounts. The
          Exchange Rate lookup could be run again later, once more countries have been added to the
          Exchange Rate lookup.

    NOTE! In this exact example, it's not entirely necessary - I use the exchange rate lookup to
          validate the given currencies, so any row with an invalid currency could never be
          imported anyway. Were they to be separated, this would become more important.
    """

    @classmethod
    def convert_to_EUR(cls):
        from api.lib import EXCHANGE_RATES

        transactions = Transaction.objects.get_unconverted_transactions()

        for transaction in transactions:
            if transaction.currency == 'EUR':
                transaction.net_euro = transaction.net
                transaction.vat_euro = transaction.vat
            else:
                exchange_rate = Decimal(EXCHANGE_RATES[transaction.currency]['value'])
                transaction.net_euro = transaction.net / exchange_rate
                transaction.vat_euro = transaction.vat / exchange_rate

            transaction.save()
