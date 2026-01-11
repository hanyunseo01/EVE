# WES Pipeline for Thyroid & Parathyroid Disorders

This repository contains the clinician-friendly bioinformatics pipeline described in the paper:
> **"Comprehensive Genetic Diagnosis Pipeline for Thyroid and Parathyroid Disorders"**

## 1. Overview
We developed a streamlined pipeline designed for endocrinologists to process WES raw data (FASTQ) and identify pathogenic variants in **25 key thyroid/parathyroid genes** 

## 2. Repository Contents
* `Dockerfile`: Contains the pre-built environment (BWA, GATK, Python).
* `pipeline_script.py`: The main automation script for analysis.
* `targets.bed`: Genomic coordinates for the virtual gene panel (hg38).

## 3. How to Run (Step-by-Step)
You don't need to install complex software. Just use **Docker**.

### Step A. Pull the Docker Image
```bash
docker pull your-docker-id/thyroseq:v1.0
```

### Step B. Build the Image (Alternative)
If you downloaded this repository code, you can build the image on your computer:
```bash
# Run this command in the folder containing the Dockerfile
docker build -t thyroseq:v1.0 .
```

### Step C. Run the Analysis
1. Create a folder named `data`.
2. Place your FASTQ files (e.g., `Patient_R1.fastq.gz`, `Patient_R2.fastq.gz`) and reference genome files inside the `data` folder.
3. Run the following command:

```bash
# Windows (PowerShell)
docker run --rm -v ${PWD}/data:/data thyroseq:v1.0

# Mac / Linux
docker run --rm -v $(pwd)/data:/data thyroseq:v1.0
```

## 4. Requirements
* **OS:** Windows 10/11 (Pro recommended), macOS, or Linux
* **Software:** Docker Desktop
* **Hardware:** Minimum 16GB RAM (32GB recommended for faster processing)

## 5. Contact & Citation
If you use this pipeline for your research or clinical practice, please cite our paper:
* **Authors:** 
* **Title:** 
* **DOI:** 

For questions, please contact:
* **Lab:** 
* **Email:** 
