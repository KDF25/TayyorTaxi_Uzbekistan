from click_api.models.request_models.prepare_request import PrepareRequest


class CompleteRequest(PrepareRequest):
    merchant_prepare_id: int
