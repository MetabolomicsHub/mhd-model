import json
from pathlib import Path

from mhd_model.convertors.announcement.v0_1.legacy.mhd2announce import (
    create_announcement_file,
)
from scripts.utils import set_basic_logging_config

if __name__ == "__main__":
    set_basic_logging_config()

    study_ids = [
        "MHDA003107",
    ]

    files = list(Path("tests/data/mhd_data/mtbls").glob("*.mhd.json"))
    for file in files:
        txt = file.read_text()
        mhd_data_json = json.loads(txt)
        study_id = file.name.removesuffix(".mhd.json")
        # txt = None
        public_ftp_base_url: str = (
            "ftp://ftp.ebi.ac.uk/pub/databases/metabolights/studies/public"
        )
        mhd_file_url = f"{public_ftp_base_url}/{study_id}/{study_id}.mhd.json"
        Path("tests/data/announcement_files").mkdir(parents=True, exist_ok=True)
        annoucement_file_path = (
            f"tests/data/announcement_files/{study_id}_announcement.json"
        )
        create_announcement_file(mhd_data_json, mhd_file_url, annoucement_file_path)
