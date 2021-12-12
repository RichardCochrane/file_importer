__all__ = ['ExchangeRateClient', 'FileImportService']

from api.lib.exchange_rate_client import ExchangeRateClient
from api.lib.file_import_service import FileImportService

# This is done here so that it is run once when the app starts. It should be run and the results
# cached in Redis or memory but this should be sufficient for a first release
EXCHANGE_RATES = ExchangeRateClient.get_exchange_rates()
