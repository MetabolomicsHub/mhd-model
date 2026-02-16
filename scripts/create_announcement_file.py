import json
from pathlib import Path

from mhd_model.convertors.announcement.v0_1.legacy.mhd2announce import (
    create_announcement_file,
)
from mhd_model.log_utils import set_basic_logging_config

if __name__ == "__main__":
    set_basic_logging_config()
    mtbls_public_ftp_base_url: str = (
        "http://ftp.ebi.ac.uk/pub/databases/metabolights/studies/public"
    )
    mw_public_ftp_base_url: str = "ftp://www.metabolomicsworkbench.org/Studies"
    # files = list(Path("tests/data/mhd_data/legacy").glob("*.mhd.json"))
    files = list(Path().glob("MTBLS30008987.mhd.json"))
    for file in files:
        txt = file.read_text()
        mhd_data_json = json.loads(txt)
        study_id = file.name.removesuffix(".mhd.json")
        if study_id.startswith("MTBLS") or study_id.startswith("REQ"):
            mhd_file_url = f"{mtbls_public_ftp_base_url}/{study_id}/{study_id}.mhd.json"
        elif study_id.startswith("ST"):
            mhd_file_url = f"{mw_public_ftp_base_url}/{study_id}/{study_id}.mhd.json"
        else:
            mhd_file_url = None

        # Path("tests/data/announcement_files/legacy").mkdir(parents=True, exist_ok=True)
        announcement_file_path = f"{study_id}.announcement.json"
        create_announcement_file(mhd_data_json, mhd_file_url, announcement_file_path)
