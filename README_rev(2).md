# 🧬 EVE: Endocrine Variant Extractor
### Clinical-Grade WES Pipeline for Endocrine and Parathyroid Disorders

[![Docker Image Version](https://img.shields.io/docker/v/hanyunseo01/eve/latest?color=blue&label=Docker%20Image)](https://hub.docker.com/r/hanyunseo01/eve)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20(Intel%2FApple%20Silicon)%20%7C%20Linux-lightgrey)](https://www.docker.com/)
[![YouTube Tutorial](https://img.shields.io/badge/YouTube-Tutorial-red?logo=youtube)](https://youtube.com/)

**EVE (Endocrine Variant Extractor)** is a streamlined, containerized bioinformatics pipeline optimized for the clinical interpretation of **Whole Exome Sequencing (WES)** data, with a specific focus on endocrine and parathyroid pathologies.

By leveraging a **"Lightweight Containerization Strategy"** and a **"Virtual Panel approach"**, EVE allows clinicians to bypass complex command-line interfaces. It automates the entire workflow from raw FASTQ to a clinical-grade Excel report with a single click, focusing specifically on 26 high-priority genes associated with parathyroid disorders and an expanded panel of 400 genes related to broader endocrine pathologies.

By integrating a **"Virtual Panel"** approach, EVE filters massive genomic data using a dual-tiered strategy: a **Core Parathyroid Panel (26 genes)** for primary high-confidence screening and an **Endocrine Expansion Panel (400 genes)** for comprehensive differential diagnosis. This enables clinicians to identify pathogenic variants with high precision and minimal computational overhead.

The Docker image is published as a **multi-architecture build** (`linux/amd64` + `linux/arm64`), so EVE runs natively on both Intel and Apple Silicon Macs as well as standard Windows PCs.

![EVE Pipeline Diagram](EVE%20Pipeline%20Architecture.jpg)

---

## 🎥 Video Tutorial (Recommended for First-Time Users)

If this is your first time using EVE, **we strongly recommend watching the step-by-step video tutorial** before reading this document. The tutorial walks you through the entire workflow — from installing Docker on a fresh computer to interpreting your final clinical report — and is designed specifically for clinicians without prior bioinformatics experience.

▶️ **[Watch on YouTube](https://youtube.com/)**

Separate tutorials are provided for **macOS** and **Windows** users.

---

## 🚀 Key Features

* **🎯 Dual-Tiered Virtual Panel:** Implements a sophisticated filtering strategy designed to maximize diagnostic yield:
    * **Tier 1 (Core):** 26 high-priority genes directly associated with parathyroid disorders
    * **Tier 2 (Expansion):** 400 genes related to broader endocrine pathologies for expanded clinical investigation and differential diagnosis
* **🧬 Fully Customizable Panels:** Users can supply their own gene lists and substitute them into the pipeline without modifying any code — see the [Custom Gene Panels](#-using-your-own-gene-panel-advanced) section
* **🐳 Dockerized & Reproducible:** Encapsulates GATK 4.4, BWA, Samtools, and Python dependencies in a portable, multi-architecture Docker image (amd64 + arm64), ensuring identical results on any OS
* **📉 Lightweight Architecture:** Heavy reference databases (hg38 Ref, SnpEff DB) are externalized, keeping the Docker image light (~2GB) and easy to distribute
* **📊 Comprehensive QC Reports:**
    * **MultiQC:** Aggregates quality metrics (Trimming, Alignment, Duplication) into a single interactive HTML report
    * **Mosdepth:** Provides rapid coverage statistics to verify diagnostic depth (e.g., >20x) for target regions
* **🌍 Population & Clinical Annotation:**
    * **ClinVar & dbSNP:** Auto-fetches the latest pathogenicity data and rsIDs via `MyVariant.info`
    * **gnomAD:** Includes Global Allele Frequency (AF) to help differentiate rare variants from common polymorphisms
    * **Functional Prediction:** SIFT and PolyPhen-2 scores included
* **⚡ One-Click Automation:** Includes a Windows Batch script (`.bat`) for "Drag-and-Drop" style execution

---

## 🔬 Pipeline Workflow (Methods)

EVE automates the following bioinformatics steps in a sequential manner:

1.  **QC & Trimming** ✂️
    * **Tools:** `FastQC`, `Trimmomatic`
    * **Details:** Adapter removal, Quality trimming (`SlidingWindow:4:15`)
2.  **Alignment** 🧬
    * **Tool:** `BWA-MEM`
    * **Reference:** Aligned to the **GRCh38 (hg38)** reference genome
3.  **Post-Processing** 🧹
    * **Tools:** `Samtools` (Sort/Index), `GATK MarkDuplicates`
    * **Details:** Sorting BAM files and marking PCR duplicates to ensure accurate variant calling
4.  **Coverage Analysis** 📉
    * **Tool:** `Mosdepth`
    * **Details:** Rapid depth-of-coverage check specifically for the targeted regions
5.  **Variant Calling** 🔍
    * **Tool:** `GATK HaplotypeCaller`
    * **Virtual Panel Filtering:** To optimize speed and precision, variant calling is restricted to the **26 + 400 gene intervals** with `--interval-padding 100` to capture critical splice site regions
6.  **Annotation** 📝
    * **Tools:** `SnpEff` (HGVS notation), `MyVariant.info` API
    * **Databases:** ClinVar, gnomAD (Global AF), dbSNP (rsID), dbNSFP (SIFT/PolyPhen)
7.  **Tiered Reporting & Final Filtering** 📊
    * **Output:** A custom Python script aggregates all data into a **Hybrid Clinical Excel Report**
    * **Virtual Panel Filtering:** The script automatically categorizes variants into:
        * **Tier 1 Sheet:** Core Parathyroid Panel (26 genes)
        * **Tier 2 Sheet:** Endocrine Expansion Panel (400 genes)
    * **Quality Filtering:** Includes MultiQC HTML summary for batch-level quality metrics

---

## 🛠️ System Requirements

Before you begin, please check that your computer meets these minimum requirements:

| Item | Minimum | Recommended |
| :--- | :--- | :--- |
| **Operating System** | Windows 10/11, macOS 11+ (Intel or Apple Silicon), or Linux | Windows 11 / macOS 13+ |
| **CPU** | 4 cores | 8 cores |
| **Memory (RAM)** | 8 GB | **16 GB or more** |
| **Free Disk Space** | 50 GB | 100 GB+ |
| **Internet Connection** | Required for installation and annotation | Stable broadband |

> [!IMPORTANT]
> **About RAM:** GATK (the variant calling tool) requires a large amount of memory. If your computer has only 8 GB of RAM, the pipeline may run very slowly or crash. We strongly recommend at least 16 GB.

> [!NOTE]
> **For Windows users:** Docker Desktop requires **Windows 10/11 64-bit (Pro, Enterprise, or Home with WSL2)**. Windows 7 and 8 are not supported.

> [!NOTE]
> **For Apple Silicon Mac users (M1/M2/M3/M4):** The EVE Docker image is built for both `amd64` and `arm64`, so no special flags are required. Docker will automatically pull the correct architecture.

---

# 📥 Getting Started — A Complete Guide for First-Time Users

This guide assumes you have **no prior experience** with Docker, command lines, or bioinformatics tools. Please follow each step in order.

There are **5 preparation steps** you must complete **before** running the pipeline:

> **Step 1:** Install Docker Desktop
> **Step 2:** Start Docker Desktop and verify it works
> **Step 3:** Download the EVE Docker image
> **Step 4:** Download reference data (hg38 + SnpEff database)
> **Step 5:** Create your project folder and place your FASTQ files

Once these are done, you can move to the "How to Run" section.

---

## Step 1️⃣ — Install Docker Desktop

Docker is a free program that lets EVE run on any computer without needing to install dozens of bioinformatics tools separately. **You only need to install it once.**

### 🍎 For macOS users

1. Open your web browser and go to:
   👉 **https://www.docker.com/products/docker-desktop/**
2. Click the **"Download for Mac"** button.
   - **If you have an Apple Silicon Mac** (M1, M2, M3, or M4 chip — most Macs sold after late 2020): choose **"Apple Silicon"**
   - **If you have an Intel Mac** (older Macs sold before late 2020): choose **"Intel Chip"**

   > **💡 How to check which Mac you have:** Click the Apple logo (top-left corner) → **About This Mac**. Look at the **"Chip"** or **"Processor"** line.

3. Once the download finishes, double-click the `Docker.dmg` file in your **Downloads** folder.
4. In the window that appears, **drag the Docker whale icon into the Applications folder**.
5. Open **Applications** (in Finder), find **Docker**, and double-click it to launch.
6. macOS may ask: *"Are you sure you want to open this app downloaded from the internet?"* → click **Open**.
7. Docker may ask for your Mac password to install some system components → enter your password and click **OK**.
8. Accept the Docker license agreement when prompted.
9. You'll see the Docker whale icon 🐳 appear in your **menu bar** (top-right of the screen). When the whale stops animating and the menu shows **"Docker Desktop is running"**, installation is complete.

### 🪟 For Windows users

1. Open your web browser and go to:
   👉 **https://www.docker.com/products/docker-desktop/**
2. Click the **"Download for Windows"** button → choose **"AMD64"** (this is correct for almost all PCs).
3. Once the download finishes, double-click `Docker Desktop Installer.exe` in your **Downloads** folder.
4. When asked, **leave both checkboxes checked** (especially "Use WSL 2 instead of Hyper-V") and click **OK**.
5. Wait for installation to complete (this may take 5–10 minutes).
6. When the installer says **"Installation succeeded"** → click **"Close and restart"**. Your computer will restart.
7. After restart, Docker Desktop will open automatically. Accept the license agreement.
8. Docker may prompt you to install the **WSL 2 Linux kernel update**. If so:
   - Click the link it shows, download the update package
   - Run the downloaded `.msi` file
   - Restart Docker Desktop
9. You may be asked to sign in or create a Docker account → this is **optional**. You can click **"Continue without signing in"**.
10. When you see the Docker whale icon 🐳 in your **system tray** (bottom-right of the screen, next to the clock) and it's not blinking, Docker is ready.

> [!TIP]
> If you don't see the whale icon, click the small upward arrow `^` in the system tray to reveal hidden icons.

---

## Step 2️⃣ — Verify Docker is Working

Before downloading EVE, let's make sure Docker is properly installed.

### 🍎 macOS

1. Open **Terminal**. (Press `Cmd + Space`, type `Terminal`, press Enter.)
2. Type the following command and press **Enter**:
   ```bash
   docker --version
   ```
3. You should see something like: `Docker version 24.0.6, build ed223bc`
4. If you see this, Docker is working correctly. ✅
5. If you see *"command not found"*, Docker Desktop is not running. Open Docker Desktop from Applications and wait until the whale icon stops animating.

### 🪟 Windows

1. Open **PowerShell**. (Press the Windows key, type `PowerShell`, press Enter.)
2. Type the following command and press **Enter**:
   ```powershell
   docker --version
   ```
3. You should see something like: `Docker version 24.0.6, build ed223bc`
4. If you see this, Docker is working correctly. ✅
5. If you see an error, make sure Docker Desktop is running (check the system tray).

---

## Step 3️⃣ — Download the EVE Docker Image

Now you'll download the EVE pipeline itself. This is a one-time download (~2 GB).

1. Make sure **Docker Desktop is running** (whale icon visible).
2. Open **Terminal** (Mac) or **PowerShell** (Windows).
3. Type the following command and press **Enter**:
   ```bash
   docker pull hanyunseo01/eve:latest
   ```
4. You'll see lines like `Pulling from hanyunseo01/eve` and progress bars. This may take **5–20 minutes** depending on your internet speed.
5. When you see `Status: Downloaded newer image for hanyunseo01/eve:latest`, the download is complete. ✅

> [!TIP]
> To verify the download, type `docker images` and you should see `hanyunseo01/eve` in the list.

> [!NOTE]
> During the download, you will see many lines like `Pulling fs layer`. Each line is a separate piece of the image being downloaded **in parallel**. The download is not stuck — actual progress bars (with MB sizes) will appear once individual layers start transferring. The largest single layer is ~900 MB and may take several minutes by itself.

---

## Step 4️⃣ — Download Reference Data

EVE keeps its Docker image small by storing large reference files **separately**. You need to download these once.

1. Go to this link in your browser:
   👉 **[Google Drive — EVE Reference Data](https://drive.google.com/drive/folders/1SmEH-AxT4eHSB-vNVKc0ZphOGIe2zvVM?usp=drive_link)**
2. You'll see two folders:
   - **`ref`** — contains the hg38 human reference genome + BWA index files (~6 GB)
   - **`snpEff_db`** — contains the SnpEff annotation database (~3 GB)
3. Download **both folders** to your computer.
   - On Google Drive: right-click each folder → **Download** (Drive will zip them automatically).
4. Once downloaded, **unzip** both files. You should end up with two folders called `ref` and `snpEff_db`.

> [!IMPORTANT]
> The download is large (~9 GB total). Make sure you have a stable internet connection and enough disk space. Do not rename these folders.

---

## Step 5️⃣ — Set Up Your Project Folder

Now you'll create the folder where EVE will read your FASTQ files and write the results.

### 5.1 Create the folder structure

1. Choose a location on your computer (e.g., **Desktop** or **Documents**).
2. Create a new folder called **`EVE_Workspace`**.
3. **Inside** `EVE_Workspace`, create a folder called **`data`**.
4. Move the **`ref`** folder (from Step 4) **inside** the `data` folder.
5. Move the **`snpEff_db`** folder (from Step 4) directly **inside** `EVE_Workspace`.

The final structure must look **exactly** like this:

```text
📁 EVE_Workspace/
├── 📁 data/                    ← put your FASTQ files here
│    └── 📁 ref/                ← hg38.fasta + BWA index files
└── 📁 snpEff_db/
     └── 📁 hg38/               ← must contain 'snpEffectPredictor.bin'
```

> [!WARNING]
> **Folder names are case-sensitive.** `data` ≠ `Data` ≠ `DATA`. Match the exact spelling shown above.

### 5.2 Place your FASTQ files

1. Copy your paired-end sequencing files into the **`data`** folder.
2. Each sample must have **two files** (forward + reverse reads).
3. Files **must** be named in the following format:
   - `[SampleName]_1.fq.gz`  — forward reads
   - `[SampleName]_2.fq.gz`  — reverse reads

   ✅ **Correct examples:**
   - `Patient01_1.fq.gz` + `Patient01_2.fq.gz`
   - `SampleA_1.fq.gz` + `SampleA_2.fq.gz`

   ❌ **Incorrect examples** (the pipeline will NOT detect these):
   - `Patient01.fastq.gz` (wrong extension)
   - `Patient01_R1.fq.gz` (must be `_1` not `_R1`)
   - `Patient01_1.fq` (must be gzipped — `.gz`)

> [!IMPORTANT]
> **File extension requirement:** Input files **must** end in `.fq.gz`. Files ending in `.fastq.gz`, `.fq`, or `.fastq` will **not** be recognized.

> [!TIP]
> If your files are named `.fastq.gz`, you can simply rename them to `.fq.gz` — the content is identical.

---

🎉 **Preparation complete!** You're now ready to run EVE.

---

# 🏃‍♀️ How to Run EVE

Choose the option that matches your operating system.

> [!IMPORTANT]
> **Do not let your computer sleep during analysis.** A full WES sample takes **2–6 hours** to process. If your computer goes to sleep, the pipeline will pause and may need to be restarted.
> - **macOS:** Either keep your Mac awake via **System Settings → Lock Screen** (set "Turn display off" to "Never"), or prefix the run command with `caffeinate -i` (see below).
> - **Windows:** Open **Settings → System → Power & battery → Screen and sleep** and set both "On battery power" and "When plugged in" to "Never" for the duration of the run.
> - **Plug in your laptop** before starting.

---

### 🪟 Option A: Windows (One-Click — Recommended)

We provide a batch script for the simplest possible execution.

1. Download **`EVE.bat`** from this repository and place it in your `EVE_Workspace` folder.
2. Make sure Docker Desktop is running.
3. **Double-click `EVE.bat`**.
4. A black terminal window will open and the pipeline will start automatically.
5. Wait until you see: `[INFO] Pipeline Completed Successfully!`
6. **Do not close the terminal window** while the pipeline is running. Closing it will stop the analysis.

---

### 🍎 Option B: macOS (Manual Command)

1. Make sure Docker Desktop is running.
2. Open **Terminal**.
3. **Navigate to your `EVE_Workspace` folder.** For example, if it's on your Desktop:
   ```bash
   cd ~/Desktop/EVE_Workspace
   ```
   > **💡 Quick tip:** You can type `cd ` (with a space), then drag the `EVE_Workspace` folder from Finder into the Terminal window — the path will be filled in automatically. Then press Enter.

4. Copy and paste the following command into Terminal and press **Enter**:
   ```bash
   docker run --rm -it \
     -v "$PWD/data:/data" \
     -v "$PWD/snpEff_db:/pipeline/snpEff/data" \
     hanyunseo01/eve:latest
   ```
   > **💡 About `-it`:** This option keeps the pipeline's progress output visible in your terminal as it runs. Without `-it`, the terminal may appear blank even though the pipeline is actually running in the background.

5. The pipeline will start. You'll see progress messages like `[INFO] Step 1: QC ...`, `[SUCCESS] ...`, etc.
6. When you see `[INFO] Pipeline Completed Successfully!`, the analysis is done.

> [!TIP]
> **Keep your Mac awake during analysis:** Prefix the command with `caffeinate -i` to prevent macOS from sleeping while EVE is running. The full command becomes:
> ```bash
> caffeinate -i docker run --rm -it \
>   -v "$PWD/data:/data" \
>   -v "$PWD/snpEff_db:/pipeline/snpEff/data" \
>   hanyunseo01/eve:latest
> ```
> You can close the laptop lid only if connected to an external display; otherwise leave it open.

> [!TIP]
> The first time you run this, macOS may ask permission for Docker to access your folder. Click **OK**.

---

### 🐧 Option C: Linux

Same as macOS — open a terminal in your `EVE_Workspace` directory and run:
```bash
docker run --rm -it \
  -v "$PWD/data:/data" \
  -v "$PWD/snpEff_db:/pipeline/snpEff/data" \
  hanyunseo01/eve:latest
```

---

# 🧬 Using Your Own Gene Panel (Advanced)

EVE's default panels (26 parathyroid + 400 endocrine genes) reflect the panel routinely used at the Yonsei University endocrine genetics program, but **you can substitute your own gene lists** without modifying or rebuilding the Docker image.

This is useful if your institution uses a different panel, if you're investigating a different endocrine sub-domain, or if you want to test additional candidate genes.

## Overview

The workflow is:

1. Prepare a plain-text file listing your gene symbols (one per line)
2. Use the provided `generate_bed_new.py` helper script to convert it into a BED file with exon coordinates (50 bp padding for splice sites)
3. Pass your custom BED file to Docker using the `-v` mount option, replacing the built-in panel

No code changes are required. Docker's volume mounting feature transparently substitutes your file for the default one inside the container.

## Step 1 — Install Python and `requests`

Most computers already have Python 3 installed.

```bash
python3 --version
pip3 install requests
```

If `python3` is not found, download it from [python.org](https://www.python.org/downloads/) and install (Mac/Windows installers available).

## Step 2 — Prepare your gene list files

Inside `EVE_Workspace`, create a new folder named `custom_panel`:

```bash
cd ~/Desktop/EVE_Workspace
mkdir custom_panel
cd custom_panel
```

Download `generate_bed_new.py` from this repository into the `custom_panel/` folder.

Create two plain-text files listing your gene symbols, one per line:

- **`my_hypopara_genes.txt`** — your Tier 1 (core) panel
- **`my_endocrine_genes.txt`** — your Tier 2 (expansion) panel

Example contents:
```
GATA3
CASR
GCM2
AIRE
PTH
...
```

> [!WARNING]
> **TextEdit on Mac saves files in Rich Text format by default** — this will break the script. Before saving, go to **Format → Make Plain Text** (`⌘⇧T`), then save with a `.txt` extension. Alternatively use a code editor like VS Code or any plain-text editor.

## Step 3 — Generate the BED files

From inside the `custom_panel/` folder:

```bash
python3 generate_bed_new.py \
  --genes my_hypopara_genes.txt \
  --output my_hypopara_targets.bed

python3 generate_bed_new.py \
  --genes my_endocrine_genes.txt \
  --output my_endocrine_targets.bed
```

The script queries MyGene.info for each gene's exon coordinates, applies 50 bp padding around each exon, merges overlapping regions, and writes a sorted BED file. At the end you'll see a validation summary like:

```
=== BED Validation ===
Total regions:    482
Unique genes:     26
Total bp:         1,243,810 (1.24 Mb)
Avg per gene:     47,839 bp
Regions/gene avg: 18.5
✓  Average region size looks correct for exon-level BED.
```

If any genes failed (e.g. symbol typo or unrecognized alias), they are printed at the end so you can correct them.

## Step 4 — Run EVE with your custom panels

Go back to `EVE_Workspace`:

```bash
cd ~/Desktop/EVE_Workspace
```

Run EVE with two additional `-v` flags that replace the built-in BED files with your custom ones:

### 🍎 macOS / 🐧 Linux

```bash
docker run --rm -it \
  -v "$PWD/data:/data" \
  -v "$PWD/snpEff_db:/pipeline/snpEff/data" \
  -v "$PWD/custom_panel/my_hypopara_targets.bed:/pipeline/hypopara_targets.bed" \
  -v "$PWD/custom_panel/my_endocrine_targets.bed:/pipeline/endocrine_targets.bed" \
  hanyunseo01/eve:latest
```

### 🪟 Windows (PowerShell)

```powershell
docker run --rm -it `
  -v "${PWD}\data:/data" `
  -v "${PWD}\snpEff_db:/pipeline/snpEff/data" `
  -v "${PWD}\custom_panel\my_hypopara_targets.bed:/pipeline/hypopara_targets.bed" `
  -v "${PWD}\custom_panel\my_endocrine_targets.bed:/pipeline/endocrine_targets.bed" `
  hanyunseo01/eve:latest
```

**How this works:** The last two `-v` lines tell Docker to replace `/pipeline/hypopara_targets.bed` and `/pipeline/endocrine_targets.bed` inside the container with your files. The pipeline script reads from those exact paths, so it transparently uses your panel — the rest of the workflow is unchanged.

The resulting Excel report will have:
- **Sheet 1 (`Parathyroid_Panel`):** Variants restricted to your `my_hypopara_genes.txt`
- **Sheet 2 (`Endocrine_Panel`):** Variants restricted to your `my_endocrine_genes.txt`

---

## 📄 Output Files

After the analysis completes, check the `data/` folder for these key files:

| File Name | Description |
| :--- | :--- |
| **`*_Final_Report.xlsx`** | **The Final Report.** A comprehensive, dual-tiered Excel file organized into two separate sheets: **Sheet 1 (`Parathyroid_Panel`, Tier 1 genes)** and **Sheet 2 (`Endocrine_Panel`, Tier 2 genes)**. All variants are fully annotated with rsID, ClinVar, gnomAD AF, SIFT/PolyPhen, and Impact. |
| **`*_MultiQC_Report.html`** | **Quality Control.** Interactive graphs showing read quality, mapping rates, and duplicate levels. Open with any web browser. |
| **`*_coverage.mosdepth.summary.txt`** | **Depth Statistics.** Shows how well the target genes were covered (e.g., mean depth, % bases > 20x). |
| `*.bam` / `*.vcf` | Intermediate alignment and variant calling files for further manual inspection (e.g., in IGV). |

### 🩺 Inside the Clinical Report (.xlsx)

The **Clinical Report** is designed for immediate clinical interpretation. It aggregates data from **SnpEff**, **ClinVar**, **gnomAD**, and **dbSNP** into a single view.

| Column Category | Columns Included | Description |
| :--- | :--- | :--- |
| **Target Info** | `Gene`, `Transcript ID` | The gene symbol (e.g., *BRAF*) and the specific transcript used for annotation. |
| **Variant Identity** | `Variant ID (rsID)` | The dbSNP reference ID (e.g., *rs113488022*), crucial for cross-referencing with literature. |
| **Genomic Location** | `Chromosome`, `Position`, `Ref`, `Alt` | Exact genomic coordinates (GRCh38) and the specific base change. |
| **Mutation Detail** | `DNA Change`, `Protein Change` | HGVS notation describing the change at the DNA (c.) and Protein (p.) level. |
| **Clinical Significance** | `ClinVar`, `gnomAD AF` | **ClinVar:** Clinical interpretation (e.g., *Pathogenic, Benign*).<br>**gnomAD AF:** Global Allele Frequency to identify rare variants vs. common polymorphisms. |
| **Impact Prediction** | `Effect`, `Impact` | **Effect:** Type of mutation (e.g., *missense_variant*).<br>**Impact:** Predicted severity (*HIGH, MODERATE, LOW, MODIFIER*). |
| **In Silico Scores** | `SIFT`, `PolyPhen` | Computational predictions of how the variant affects protein function. |

> **💡 Tip for Clinicians:** Start by filtering the **`Impact`** column for **HIGH** or **MODERATE**, and check the **`ClinVar`** column for known pathogenic variants.

---

## 🛠️ Troubleshooting

If you encounter issues while running EVE, check the solutions below for common problems.

---

### ❌ Problem 1: Docker Desktop won't start / "Docker Desktop stopped"

**Possible causes:**
- WSL 2 is not enabled (Windows)
- Virtualization is disabled in BIOS (Windows)
- Insufficient disk space

**Solution (Windows):**
1. Open **Windows Features** (press Windows key, type `Turn Windows features on or off`).
2. Make sure these are **checked**:
   - **Virtual Machine Platform**
   - **Windows Subsystem for Linux**
3. Click OK and restart your computer.
4. Open PowerShell and run:
   ```powershell
   wsl --update
   wsl --set-default-version 2
   ```
5. Restart Docker Desktop.

**Solution (macOS):**
- Make sure you downloaded the correct version for your chip (Apple Silicon vs. Intel).
- Try uninstalling and reinstalling Docker Desktop.

---

### ❌ Problem 2: `no matching manifest for linux/arm64/v8` Error (Apple Silicon Mac)

**Problem:** When pulling the image, you see:
```
Error response from daemon: no matching manifest for linux/arm64/v8 in the manifest list entries
```

**Cause:** This happened with older single-architecture builds of the EVE image.

**Solution:** The current EVE image (`hanyunseo01/eve:latest` and `hanyunseo01/eve:v3.0`) is published as a multi-architecture image and supports Apple Silicon natively. If you still see this error, you may be using a very old cached version — clean it up and re-pull:
```bash
docker rmi hanyunseo01/eve:latest
docker pull hanyunseo01/eve:latest
```

As a temporary workaround you can force the amd64 image to run under emulation (slower):
```bash
docker pull --platform linux/amd64 hanyunseo01/eve:latest
docker run --platform linux/amd64 --rm -it \
  -v "$PWD/data:/data" \
  -v "$PWD/snpEff_db:/pipeline/snpEff/data" \
  hanyunseo01/eve:latest
```

---

### ❌ Problem 3: Terminal shows nothing / pipeline appears stuck after `docker run`

**Problem:** You ran `docker run ...` but the terminal stays blank with no output, even after a minute.

**Cause:** Docker's output is being buffered and not shown in real time because the `-it` flag was omitted.

**Solution:** Stop the run with `Ctrl + C` and re-run with the `-it` flag, exactly as shown in the "How to Run" section:
```bash
docker run --rm -it \
  -v "$PWD/data:/data" \
  -v "$PWD/snpEff_db:/pipeline/snpEff/data" \
  hanyunseo01/eve:latest
```

You should immediately see `>>> Starting EVE Pipeline ...` followed by `[INFO]` and `[SUCCESS]` messages.

---

### ❌ Problem 4: `permission denied` when running Docker

**Problem:** On macOS or Linux, you see an error like `permission denied while trying to connect to the Docker daemon socket`.

**Solution (macOS):**
- Make sure Docker Desktop is **running** (whale icon in menu bar).
- The first time you run the pipeline, macOS may prompt for permission to access the folder. Click **OK** / **Allow**.

**Solution (Linux):**
Add your user to the docker group:
```bash
sudo usermod -aG docker $USER
```
Then **log out and log back in** for the change to take effect.

---

### ❌ Problem 5: `is not a valid Windows path` Error

**Problem:** This usually happens when running the `docker run` command in **PowerShell** using CMD-style syntax (`%cd%`).

**Solution:**
- **If using PowerShell:** Use `${PWD}` instead of `%cd%`.
  - *Example:* `-v "${PWD}\data:/data"`
- **If using Command Prompt (CMD):** Keep using `%cd%`.

---

### ❌ Problem 6: `SnpEff database not found!` Error

**Problem:** The pipeline cannot find the `hg38` database files inside the container.

**Solution:**
- **Check Folder Name:** Verify that your folder is named **`snpEff_db`** (exact spelling, case-sensitive).
- **Match Docker Mount:** The mount path `-v .../snpEff_db:/pipeline/snpEff/data` must match your actual host folder name **exactly**.
- **Verify Structure:** Ensure the `hg38` folder is located directly inside `snpEff_db`, and that it contains the file `snpEffectPredictor.bin`.

---

### ❌ Problem 7: `No input FASTQ files found` Error

**Problem:** The pipeline script cannot detect your raw sequencing data.

**Solution:**
- **Check Naming Convention:** Files must end in `_1.fq.gz` and `_2.fq.gz` (not `_R1.fastq.gz`, not `.fq`, not `.fastq.gz`).
  - *Correct example:* `Patient01_1.fq.gz`, `Patient01_2.fq.gz`
- **Check Folder Location:** FASTQ files must be **directly inside** the `data/` folder, not in a subfolder.
- **Check Mounting:** Verify that `-v "$PWD/data:/data"` is correctly written.

---

### ❌ Problem 8: Reference data download fails or is corrupted

**Problem:** Google Drive download fails partway, or the unzipped files seem incomplete.

**Solution:**
- Google Drive sometimes throttles large folder downloads. Try downloading the `ref` and `snpEff_db` folders **one at a time**, not together.
- If a folder downloads as multiple `.zip` parts, you must unzip **all** of them.
- After unzipping, verify:
  - `data/ref/` contains `Homo_sapiens_assembly38.fasta` (and `.fai`, `.dict`, BWA index files like `.amb`, `.ann`, `.bwt`, `.pac`, `.sa`)
  - `snpEff_db/hg38/` contains `snpEffectPredictor.bin`
- If files are missing, re-download.

---

### ❌ Problem 9: Memory / RAM Crash (GATK Errors)

**Problem:** `GATK HaplotypeCaller` or `SnpEff` crashes with errors mentioning "Java heap space" or "OutOfMemoryError". This means Docker is not allocated enough RAM.

**Solution 1: Increase Docker Desktop memory**
1. Open **Docker Desktop** → click the **⚙️ Settings** icon (gear) in the top-right.
2. Go to **Resources** → **Advanced**.
3. Increase **Memory** to at least **16 GB** (8 GB is the absolute minimum).
4. Click **Apply & Restart**.

**Solution 2: WSL 2 Configuration (Windows, Advanced)**
If you are using Docker with the WSL 2 backend on Windows:
1. Press `Win + R`, type `%UserProfile%`, and press **Enter**.
2. Create or edit a file named `.wslconfig` (ensure it has no `.txt` extension).
3. Paste the following:
   ```ini
   [wsl2]
   memory=16GB    # Limits VM memory in WSL2
   processors=8   # Optional: limits number of CPU cores
   ```
4. Restart WSL by running `wsl --shutdown` in PowerShell, then restart Docker Desktop.

> [!TIP]
> **Recommended Allocation:** Set the WSL 2 memory to **50–75%** of your total system RAM to maintain overall system stability.

---

### ❌ Problem 10: Pipeline pauses or stops partway through

**Problem:** The pipeline runs for a while and then output stops, but no error appears.

**Possible causes:**
- Your computer went to sleep
- Docker Desktop was closed
- The terminal window was closed

**Solution:**
- See the [How to Run](#-how-to-run-eve) section for sleep-prevention settings.
- Re-run the same `docker run` command — the pipeline will **automatically skip** completed steps (it checks for output files at each step), so you only re-process the unfinished steps.

---

### ❌ Problem 11: Pipeline runs but the Excel report is empty or missing variants

**Problem:** The analysis completes, but the Clinical Report shows zero variants in one or both tiers.

**Solution:**
- Check the **MultiQC report** to verify the sequencing quality is acceptable (mapping rate >90%, duplication rate <30%).
- Check the **mosdepth coverage summary** — if mean depth is < 20×, your sample may be under-sequenced for confident variant calling.
- A genuinely empty Tier 1 sheet is biologically possible (the patient may have no variants in the 26 core parathyroid genes). The Tier 2 sheet (400 genes) should typically contain variants.
- **Custom panel users:** Double-check that your gene symbols are correct (HGNC official symbols), and look at the `Failed lookups` list printed by `generate_bed_new.py`.

---

### ❌ Problem 12: Docker says "no space left on device"

**Problem:** Your hard drive is full, or Docker's virtual disk is full.

**Solution:**
1. Free up space on your computer (target: at least 50 GB free).
2. Clean up old Docker images you no longer need:
   ```bash
   docker system prune -a
   ```
   ⚠️ This deletes **all** unused Docker images. After this you'll need to `docker pull hanyunseo01/eve:latest` again.

---

### ❌ Problem 13: DNS / network errors during image pull or build (WSL2 users)

**Problem:** You see errors like:
```
failed to resolve source metadata for docker.io/...
dial tcp: lookup registry-1.docker.io on 10.255.255.254:53: read udp ...: i/o timeout
```

**Cause:** WSL 2's auto-generated DNS server (`10.255.255.254`) sometimes fails to reach Docker Hub on certain networks.

**Solution:**
1. Inside WSL, edit `/etc/wsl.conf` (create it if missing):
   ```ini
   [network]
   generateResolvConf = false
   ```
2. Edit `/etc/resolv.conf` and replace its contents with:
   ```
   nameserver 8.8.8.8
   nameserver 8.8.4.4
   ```
3. In Windows PowerShell, run `wsl --shutdown`, then re-open WSL.
4. Verify: `curl -I https://registry-1.docker.io` should return HTTP headers (not a timeout).

---

### 💬 Still stuck?

If your problem is not listed here, please [open an issue on GitHub](https://github.com/) with:
- Your operating system and version
- The exact error message (screenshot is helpful)
- The command you used to run the pipeline

---

## 📜 Citation & Contact

If you use EVE in your research, please cite the following paper:

>

### ✉️ Contact

For technical support, bug reports, or collaboration inquiries, please contact:

* **Developer:** Yun-seo Han ([yunseo21c@korea.ac.kr](mailto:yunseo21c@korea.ac.kr))
* **Lab:** [H-Lee Lab](http://hleelab.korea.ac.kr), Department of Life Sciences, Korea University
