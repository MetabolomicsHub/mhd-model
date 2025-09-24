# MetabolomicsHub Common Data Model and Utility Tools (mhd-model)


You can find documentation [here](https://metabolomicshub.github.io/mhd-model/)


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

mhd-model


```