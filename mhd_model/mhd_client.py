import datetime
import enum
import logging
import time
import traceback
from pathlib import Path
from typing import Literal

import httpx2
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel, to_pascal

logger = logging.getLogger(__name__)


class MhdBaseModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_serialization_defaults_required=True,
        field_title_generator=lambda field_name, field_info: to_pascal(
            field_name.replace("_", " ").strip()
        ),
        alias_generator=to_camel,
    )


class SubmittedRevision(MhdBaseModel):
    accession: str | None
    revision: int | None
    revision_datetime: datetime.datetime | None
    description: str | None
    repository_revision: int | None
    repository_revision_datetime: datetime.datetime | None
    status: str | None


class RepositoryToken(MhdBaseModel):
    api_token_name: str | None = None
    api_token: str | None = None
    expiration_time: str | None = None
    message: str | None = None


class RepositoryTokenValidation(MhdBaseModel):
    valid: bool | None = None
    message: str | None = None


class ApiTokenStatus(enum.IntEnum):
    INVALID = 0
    VALID = 1


class ApiTokenModel(MhdBaseModel):
    name: None | str
    description: None | str
    expiration_datetime: None | datetime.datetime
    status: None | ApiTokenStatus
    created_at: None | datetime.datetime
    modified_at: None | datetime.datetime


class MhdClientError(Exception):
    def __init__(self, message: str):
        self.message = message


class ApiTokenInvalidation(MhdBaseModel):
    invalidated: None | bool = None
    message: None | str = None


AccessionType = Literal["mhd", "legacy", "test-legacy", "test-mhd", "dev"]


class MhdAuthClient:
    def __init__(
        self, signed_jwt: str, mhd_webservice_base_url: str, api_version: str = "v0.1"
    ):
        if not signed_jwt:
            logger.error("Signed JWT token is not provided")
            raise MhdClientError("Signed JWT token is not provided")
        if not mhd_webservice_base_url:
            logger.error("MHD webservice base URL is not provided")
            raise MhdClientError("MHD webservice base URL is not provided")
        self.signed_jwt = signed_jwt
        self.mhd_webservice_base_url = mhd_webservice_base_url.lstrip("/")
        self.api_version = api_version.replace(".", "_") if api_version else "v0_1"
        suffix = "/" + self.api_version
        if mhd_webservice_base_url.endswith(suffix):
            self.mhd_webservice_base_url = self.mhd_webservice_base_url.replace(
                suffix, ""
            )

    def list_api_tokens(
        self, token_name: None | str, include_invalid_api_tokens: None | bool = None
    ) -> list[ApiTokenModel]:
        url = f"{self.mhd_webservice_base_url}/{self.api_version}/api-tokens"
        params = {
            "name": token_name,
        }
        if include_invalid_api_tokens is not None:
            params["include_invalid_api_tokens"] = include_invalid_api_tokens

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-signed-jwt-token": self.signed_jwt,
        }
        text = ""
        try:
            response = httpx2.get(url, headers=headers, params=params)
            text = response.text
            response_json = response.json()
            tokens = [
                ApiTokenModel.model_validate(x)
                for x in response_json.get("tokens") or []
            ]
            return tokens

        except Exception as ex:
            if isinstance(ex, MhdClientError):
                raise ex
            logger.exception(ex)
            raise MhdClientError(
                f"Failed to list MHD client API tokens: {text} {ex!s} "
            ) from ex

    def get_new_api_token(
        self,
        token_name: str,
        description: None | str = None,
        expiration_time: None | datetime.datetime = None,
    ) -> RepositoryToken:
        url = f"{self.mhd_webservice_base_url}/{self.api_version}/api-tokens"
        params = {}
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-signed-jwt-token": self.signed_jwt,
            "x-name": token_name,
        }
        if expiration_time:
            headers["x-expiration-time"] = expiration_time.isoformat()
        if description:
            headers["x-description"] = description
        text = ""
        try:
            response = httpx2.post(url, headers=headers, params=params)
            text = response.text
            # response.raise_for_status()
            response_json = response.json()

            token_info = RepositoryToken.model_validate(response_json)
            if not token_info.api_token:
                raise MhdClientError(token_info.message)
            return token_info

        except Exception as ex:
            if isinstance(ex, MhdClientError):
                raise ex
            logger.exception(ex)
            raise MhdClientError(
                f"Failed to create new MHD client API token: {text} {ex!s} "
            ) from ex

    def delete_api_token(self, api_token: str) -> ApiTokenInvalidation:
        url = f"{self.mhd_webservice_base_url}/{self.api_version}/api-tokens"
        params = {}
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-signed-jwt-token": self.signed_jwt,
            "x-api-token": api_token,
        }
        text = ""
        try:
            response = httpx2.delete(url, headers=headers, params=params)
            text = response.text
            # response.raise_for_status()
            response_json = response.json()

            deletion_response = ApiTokenInvalidation.model_validate(response_json)
            if not deletion_response or deletion_response.invalidated is None:
                raise MhdClientError("Deletion response is not valid.")
            return deletion_response

        except Exception as ex:
            if isinstance(ex, MhdClientError):
                raise ex
            logger.exception(ex)
            raise MhdClientError(
                f"Failed to delete MHD client API token: {text} {ex!s} "
            ) from ex

    def validate_api_token(self, api_token: str) -> RepositoryTokenValidation:
        url = f"{self.mhd_webservice_base_url}/{self.api_version}/api-tokens/validation"
        params = {}
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-signed-jwt-token": self.signed_jwt,
            "x-api-token": api_token,
        }
        text = ""
        try:
            response = httpx2.post(url, headers=headers, params=params)
            text = response.text
            response_json = response.json()

            token_info = RepositoryTokenValidation.model_validate(response_json)
            return token_info

        except Exception as ex:
            if isinstance(ex, MhdClientError):
                raise ex
            logger.exception(ex)
            raise MhdClientError(
                f"Failed to validate MHD client API token: {text} {ex!s} "
            ) from ex


