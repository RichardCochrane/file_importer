import json
import os

from functools import wraps
from django.http import HttpResponseForbidden


def validate_api_request(func):
    @wraps(func)
    def validate_api_secret(request, *args, **kwargs):
        data = request.json()
        provided_security_hash = data.pop('security_hash')
        secret_key = os.environ['API_SECRET_KEY']
        calculated_security_hash = hash(
            secret_key + json.dumps(data, sort_keys=True))

        if provided_security_hash != calculated_security_hash:
            return HttpResponseForbidden('The security hash does not appear to be valid')

        return func(request, *args, **kwargs)
    return validate_api_secret
