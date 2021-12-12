import datetime

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from api.lib import FileImportService
from api.decorators import require_api_authentication
from api.models import Transaction


def heartbeat_view(request):
    return HttpResponse("OK.")


@csrf_exempt
@require_api_authentication
def import_transactions_view(request, json_body):
    # The api_partner_id can be used to pair all of the requests from this one client with a
    # particular account - useful if the API contract has a rate limit or usage limit
    api_partner_id = json_body['api_partner_id']

    ignore_errors = json_body['ignore_errors']
    ignore_first_row = json_body['ignore_first_row']
    transaction_data = json_body['transaction_data']
    transaction_count = len(transaction_data)

    file_import_service = FileImportService(transaction_data, ignore_first_row)
    if file_import_service.validate_transaction_data() or ignore_errors:
        successful_rows = file_import_service.save_transactions(ignore_errors)
        message = f'{successful_rows} / {transaction_count} row(s) were successfully imported'

        invalid_row_count = len(file_import_service.file_validation.validation_errors)
        if invalid_row_count:
            message = f'{message}, {invalid_row_count} invalid row(s) were ignored'

        response_data = {
            'success': True,
            'message': message,
            'errors': file_import_service.file_validation.validation_errors
        }
    else:
        invalid_row_count = len(file_import_service.file_validation.validation_errors)
        response_data = {
            'success': False,
            'message': (
                f'There were {invalid_row_count} / {transaction_count} invalid row(s) preventing '
                'the import of the data - try setting the "ignore_errors" flag to True to import '
                'all valid transactions and ignore the invalid transactions'),
            'errors': file_import_service.file_validation.validation_errors
        }

    return JsonResponse(data=response_data, status=200)


@csrf_exempt
@require_api_authentication
def query_transactions_view(request, json_body):
    from api.lib import EXCHANGE_RATES

    api_partner_id = json_body['api_partner_id']

    country_code = json_body['country_code'].upper()
    raw_query_date = json_body['query_date']

    # Validate the inputs
    errors = []

    # Note! This is a bit hacky - assuming that country can be properly validated by being in the
    # list of exchange rates but it'll do for now.
    if country_code not in [code[:2] for code in EXCHANGE_RATES.keys()]:
        errors.append(f'Country code "{country_code}" is not supported')

    try:
        query_date = datetime.datetime.strptime(raw_query_date, '%Y/%m/%d')
    except ValueError:
        errors.append(f'Query date "{raw_query_date}" is not in a supported format (YYYY/MM/DD)')

    if errors:
        return JsonResponse(data={'errors': errors}, status=400)

    transactions = Transaction.objects.get_by_country_code_and_date(country_code, query_date)
    transaction_data = [
        [t.created_at.date(), t.country, t.currency, t.transaction_type, t.net, t.vat, t.net_euro,
         t.vat_euro] for t in transactions]

    return JsonResponse(data={'transactions': transaction_data}, status=200)
