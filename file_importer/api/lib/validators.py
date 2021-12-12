# This is a list of functions used to validate specific field types. Each validator will either
# return the acceptable form of the field value or raise an error with a description of the error.
import datetime

from decimal import Decimal, InvalidOperation

from api.lib.file_import_fields import FIELD_COUNTRY, FIELD_CURRENCY, FIELD_DATE, FIELD_MONEY, \
    FIELD_TRX_TYPE, TRX_TYPE_PURCHASE, TRX_TYPE_SALE


class ValidationError(Exception):
    """Specific error class for handling validation errors."""

    pass


def validate_date(date_value):
    try:
        clean_date = datetime.datetime.strptime(date_value, "%Y/%m/%d")
    except ValueError:
        raise ValidationError(
            f'date value ("{date_value}") is not an acceptable date - must be in the '
            f'format: YYYY/MM/DD')

    return clean_date


def validate_trx_type(trx_type):
    """
    Only Sale and Purchase are allowed for this field type.

    Allowances will be made for casing differences and leading or trailing white space
    but any variation thereof will be rejected.
    """
    clean_trx_type = trx_type.strip().lower()
    acceptable_values = [TRX_TYPE_SALE, TRX_TYPE_PURCHASE]

    valid = clean_trx_type in acceptable_values
    if not valid:
        raise ValidationError(
            f'transaction type ("{trx_type}") is not an acceptable value - must be either '
            f'"Sale" or "Purchase"')

    return clean_trx_type


def validate_country(country):
    """
    All countries will be allowed.

    Assuming that country is only important to see what the exchange rate is, the currency field
    is available and less error-prone than the many variations of country that may be exposed. That
    said, it may still be useful to store the original country - just don't modify it in any way
    except for the most basic of cleaning, like stripping leading/trailing spaces.
    """
    return country.strip()


def validate_currency(currency):
    from api.lib import EXCHANGE_RATES

    # EUR is actually not present in EXCHANGE_RATES so it needs to be allowed manually in this
    # validator
    currency = currency.strip().upper()
    if currency in EXCHANGE_RATES or currency == 'EUR':
        return currency

    raise ValidationError(
        f'currency ("{currency}") is not an acceptable value - must be recognised by the '
        f'European Central Bank')


def validate_money(money):
    try:
        clean_money = Decimal(money)
    except InvalidOperation:
        raise ValidationError(
            f'transaction amount ("{money}") is not an acceptable value - must be valid numeric '
            f'value')

    return clean_money


VALIDATORS = {
    FIELD_DATE: validate_date,
    FIELD_TRX_TYPE: validate_trx_type,
    FIELD_COUNTRY: validate_country,
    FIELD_CURRENCY: validate_currency,
    FIELD_MONEY: validate_money
}
