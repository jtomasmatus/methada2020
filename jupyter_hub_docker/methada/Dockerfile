FROM python:3

RUN mkdir /app
WORKDIR /app

COPY jupyterhub_config.py /app/jupyterhub_config.py
RUN echo "deb https://cran.stat.unipd.it/bin/linux/debian buster-cran35/" >> /etc/apt/sources.list
RUN apt-key adv --keyserver keys.gnupg.net --recv-key 'E19F5F87128899B192B1A2C2AD5F960A256A04AF'
RUN apt-get update
RUN apt-get -y install npm
RUN apt-get -y install r-base r-base-dev
RUN apt-get -y install openjdk-11-jdk
RUN pip install jupyterhub
RUN npm install -g configurable-http-proxy
RUN pip install notebook
RUN pip install jupyterlab
RUN pip install numpy scipy pandas matplotlib pysradb scikit-learn seaborn
RUN Rscript -e 'install.packages("IRkernel")'
RUN Rscript -e 'install.packages("BiocManager")'
RUN Rscript -e 'BiocManager::install("RNAseq123")'
RUN Rscript -e 'BiocManager::install("RnaSeqGeneEdgeRQL")'
RUN Rscript -e 'BiocManager::install("rnaseqGene")'
RUN Rscript -e 'BiocManager::install("tximport")'
RUN Rscript -e 'BiocManager::install("goseq")'
RUN Rscript -e 'BiocManager::install("topGO")'
RUN Rscript -e 'BiocManager::install("recounts")'
RUN Rscript -e 'BiocManager::install("RColorBrewer")'
RUN Rscript -e 'BiocManager::install("tidyverse")'
RUN Rscript -e 'BiocManager::install("recount")'
RUN Rscript -e 'BiocManager::install("Rsubread")'
RUN Rscript -e 'BiocManager::install("plotly")'
RUN Rscript -e 'BiocManager::install("ggrepel")'
RUN Rscript -e 'BiocManager::install("biomformat")'
RUN Rscript -e 'BiocManager::install("phyloseq")'
RUN Rscript -e 'BiocManager::install("remotes")'
RUN Rscript -e 'BiocManager::install("AnnotationHub")'
RUN Rscript -e 'remotes::install_github("twbattaglia/btools")'
RUN Rscript -e 'IRkernel::installspec(user = FALSE)'
