@echo off
title EVE (Endocrine Variant Extractor) - Clinical Pipeline
echo ========================================================
echo  [H-Lee Lab] EVE: Endocrine Variant Extractor
echo  Version: 2.0 (Clinical-Grade WES Pipeline)
echo ========================================================
echo.

:: 1. Check for required database and reference files
if not exist "snpEff_db\hg38\snpEffectPredictor.bin" (
    echo [ERROR] 'snpEff_db' folder is missing or incomplete!
    echo Please ensure 'snpEff_db\hg38\snpEffectPredictor.bin' exists.
    pause
    exit
)

:: Verify reference genome exists within the nested data/ref structure
if not exist "data\ref\Homo_sapiens_assembly38.fasta" (
    echo [ERROR] Reference genome files are missing!
    echo Please ensure 'data\ref\Homo_sapiens_assembly38.fasta' exists.
    pause
    exit
)

:: 2. Check for FASTQ files and verify .fq.gz extension
if not exist "data\*.fq.gz" (
    echo [ERROR] No input FASTQ files found in 'data' folder!
    echo.
    echo [IMPORTANT] Files MUST end exactly with '.fq.gz'
    echo (Example: sample_1.fq.gz, sample_2.fq.gz)
    echo (.fastq.gz or .fq extensions will NOT be recognized)
    echo.
    pause
    exit
)

:: 3. Pull/Update the latest Docker image (v2.0)
echo [INFO] Checking for the latest Docker image (v2.0)...
docker pull hanyunseo01/eve:v2.0
if %errorlevel% neq 0 (
    echo [WARNING] Failed to update image. Attempting to run with the local version...
)
echo.

echo [INFO] All requirements met. Starting analysis...
echo [INFO] This process may take several hours. Do not close this window.
echo.

:: 4. Execute the pipeline
:: The -v "%cd%\data:/data" command mounts both raw sequences and the nested 'ref/' folder.
docker run --rm ^
  -v "%cd%\data:/data" ^
  -v "%cd%\snpEff_db:/pipeline/snpEff/data" ^
  hanyunseo01/eve:v2.0

:: 5. Final status check and reporting
echo.
if %errorlevel% neq 0 (
    echo [ERROR] Analysis failed.
    echo Please check the following:
    echo 1. Is Docker Desktop running?
    echo 2. Is allocated RAM sufficient (Min 16GB recommended)?
    echo 3. Do you have enough disk space?
) else (
    echo [SUCCESS] Analysis complete!
    echo --------------------------------------------------------
    echo Please check the 'data' folder for results:
    echo - Clinical Report: *.xlsx
    echo - Quality Report: *.html (MultiQC)
    echo --------------------------------------------------------
)

pause