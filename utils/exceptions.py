from rest_framework.views import exception_handler
from rest_framework import status as http_status
from .response import error_response
from http import HTTPStatus


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return None

    return error_response(response.data,HTTPStatus(response.status_code).phrase,response.status_code)
