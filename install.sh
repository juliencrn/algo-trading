#!/bin/bash
#
# Script to Install
# Linux System Tools and
# Basic Python Components
#
# Python for Algorithmic Trading
# (c) Dr. Yves J. Hilpisch
# The Python Quants GmbH
#
# GENERAL LINUX
# apt-get update  # updates the package index cache
# apt-get upgrade -y  # updates packages
# installs system tools
# apt-get install -y bzip2 gcc git iputils-ping # system tools
# apt-get install -y htop screen vim wget git git-lfs # system tools
# apt-get upgrade -y bash  # upgrades bash if necessary
# apt-get clean  # cleans up the package index cache

apt-get update --yes && \
    # - apt-get upgrade is run to patch known vulnerabilities in apt-get packages as
    #   the ubuntu base image is rebuilt too seldom sometimes (less than once a month)
    apt-get upgrade --yes && \
    apt-get install --yes --no-install-recommends \
    bzip2 \
    ca-certificates \
    fonts-liberation \
    locales \
    pandoc \
    gcc \
    iputils-ping \
    sudo \
    screen \
    vim \
    curl \
    git git-lfs \
    wget && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && \
    echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen

# INSTALL MINICONDA
# downloads Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O Miniconda.sh
bash Miniconda.sh -b  # installs it
rm -rf Miniconda.sh  # removes the installer

# prepends the new path for the current session
export PATH="/root/miniconda3/bin:$PATH"
# prepends the new path in the shell configuration
cat >> ~/.profile <<EOF
export PATH="/root/miniconda3/bin:$PATH"
EOF

# INSTALLING PYTHON LIBRARIES
conda install -y jupyter  # interactive data analytics in the browser
conda install -y jupyterlab  # Jupyter Lab environment
conda install -y numpy  #  numerical computing package
conda install -y pytables  # wrapper for HDF5 binary storage
conda install -y pandas  #  data analysis package
conda install -y matplotlib  # standard plotting library
conda install -y seaborn  # statistical plotting library
conda install -y quandl  # wrapper for Quandl data API
conda install -y scikit-learn  # machine learning library
conda install -y openpyxl  # package for Excel interaction
conda install -y xlrd xlwt  # packages for Excel interaction
conda install -y pyyaml  # package to manage yaml files

pip install --upgrade pip  # upgrading the package manager
pip install q  # logging and debugging
pip install plotly  # interactive D3.js plots
pip install cufflinks  # combining plotly with pandas
pip install tensorflow  # deep learning library
pip install keras  # deep learning library
pip install eikon  # Python wrapper for the Refinitiv Eikon Data API
# Python wrapper for Oanda API
pip install git+git://github.com/yhilpisch/tpqoa
# Install the project's specific dependencies
pip install -r requirements.txt

# Install Jupyter lab extensions
conda install -c conda-forge \
    jupyterlab-git \
    jupyterlab-lsp \
    python-lsp-server


# COPYING FILES AND CREATING DIRECTORIES
mkdir /root/.jupyter
mv /root/jupyter_notebook_config.py /root/.jupyter/
mv /root/mycert.pem /root/.jupyter
mv /root/mykey.key /root/.jupyter
# mkdir /root/notebook
# cd /root/notebook

# # STARTING JUPYTER LAB
# jupyter lab &
