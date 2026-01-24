import datetime
import logging
import time
from pathlib import Path
from typing import Literal, Optional

import httpx
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel, to_pascal

logger = logging.getLogger(__name__)


class MhdBaseModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        JSON_schema_serialization_defaults_required=True,
        field_title_generator=lambda field_name, field_info: to_pascal(
            field_name.replace("_", " ").strip()
        ),
        alias_generator=to_camel,
    )


class SubmittedRevision(MhdBaseModel):
    accession: Optional[str]
    revision: Optional[int]
    revision_datetime: Optional[datetime.datetime]
    description: Optional[str]
    repository_revision: Optional[int]
    repository_revision_datetime: Optional[datetime.datetime]
    status: Optional[str]


class MhdClientError(Exception):
    def __init__(self, message: str):
        self.message = message


AccessionType = Literal["mhd", "legacy", "test", "dev"]


class MhdClient:
    def __init__(self, mhd_webservice_base_url: str, api_key: str):
        if not api_key:
            logger.error("API key is not provided")
            raise MhdClientError("API key is not provided")
        if not mhd_webservice_base_url:
            logger.error("MHD webservice base URL is not provided")
            raise MhdClientError("MHD webservice base URL is not provided")
        self.api_key = api_key
        self.mhd_webservice_base_url = mhd_webservice_base_url

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
        url = f"{self.mhd_webservice_base_url}/v0_1/identifiers"
        params = {
            "accession_type": accession_type,
            "dataset_repository_identifier": dataset_repository_identifier,
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-api-token": self.api_key,
        }
        try:
            response = httpx.post(url, headers=headers, params=params)
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
            raise MhdClientError(f"Failed to get new MHD accession: {str(ex)}") from ex

    def submit_announcement_file(
        self,
        dataset_repository_id: str,
        mhd_id: None | str,
        file_path: str,
        announcement_reason: str,
        max_retries: int = 10,
        sleep_time: int = 5,
    ) -> SubmittedRevision:
        file = Path(file_path)
        if not file.exists():
            message = "File %s does not exist" % file_path
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

            url = f"{self.mhd_webservice_base_url}/v0_1/datasets/{mhd_id}/announcements"
            headers = {"x-api-token": self.api_key, "Accept": "application/json"}
            post_headers = headers.copy()
            # post_headers["Content-Type"] = "multipart/form-data"
            post_headers["x-announcement-reason"] = announcement_reason or ""

            with file.open("rb") as f:
                files = {"file": (file.name, f, "application/json")}

                response = httpx.post(url, headers=post_headers, files=files)
                response.raise_for_status()
                response_json = response.json()

            task_id = response_json.get("taskId")
            if task_id and response.status_code == 200:
                logger.info("Validation task started with id: %s", task_id)
                status_url = f"{self.mhd_webservice_base_url}/v0_1/datasets/{mhd_id}/tasks/{task_id}"
                for iteration in range(max_retries):
                    try:
                        status_response = httpx.get(status_url, headers=headers)

                        if status_response.status_code == 200:
                            status_data = status_response.json()
                            accession = status_data.get("result", {}).get(
                                "accession", ""
                            )
                            if accession:
                                revision = SubmittedRevision.model_validate(
                                    status_data.get("result", {})
                                )
                            return revision
                        elif status_response.status_code != 425:
                            message = "Validation task status check failed"
                            logger.error(message)
                            raise MhdClientError(message)
                    except Exception as ex:
                        logger.debug(
                            "Validation task status check failed (Iteration: %s): %s",
                            iteration + 1,
                            str(ex),
                        )
                    time.sleep(sleep_time)
                message = "Validation task failed after retries."
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
            message = f"MetabolomicsHub submission error: {str(ex)}"
            logger.error(message)
            raise MhdClientError(message)
