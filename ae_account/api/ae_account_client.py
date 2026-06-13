import allure

from ae_account.models.ae_account_model import (
    AeCreateAccountRequest,
    AeMessageResponse,
    AeUserDetailResponse,
)
from core.ae_base_client import AeBaseClient


class AeAccountClient(AeBaseClient):
    @allure.step("POST /api/verifyLogin")
    def verify_login(self, email: str, password: str) -> AeMessageResponse:
        return AeMessageResponse.model_validate(
            self._post("/verifyLogin", form={"email": email, "password": password})
        )

    @allure.step("POST /api/verifyLogin — missing email parameter")
    def verify_login_missing_email(self, password: str) -> AeMessageResponse:
        return AeMessageResponse.model_validate(
            self._post("/verifyLogin", form={"password": password})
        )

    @allure.step("DELETE /api/verifyLogin")
    def delete_verify_login(self) -> AeMessageResponse:
        return AeMessageResponse.model_validate(self._delete("/verifyLogin"))

    @allure.step("POST /api/createAccount")
    def create_account(self, payload: AeCreateAccountRequest) -> AeMessageResponse:
        return AeMessageResponse.model_validate(
            self._post("/createAccount", form=payload.model_dump())
        )

    @allure.step("DELETE /api/deleteAccount")
    def delete_account(self, email: str, password: str) -> AeMessageResponse:
        return AeMessageResponse.model_validate(
            self._delete("/deleteAccount", form={"email": email, "password": password})
        )

    @allure.step("PUT /api/updateAccount")
    def update_account(self, payload: AeCreateAccountRequest) -> AeMessageResponse:
        return AeMessageResponse.model_validate(
            self._put("/updateAccount", form=payload.model_dump())
        )

    @allure.step("GET /api/getUserDetailByEmail")
    def get_user_detail(self, email: str) -> AeUserDetailResponse:
        return AeUserDetailResponse.model_validate(
            self._get("/getUserDetailByEmail", params={"email": email})
        )
