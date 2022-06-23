#
# Building a Docker Image with
# the Latest Ubuntu Version and
# Basic Python Install
# 
# Python for Algorithmic Trading
# (c) Dr. Yves J. Hilpisch
# The Python Quants GmbH
#

# latest Ubuntu version
FROM --platform=linux/amd64 ubuntu:latest

# Install linux dependencies
RUN apt-get update --yes && \
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

# Install Miniconda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O Miniconda.sh \
    && bash Miniconda.sh -b \
    && rm -rf Miniconda.sh

ENV PATH /root/miniconda3/bin:$PATH

# Install Python Libraries
RUN conda install --channel conda-forge --yes \
    # interactive data analytics in the browser
    jupyter \
    # Jupyter Lab environment
    jupyterlab \
    # Jupyter Lab extensions
    jupyterlab-git \
    jupyterlab-lsp \
    python-lsp-server \
    jupyterlab-spellchecker \
    #  numerical computing package
    numpy \
    # wrapper for HDF5 binary storage
    pytables \
    #  data analysis package
    pandas \
    # standard plotting library
    matplotlib \
    # statistical plotting library
    seaborn \
    # wrapper for Quandl data API
    quandl \
    # machine learning library
    # scikit-learn \
    # package for Excel interaction
    openpyxl \
    # packages for Excel interaction
    xlrd xlwt \
    # package to manage yaml files
    pyyaml

RUN pip install --upgrade pip
RUN pip install \
    # logging and debugging
    q \
    # interactive D3.js plots
    plotly \
    # combining plotly with pandas
    cufflinks \
    # deep learning library
    # tensorflow \
    # deep learning library
    # keras \
    # Python wrapper for the Refinitiv Eikon Data API
    eikon

# Python wrapper for Oanda API
# RUN pip install git+git://github.com/yhilpisch/tpqoa

# Install the project's specific dependencies
ADD requirements.txt /
RUN pip install -r requirements.txt

# ---

# COPYING THE FILES
RUN mkdir /root/.jupyter
RUN mkdir /root/.ssh
ADD mycert.pem /root/.jupyter/
ADD mykey.key /root/.jupyter/
ADD gh /root/.ssh/
ADD gh.pub /root/.ssh/
ADD jupyter_notebook_config.py /root/.jupyter/
# ADD requirements.txt /

# change rights for the script
# RUN chmod u+x /install.sh
# run the bash script
# RUN /install.sh
# prepend the new path
ENV PATH /root/miniconda3/bin:$PATH

EXPOSE 8888

WORKDIR /app

ENTRYPOINT ["jupyter", "lab","--ip=0.0.0.0","--allow-root"]