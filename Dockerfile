# =================================================================
# Dockerfile for ThyroScope 
# =================================================================
FROM broadinstitute/gatk:4.4.0.0

LABEL maintainer="H-Lee Lab"

ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# 1. Install System Tools
RUN apt-get update && apt-get install -y \
    bwa \
    samtools \
    trimmomatic \
    fastqc \
    wget \
    unzip \
    python3-pip \
    python3-dev \
    gcc \
    && apt-get clean

# 2. Install Mosdepth (For Coverage Analysis, direct binary download)
RUN wget https://github.com/brentp/mosdepth/releases/download/v0.3.6/mosdepth -O /usr/bin/mosdepth \
    && chmod +x /usr/bin/mosdepth

# 3. Install Python Libraries (Including MultiQC)
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir \
    pandas==1.1.5 \
    openpyxl \
    myvariant \
    multiqc==1.14 \
    importlib-metadata==4.8.3

# 4. Install Trimmomatic Adapters
RUN mkdir -p /usr/share/trimmomatic/adapters \
    && wget https://raw.githubusercontent.com/usadellab/Trimmomatic/master/adapters/TruSeq3-PE.fa -O /usr/share/trimmomatic/adapters/TruSeq3-PE.fa

# 5. Install SnpEff (Core Engine Only)
WORKDIR /pipeline
RUN wget https://snpeff-public.s3.amazonaws.com/versions/snpEff_v5_1d_core.zip \
    && unzip snpEff_v5_1d_core.zip \
    && rm snpEff_v5_1d_core.zip

# 6. Copy Scripts and Target Files
COPY pipeline_script.py /pipeline/
COPY endocrine_targets.bed /pipeline/
COPY hypopara_targets.bed /pipeline/

# 7. Set Permissions and Entrypoint
RUN chmod +x /pipeline/pipeline_script.py
ENTRYPOINT ["/usr/bin/python3", "/pipeline/pipeline_script.py"]
