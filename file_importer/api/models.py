import datetime

from django.db import models


class TransactionManager(models.Manager):

    def get_unconverted_transactions(self):
        return super().get_queryset().filter(net_euro__isnull=True)

    def get_by_country_code_and_date(self, country_code, query_date):
        """
        Return all transactions matching the given country code and date.

        Assumptions - because country in the source data is super flaky and currency is more
        consistent, this query will filter based on the first two characters in the currency,
        i.e. a query for United States will pass through country-code = 'US' which will match on
        'USD'. This is crude and assumes that no currency has the SAME first two characters.
        """
        start_date = query_date
        end_date = query_date + datetime.timedelta(days=1)

        return super().get_queryset().filter(
            currency__istartswith=country_code,
            created_at__gte=start_date,
            created_at__lt=end_date)


class Transaction(models.Model):
    created_at = models.DateTimeField('date created')
    country = models.CharField(max_length=50)
    currency = models.CharField(max_length=3)
    transaction_type = models.CharField(max_length=50)
    net = models.DecimalField(max_digits=5, decimal_places=2)
    vat = models.DecimalField(max_digits=5, decimal_places=2)
    net_euro = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    vat_euro = models.DecimalField(max_digits=5, decimal_places=2, null=True)

    objects = TransactionManager()
