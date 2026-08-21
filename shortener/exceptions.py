from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):

    response = exception_handler(exc, context)

    if response is None:
        return response

    if isinstance(response.data, dict):

        if "detail" in response.data:
            response.data = {
                "success": False,
                "error": {
                    "code": str(
                        getattr(exc, "default_code", "error")
                    ),
                    "message": response.data["detail"],
                },
            }

        else:
            response.data = {
                "success": False,
                **response.data,
            }

    return response
