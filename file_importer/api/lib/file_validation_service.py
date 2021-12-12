from api.lib.validators import VALIDATORS, ValidationError


class FileValidationService():
    """
    This will validate all of the given transaction data and return validation errors.

    It will also co-erce and prepare any data for import to the database.
    NOTE! The cleaning up could be done in a separate service but it's use is so intertwined with
          validating the data that it makes more sense to combine both functions in this service.
    """

    def __init__(self, transaction_data):
        self.transaction_data = transaction_data
        self.valid_transactions = []
        self.validation_errors = []

    def validate(self, field_structure):
        """
        Validate the given transaction data and return the success/failure and errors.

        field_structure: a list of values describing the fields in the order that they occur in:
                         - "date": a date value in the format: YYYY/MM/DD
                         - "trx_type": a string value from a particular set
                         - "country": a string value from a particular list of countries
                         - "currency": a string value denoting a particular countries currency code
                         - "money": a floating number used to denote a monetary value

        The output shall be in the format:
        (True (if all valid) or False (contains at least one invalid row), list of errors)
        """
        valid_transactions = []
        errors = []

        for row_number, transaction in enumerate(self.transaction_data):
            row = []
            row_errors = []

            # Validate each transaction column-by-column
            for column_number, field_value in enumerate(transaction):
                field_type = field_structure[column_number]
                try:
                    clean_value = VALIDATORS[field_type](field_value)
                    row.append(clean_value)
                except ValidationError as e:
                    row_errors.append([row_number, field_value, str(e)])

            if row_errors:
                errors.extend(row_errors)
            else:
                valid_transactions.append(row)

        self.valid_transactions = valid_transactions
        self.validation_errors = errors
        return bool(errors == [])