class MhdClient:
    def __init__(
        self, mhd_webservice_base_url: str, api_token: str, api_version: str = "v0.1"
    ):
        if not api_token:
            logger.error("API token is not provided")
            raise MhdClientError("API token is not provided")
        if not mhd_webservice_base_url:
            logger.error("MHD webservice base URL is not provided")
            raise MhdClientError("MHD webservice base URL is not provided")
        self.api_token = api_token
        self.mhd_webservice_base_url = mhd_webservice_base_url.lstrip("/")
        self.api_version = api_version.replace(".", "_") if api_version else "v0_1"
        suffix = "/" + self.api_version
        if mhd_webservice_base_url.endswith(suffix):
            self.mhd_webservice_base_url = self.mhd_webservice_base_url.replace(
                suffix, ""
            )

    def get_new_mhd_accession(
        self,
        dataset_repository_identifier: str,
        accession_type: AccessionType,
    ) -> str:
        if not dataset_repository_identifier:
            message = "Dataset repository identifier is not provided"
            logger.error(message)
            raise MhdClientError(message)
        if not accession_type:
            message = "Accession type is not provided"
            logger.error(message)
            raise MhdClientError(message)
        url = f"{self.mhd_webservice_base_url}/{self.api_version}/identifiers"
        params = {
            "accession_type": accession_type,
            "dataset_repository_identifier": dataset_repository_identifier,
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-api-token": self.api_token,
        }
        try:
            response = httpx2.post(url, headers=headers, params=params)
            response.raise_for_status()
            response_json = response.json()
            accession = response_json.get("assignment", {}).get("accession")
            if not accession:
                message = "Accession is not provided"
                logger.error(message)
                raise MhdClientError(message)
            return accession
        except Exception as ex:
            logger.exception(ex)
            raise MhdClientError(f"Failed to get new MHD accession: {ex!s}") from ex

    def submit_announcement_file(
        self,
        dataset_repository_id: str,
        mhd_id: None | str,
        file_path: str,
        announcement_reason: str,
        max_retries: int = 10,
        sleep_time: int = 10,
    ) -> SubmittedRevision:
        file = Path(file_path)
        if not file.exists():
            message = f"File {file_path} does not exist"
            logger.error(message)
            raise MhdClientError(message)

        if not dataset_repository_id:
            message = "Dataset repository ID is not provided"
            logger.error(message)
            raise MhdClientError(message)

        if not announcement_reason:
            message = "Announcement reason is not provided"
            logger.error(message)
            raise MhdClientError(message)

        if not mhd_id:
            mhd_id = dataset_repository_id
        try:
            logger.info(
                "%s announcement file is being submitted to MetabolomicsHub...",
                dataset_repository_id,
            )

            url = f"{self.mhd_webservice_base_url}/{self.api_version}/datasets/{mhd_id}/announcements"
            headers = {"x-api-token": self.api_token, "Accept": "application/json"}
            post_headers = headers.copy()
            # post_headers["Content-Type"] = "multipart/form-data"
            post_headers["x-announcement-reason"] = announcement_reason or ""
            logger.info(
                "%s %s submission on URL  %s", dataset_repository_id, mhd_id, url
            )
            with file.open("rb") as f:
                files = {"file": (file.name, f, "application/json")}

                response = httpx2.post(url, headers=post_headers, files=files)
                response.raise_for_status()
                response_json = response.json()

            task_id = response_json.get("taskId")
            error = None
            if task_id and response.status_code == 200:
                logger.info("Validation task started with id: %s", task_id)
                status_url = f"{self.mhd_webservice_base_url}/{self.api_version}/datasets/{mhd_id}/tasks/{task_id}"
                for iteration in range(max_retries):
                    time.sleep(sleep_time)
                    try:
                        logger.debug(
                            "Validation task status check (Iteration: %s)",
                            iteration + 1,
                        )
                        status_response = httpx2.get(status_url, headers=headers)
                        logger.info(
                            "Validation task check response code: %s",
                            status_response.status_code,
                        )
                        logger.info("Response: %s", status_response.text)
                        if status_response.status_code in (200, 201):
                            status_data = status_response.json()
                            task_status = status_data.get("taskStatus", "") or ""
                            logger.debug(
                                "Validation task check status: %s", task_status
                            )
                            if task_status.upper() == "SUCCESS":
                                logger.info("Submission is successful")
                                return SubmittedRevision.model_validate(
                                    status_data.get("result", {})
                                )
                            elif task_status.upper() == "FAILED":
                                logger.info("Submission failed")
                                raise MhdClientError(
                                    str(status_data.get("messages", []))
                                )
                        elif status_response.status_code != 425:
                            message = f"Validation task status check failed: {status_response.text}"
                            logger.error(message)
                            raise MhdClientError(message)
                    except Exception as ex:
                        if isinstance(ex, MhdClientError):
                            raise ex
                        logger.error(
                            "Validation task status check failed (Iteration: %s): %s",
                            iteration + 1,
                            str(ex),
                        )
                        traceback.print_exc()
                message = f"Validation task failed after retries: {error or ''}"
                logger.error(message)
                raise MhdClientError(message)
            else:
                if task_id:
                    message = f"Validation task failed with status code: {response.status_code}"
                else:
                    message = "Validation task response does not contain task id"
                logger.error(message)
                raise MhdClientError(message)

        except Exception as ex:
            if isinstance(ex, MhdClientError):
                raise ex
            message = f"MetabolomicsHub submission error: {ex!s}"
            logger.error(message)
            raise MhdClientError(message)
