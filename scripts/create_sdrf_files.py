import json
from pathlib import Path

from mhd_model.convertors.sdrf.mhd2sdrf import create_sdrf_files
from scripts.utils import set_basic_logging_config

if __name__ == "__main__":
    set_basic_logging_config()
    mtbls_public_ftp_base_url: str = (
        "ftp://ftp.ebi.ac.uk/pub/databases/metabolights/studies/public"
    )

    files = list(Path("tests/data/mhd_data/legacy").glob("MTBLS3107_full.mhd.json"))
    for file in files:
        txt = file.read_text()
        mhd_data_json = json.loads(txt)
        study_id = file.name.removesuffix(".mhd.json")
        if study_id.startswith("MTBLS"):
            mhd_file_url = f"{mtbls_public_ftp_base_url}/{study_id}/{study_id}.mhd.json"
        else:
            mhd_file_url = None
        sdrf_file_root_path = "tests/data/sdrf_files"
        Path(sdrf_file_root_path).mkdir(parents=True, exist_ok=True)

        create_sdrf_files(mhd_data_json, mhd_file_url, sdrf_file_root_path)
