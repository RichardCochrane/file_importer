import hashlib
import hmac
import json
import os

from django.http import JsonResponse
from dotenv import load_dotenv
from functools import wraps

load_dotenv()


def require_api_authentication(func):
    """
    Validate the incoming API request.

    To confirm that the message is entirely untouched from the sending party, the message contents
    will be hashed and that hash compared to the given hash.
    """
    @wraps(func)
    def validate_request(request, *args, **kwargs):
        json_data = json.loads(request.body)
        provided_security_hash = json_data.pop('security_hash')

        api_secret = os.environ['API_SECRET_KEY']

        calculated_security_hash = hmac.new(
            api_secret.encode(),
            json.dumps(json_data, sort_keys=True).encode(),
            hashlib.sha256).hexdigest()

        if provided_security_hash == calculated_security_hash:
            return func(request, json_data, *args, **kwargs)
        else:
            return JsonResponse({'error': 'Invalid security hash'}, status=403)

    return validate_request
