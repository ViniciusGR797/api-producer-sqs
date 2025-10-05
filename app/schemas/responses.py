from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    detail: str = Field(...,
                        example="An unexpected error occurred while processing your request.")


class ValidationLoginErrorResponse(BaseModel):
    detail: list = Field(...,
                         example=[{"loc": ["body",
                                           "email"],
                                   "msg": "Field required",
                                   "type": "value_error.missing"}],
                         description="List of validation errors in the request payload.")


class ValidationMessageErrorResponse(BaseModel):
    detail: list = Field(...,
                         example=[{"loc": ["body",
                                           "currency"],
                                   "msg": "Field required",
                                   "type": "value_error.missing"}],
                         description="List of validation errors in the request payload.")


class QueueNotFoundErrorResponse(BaseModel):
    detail: str = "The specified queue does not exist or the name is invalid."
