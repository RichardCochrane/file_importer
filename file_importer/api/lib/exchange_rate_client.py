import requests


class ExchangeRateClient():
    """
    This class will handle the retrieval of exchange rate information through an API.

    In this case, it will be hard-coded to the European Central Bank
    (https://sdw-wsrest.ecb.europa.eu/help/) but multiple clients could be used to handle multiple
    exchange rate sources.
    """

    @classmethod
    def get_exchange_rates(cls):
        """
        Return the exchange rate data available via the European Central Bank.

        The data will be in the form:
        {
            3-letter currency: {
                name: description of currency
                value: latest exchange rate
            }
        }

        Eg.
        {
            'ZAR': {
                'name': 'South African rand',
                'value': 20.01
            }
        }
        """
        # This will get all of the daily exchange rates for all currencies against the Euro and
        # return the data in a JSON format (last occurance only - previous exchange rates are not
        # relevant at this time)
        response = requests.get(
            'https://sdw-wsrest.ecb.europa.eu/service/data/EXR/D..EUR.SP00.A?'
            'lastNObservations=1&format=jsondata')

        exchange_rate_data = response.json()
        attribute_series = exchange_rate_data['structure']['attributes']['series']

        # The UNIT series is the 3-letter currency abbreviation paired with the more description
        # form of the currency, i.e. "South African rand"
        exchange_rate_units = [d for d in attribute_series if d['id'] == 'UNIT']

        # "exchange_rates" will have the form: (3-letter currency, long-form currency name)
        # in the original order presented - this is important when looking up the actual exchange
        # rate information
        exchange_rates = [(eru['id'], eru['name']) for eru in exchange_rate_units[0]['values']]

        dataset_series = exchange_rate_data['dataSets'][0]['series']
        final_exchange_rates = {}
        for index, exchange_rate in enumerate(exchange_rates):
            exchange_rate_code, exchange_rate_name = exchange_rate

            # The API for the ECB is really horrible and terribly documented but it appears that
            # this will get the exchange rate for the last observation available
            observations = dataset_series[f'0:{index}:0:0:0']['observations']
            latest_exchange_rate = list(observations.values())[0][0]

            final_exchange_rates[exchange_rate_code.upper()] = {
                'name': exchange_rate_name,
                'value': latest_exchange_rate
            }

        return final_exchange_rates
