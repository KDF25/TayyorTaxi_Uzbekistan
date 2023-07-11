from pydantic import BaseModel
from payme_api.paycom_exceptions import *

error_code = int


class ErrorBody(BaseModel):
    code: error_code
    message: str


class ErrorResponse(BaseModel):
    jsonrpc: str = "2.0"
    error: ErrorBody


error_invalid_account = ErrorResponse(error=ErrorBody(code=ERROR_INVALID_ACCOUNT,
                                                      message="Номер заказа не найден")).dict()
error_invalid_amount = ErrorResponse(error=ErrorBody(code=ERROR_INVALID_AMOUNT,
                                                     message="Неверная сумма")).dict()
error_could_not_perform = ErrorResponse(error=ErrorBody(code=ERROR_COULD_NOT_PERFORM,
                                                        message="Невозможно выполнить операцию.")).dict()
error_transaction_not_found = ErrorResponse(error=ErrorBody(code=ERROR_TRANSACTION_NOT_FOUND,
                                                            message="Транзакция не найдена")).dict()
error_could_not_cansel = ErrorResponse(error=ErrorBody(code=ERROR_COULD_NOT_CANCEL,
                                                       message="Заказ выполнен. Невозможно отменить транзакцию. "
                                                               "Товар или услуга предоставлена покупателю в "
                                                               "полном объеме.")).dict()
