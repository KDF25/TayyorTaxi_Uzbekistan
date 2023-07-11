from click_api.models.error_model import ErrorModel

success = ErrorModel(error=0, error_note="Success")
sign_check_failed = ErrorModel(error=-1, error_note="SIGN CHECK FAILED!")
incorrect_parameter_amount = ErrorModel(error=-2, error_note="Incorrect parameter amount")
action_not_found = ErrorModel(error=-3, error_note="Action not found")
already_paid = ErrorModel(error=-4, error_note="Already paid")
user_does_not_exist = ErrorModel(error=-5, error_note="User does not exist")
transaction_does_not_exist = ErrorModel(error=-6, error_note="Transaction does not exist")
failed_to_update_user = ErrorModel(error=-7, error_note="Failed to update user")
error_in_request_from_click = ErrorModel(error=-8, error_note="Error in request from click")
transaction_cancelled = ErrorModel(error=-9, error_note="Transaction cancelled")
