from itertools import islice

from api.models import Transaction
from api.lib.file_validation_service import FileValidationService
from api.lib.transaction_conversion_service import TransactionConversionService
from api.lib.file_import_fields import FIELD_COUNTRY, FIELD_CURRENCY, FIELD_DATE, FIELD_MONEY, \
    FIELD_TRX_TYPE, TRX_TYPE_PURCHASE


class FileImportService():
    """
    This will handle the importing of transaction data, including validation, to the database.

    Note! This is a very specific handling for this one kind of file (VAT Imports). Ideally,
          differences would be abstracted into a file-specific format, ie. the file import service
          receives an object telling it what fields are in what order, any pre- and post-validation
          checks, etc.
    """
    FILE_STRUCTURE = [
        FIELD_DATE, FIELD_TRX_TYPE, FIELD_COUNTRY, FIELD_CURRENCY, FIELD_MONEY, FIELD_MONEY]

    def __init__(self, transaction_data, ignore_first_row):
        self.transaction_data = transaction_data[1:] if ignore_first_row else transaction_data
        self.file_validation = None

    def validate_transaction_data(self):
        self.file_validation = FileValidationService(self.transaction_data)
        return self.file_validation.validate(self.FILE_STRUCTURE)

    def save_transactions(self, ignore_invalid_transactions=False):
        """
        Save all of the valid transactions to the database.

        ignore_invalid_transactions: True if the importer should import all valid transactions
                                     even in the presense of some bad transactions or whether
                                     it should not save anything at all.
        """
        if self.file_validation.validation_errors and not ignore_invalid_transactions:
            return

        self._post_validation_updates()

        transaction_count = 0

        # This method of saving transactions in batches may be premature optimisation...
        # It's here as an alternative if my test is used to spawn a real feature  :-D

        # transactions_to_save = []
        for transaction in self.file_validation.valid_transactions:
            created_at, transaction_type, country, currency, net, vat = transaction
            transaction_count += 1

            Transaction(
                created_at=created_at, transaction_type=transaction_type, country=country,
                currency=currency, net=net, vat=vat).save()

            # transactions_to_save.append(
            #     Transaction(
            #         created_at=created_at, transaction_type=transaction_type, country=country,
            #         currency=currency, net=net, vat=vat))

        # Save the transactions in batches to optimise database usage when saving many rows at once
        # batch_size = 100
        # while True:
        #     batch = list(islice(transactions_to_save, batch_size))
        #     if not batch:
        #         break
        #     Transaction.objects.bulk_create(batch, batch_size)

        self._post_import_updates()

        return transaction_count

    def _post_validation_updates(self):
        """Update the validated transactions."""
        for transaction in self.file_validation.valid_transactions:
            trx_type = transaction[1]

            if trx_type == TRX_TYPE_PURCHASE:
                transaction[4] *= -1
                transaction[5] *= -1

    def _post_import_updates(self):
        """Update the newly imported transactions."""
        TransactionConversionService.convert_to_EUR()
