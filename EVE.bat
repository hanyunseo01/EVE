@echo off
title EVE (Endocrine Variant Extractor) - Diagnostic Mode
echo ========================================================
echo  [Diagnostic] Checking Your File Structure...
echo ========================================================
echo.

echo Current Folder: %cd%
echo Listing files in 'data' folder:
dir /b "data\*.fq*"
echo --------------------------------------------------------
echo.

if not exist "snpEff_db\hg38\snpEffectPredictor.bin" (
    echo [ERROR] 'snpEff_db' folder is missing or incomplete!
    pause
    exit
)

if not exist "data\ref\Homo_sapiens_assembly38.fasta" (
    echo [ERROR] Reference genome folder is missing inside 'data'!
    pause
    exit
)

if not exist "data\*.fq*" (
    echo [ERROR] No input FASTQ files found in 'data' folder!
    echo Current files in 'data':
    dir /b "data"
    echo.
    echo Please make sure your files have 'fq' in their names.
    pause
    exit
)

echo [INFO] Files found! Starting analysis...
echo.

docker pull hanyunseo01/eve:v2.0

docker run --rm ^
  -v "%cd%\data:/data" ^
  -v "%cd%\snpEff_db:/pipeline/snpEff/data" ^
  hanyunseo01/eve:v2.0

pause
