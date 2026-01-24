# MetabolomicsHub Common Data Model and Utility Tools (mhd-model)

You can find documentation [on Github](https://metabolomicshub.github.io/mhd-model/)

## Development Environment

Development environment for linux or mac

```bash

# install python package manager uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# add $HOME/.local/bin to your PATH, either restart your shell or run
export PATH=$HOME/.local/bin:$PATH

# install git from https://git-scm.com/downloads
# Linux command
apt update; apt install git -y

# Mac command
# brew install git

# clone project from github
git clone https://github.com/MetabolomicsHub/mhd_model.git

cd mhd-model

# install python if it is not installed
uv python install 3.12

# install python dependencies
uv sync

# install pre-commit to check repository integrity and format checking
uv run pre-commit

# open your IDE (vscode, pycharm, etc.) and set python interpreter as .venv/bin/python

```

## Commandline Usage

```bash
# you can use any python version >= 3.12
pip install mhd-model

mhd-cli


```

## Example API Usage

```python

from mhd_model.mhd_client import MhdClient, MhdClientError

mhd_webservice_base_url = "https://www.metabolomicshub.org/api/submission"
api_key = "<your-api-key>"

def get_new_mhd_accession_example():
    mhd_client: MhdClient = MhdClient(mhd_webservice_base_url, api_key)

    try:
        accession = mhd_client.get_new_mhd_accession(
            dataset_repository_identifier="MTBLS1234567", accession_type="mhd"
        )
        print("Accession: %s" % accession)
    except MhdClientError as ex:
        print("Error: %s" % ex.message)

def get_new_test_mhd_accession_example():
    mhd_client: MhdClient = MhdClient(mhd_webservice_base_url, api_key)

    try:
        accession = mhd_client.get_new_mhd_accession(
            dataset_repository_identifier="MTBLS4444", accession_type="test"
        )
        print("Accession: %s" % accession)
    except MhdClientError as ex:
        print("Error: %s" % ex.message)


def submit_legacy_dataset_example():
    announcement_file_path = "MTBLS9876543.announcement.json"
    dataset_repository_id = "MTBLS9876543"
    announcement_reason="Initial revision"
    mhd_client: MhdClient = MhdClient(mhd_webservice_base_url, api_key)

    try:
        revision: SubmittedRevision = mhd_client.submit_announcement_file(
            dataset_repository_id=dataset_repository_id,
            mhd_id=None,
            file_path=announcement_file_path,
            announcement_reason=announcement_reason,
        )
        print("Revision: %s" % revision.revision)
    except MhdClientError as ex:
        print("Error: %s" % ex.message)


def submit_mhd_dataset_example():
    announcement_file_path = "MTBLS9876543.announcement.json"
    mhd_id = "MHD0000001"
    dataset_repository_id = "MTBLS22222"
    announcement_reason="Initial revision"
    mhd_client: MhdClient = MhdClient(mhd_webservice_base_url, api_key)

    try:
        revision: SubmittedRevision = mhd_client.submit_announcement_file(
            dataset_repository_id=dataset_repository_id,
            mhd_id=mhd_id,
            file_path=announcement_file_path,
            announcement_reason=announcement_reason,
        )
        print("Revision: %s" % revision.revision)
    except MhdClientError as ex:
        print("Error: %s" % ex.message)


```
