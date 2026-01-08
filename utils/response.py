from rest_framework.response import Response

def success_response(data=None, message="Success", status_code=200):
    return Response(
        {
            "status": status_code,
            "message": message,
            "data": data
        },
        status=status_code
    )


def error_response(error=None, message="Error", status_code=400):
    return Response(
        {
            "status": status_code,
            "message": message,
            "error": error
        },
        status=status_code
    )
