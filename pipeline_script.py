import os
import subprocess
import sys
import glob
import pandas as pd
import myvariant

# ========================================================
# [Config] EVE Pipeline (Parathyroid & Endocrine)
# ========================================================

DATA_DIR = "/data"
REF_DIR = "/data/ref"
REF_FILE = os.path.join(REF_DIR, "Homo_sapiens_assembly38.fasta")

# BED files must be located in the host's pipeline folder and mounted into the container.
# To use custom panels, override these paths using Docker -v mount options (see README).
BED_PARATHYROID = "/pipeline/hypopara_targets.bed"   # Sheet 1: Core Parathyroid Panel
BED_ENDOCRINE = "/pipeline/endocrine_targets.bed"    # Sheet 2: Endocrine Expansion Panel

# Temporary merged BED file combining both panels for variant calling
BED_COMBINED = "/pipeline/combined_targets.bed"

SNPEFF_JAR = "/pipeline/snpEff/snpEff.jar"
SNPEFF_DB_DIR = "/pipeline/snpEff/data/hg38"
THREADS = "4"

def run_command(cmd, step_name, output_check=None):
    print(f"\n[INFO] Checking Step: {step_name}")
    if output_check and os.path.exists(output_check):
        if os.path.getsize(output_check) > 0:
            print(f"[SKIP] File '{output_check}' already exists. Skipping.")
            return
        else:
            print(f"[WARN] File exists but is empty. Re-running.")

    print(f"Command: {cmd}")
    try:
        subprocess.check_call(cmd, shell=True)
        print(f"[SUCCESS] {step_name} completed.")
    except subprocess.CalledProcessError:
        print(f"[ERROR] {step_name} failed.")
        sys.exit(1)

def combine_bed_files(bed1, bed2, output_bed):
    print(f"[INFO] Merging BED files into {output_bed}...")
    try:
        with open(output_bed, 'w') as outfile:
            for fname in [bed1, bed2]:
                if os.path.exists(fname):
                    with open(fname) as infile:
                        outfile.write(infile.read())
                        outfile.write("\n") # Ensure newline at end of each file
                else:
                    print(f"[ERROR] BED file missing: {fname}")
                    sys.exit(1)
        print(f"[SUCCESS] Merged BED created.")
    except Exception as e:
        print(f"[ERROR] Failed to merge BED files: {e}")
        sys.exit(1)

def get_gene_list_from_bed(bed_path):
    genes = set()
    if not os.path.exists(bed_path):
        return genes

    try:
        with open(bed_path, 'r') as f:
            for line in f:
                if line.startswith("#") or not line.strip(): continue
                parts = line.strip().split('\t')
                if len(parts) >= 4:
                    genes.add(parts[3].strip())
    except Exception as e:
        print(f"[ERROR] Failed to read gene names from BED: {e}")

    return genes

def get_myvariant_info(chrom, pos, ref, alt, mv):
    hgvs_id = f"{chrom}:g.{pos}{ref}>{alt}"
    clinvar_sig = "Not Found"
    sift_pred = "-"
    polyphen_pred = "-"
    gnomad_af = "-"
    rsid = "-"

    try:
        res = mv.getvariant(hgvs_id, assembly='hg38', fields='clinvar,dbnsfp,gnomad_genome,dbsnp')
        if res:
            if 'clinvar' in res and 'rcv' in res['clinvar']:
                rcv = res['clinvar']['rcv']
                if isinstance(rcv, list):
                    clinvar_sig = rcv[0].get('clinical_significance', 'Check ClinVar')
                else:
                    clinvar_sig = rcv.get('clinical_significance', 'Check ClinVar')

            if 'dbnsfp' in res:
                if 'sift' in res['dbnsfp'] and 'pred' in res['dbnsfp']['sift']:
                    sift_pred = res['dbnsfp']['sift']['pred']
                if 'polyphen2' in res['dbnsfp']:
                    pp2 = res['dbnsfp']['polyphen2']
                    if isinstance(pp2, dict) and 'hvar' in pp2:
                        hvar = pp2['hvar']
                        if isinstance(hvar, dict) and 'pred' in hvar:polyphen_pred = hvar['pred']

            if 'gnomad_genome' in res and 'af' in res['gnomad_genome']:
                if 'af' in res['gnomad_genome']['af']:
                    gnomad_af = res['gnomad_genome']['af']['af']

            if 'dbsnp' in res and 'rsid' in res['dbsnp']:
                rsid = res['dbsnp']['rsid']
    except:
        pass

    return clinvar_sig, sift_pred, polyphen_pred, gnomad_af, rsid

def generate_tiered_report(snpeff_vcf, excel_file):
    print(f"\n[INFO] Generating Report: Parathyroid vs Endocrine...")

    # Load gene lists from each BED panel
    genes_parathyroid = get_gene_list_from_bed(BED_PARATHYROID)
    genes_endocrine = get_gene_list_from_bed(BED_ENDOCRINE)

    print(f" -> Loaded {len(genes_parathyroid)} genes for Sheet 1 (Parathyroid)")
    print(f" -> Loaded {len(genes_endocrine)} genes for Sheet 2 (Endocrine)")

    mv = myvariant.MyVariantInfo()
    records = []

    try:
        with open(snpeff_vcf, 'r') as f:
            for line in f:
                if line.startswith("#"): continue
                parts = line.strip().split('\t')
                if len(parts) >= 8:
                    chrom, pos, ref, alt, info = parts[0], parts[1], parts[3], parts[4], parts[7]

                    gene_name = "Unknown"
                    effect = "-"
                    impact = "-"
                    transcript_id = "-"
                    dna_change = "-"
                    protein_change = "-"

                    ann_start = info.find("ANN=")
                    if ann_start != -1:
                        ann_str = info[ann_start+4:].split(';')[0]
                        first_ann = ann_str.split(',')[0]
                        fields = first_ann.split('|')

                        if len(fields) > 1: effect = fields[1]
                        if len(fields) > 2: impact = fields[2]
                        if len(fields) > 3: gene_name = fields[3]
                        if len(fields) > 6: transcript_id = fields[6]
                        if len(fields) > 9: dna_change = fields[9]
                        if len(fields) > 10: protein_change = fields[10]

                    clinvar, sift, polyphen, gnomad, rsid = get_myvariant_info(chrom, pos, ref, alt, mv)

                    records.append({
                        "Gene": gene_name,
                        "Variant ID": rsid,
                        "Chromosome": chrom, "Position": pos, "Ref": ref, "Alt": alt,
                        "Effect": effect,
                        "Impact": impact,
                        "DNA Change": dna_change, "Protein Change": protein_change,
                        "ClinVar": clinvar, "gnomAD AF": gnomad,
                        "SIFT": sift, "PolyPhen": polyphen,
                        "Transcript ID": transcript_id
                    })

        # Build full variant dataframe
        df_full = pd.DataFrame(records)
        cols = ["Gene", "Variant ID", "DNA Change", "Protein Change", "ClinVar", "gnomAD AF", "Effect", "Impact", "SIFT", "PolyPhen", "Chromosome", "Position"]

        if not df_full.empty:
            final_cols = [c for c in cols if c in df_full.columns] + [c for c in df_full.columns if c not in cols]
            df_full = df_full[final_cols]

            # Split variants into two sheets based on panel membership
            # Sheet 1: Core Parathyroid Panel (hypopara_targets.bed)
            df_parathyroid = df_full[df_full['Gene'].isin(genes_parathyroid)]

            # Sheet 2: Endocrine Expansion Panel (endocrine_targets.bed)
            df_endocrine = df_full[df_full['Gene'].isin(genes_endocrine)]

            # Save to Excel
            with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                df_parathyroid.to_excel(writer, sheet_name='Parathyroid_Panel', index=False)
                df_endocrine.to_excel(writer, sheet_name='Endocrine_Panel', index=False)

            print(f"[SUCCESS] Report Saved: {excel_file}")
            print(f" -> Sheet 'Parathyroid_Panel': {len(df_parathyroid)} variants")
            print(f" -> Sheet 'Endocrine_Panel': {len(df_endocrine)} variants")

        else:
            print("[WARN] No variants found in VCF.")

    except Exception as e:
        print(f"[ERROR] Failed to create Excel: {e}")

def main():
    print(">>> Starting EVE Pipeline (Parathyroid & Endocrine Mode) <<<")

    # Verify BED files exist inside the container
    if not os.path.exists(BED_PARATHYROID) or not os.path.exists(BED_ENDOCRINE):
        print(f"[ERROR] BED files missing inside container.")
        print(f"Checking: {BED_PARATHYROID}")
        print(f"Checking: {BED_ENDOCRINE}")
        sys.exit(1)

    # Merge both BED panels into a single combined file for variant calling
    combine_bed_files(BED_PARATHYROID, BED_ENDOCRINE, BED_COMBINED)

    # All downstream steps use the combined BED
    TARGETS_BED = BED_COMBINED

    # Detect input FASTQ files (must follow naming convention: *_1.fq.gz / *_2.fq.gz)
    r1_files = glob.glob(os.path.join(DATA_DIR, "*_1.fq.gz"))
    if not r1_files:
        print("[ERROR] No input FASTQ files found in /data.")
        sys.exit(1)
    r1 = r1_files[0]
    r2 = r1.replace("_1.fq.gz", "_2.fq.gz")
    base_name = os.path.basename(r1).split("_")[0]

    # Define output file paths
    trimmed_r1_paired = os.path.join(DATA_DIR, f"{base_name}_R1_paired.fq.gz")
    trimmed_r1_unpaired = os.path.join(DATA_DIR, f"{base_name}_R1_unpaired.fq.gz")
    trimmed_r2_paired = os.path.join(DATA_DIR, f"{base_name}_R2_paired.fq.gz")
    trimmed_r2_unpaired = os.path.join(DATA_DIR, f"{base_name}_R2_unpaired.fq.gz")

    bam_file = os.path.join(DATA_DIR, f"{base_name}.bam")
    sorted_bam = os.path.join(DATA_DIR, f"{base_name}.sorted.bam")
    dedup_bam = os.path.join(DATA_DIR, f"{base_name}.dedup.bam")
    metrics_file = os.path.join(DATA_DIR, f"{base_name}.metrics.txt")
    raw_vcf = os.path.join(DATA_DIR, f"{base_name}.raw.vcf.gz")
    snpeff_vcf = os.path.join(DATA_DIR, f"{base_name}.snpeff.vcf")
    excel_report = os.path.join(DATA_DIR, f"{base_name}_Final_Report.xlsx")

    # --- Pipeline Execution ---
    run_command(f"fastqc {r1} {r2} -o {DATA_DIR} -t {THREADS} --quiet", "Step 0-1: FastQC (raw reads)", os.path.join(DATA_DIR, f"{base_name}_1_fastqc.html"))
    run_command(f"java -jar /usr/share/java/trimmomatic.jar PE -threads {THREADS} {r1} {r2} {trimmed_r1_paired} {trimmed_r1_unpaired} {trimmed_r2_paired} {trimmed_r2_unpaired} ILLUMINACLIP:/usr/share/trimmomatic/adapters/TruSeq3-PE.fa:2:30:10 LEADING:3 TRAILING:3 SLIDINGWINDOW:4:15 MINLEN:36", "Step 0: Trimming", trimmed_r1_paired)
    run_command(f"fastqc {trimmed_r1_paired} {trimmed_r2_paired} -o {DATA_DIR} -t {THREADS} --quiet", "Step 0-3: FastQC (trimmed reads)", os.path.join(DATA_DIR, f"{base_name}_R1_paired_fastqc.html"))
    run_command(f"bwa mem -t {THREADS} -R '@RG\\tID:{base_name}\\tSM:{base_name}\\tPL:ILLUMINA' {REF_FILE} {trimmed_r1_paired} {trimmed_r2_paired} | samtools view -bS - > {bam_file}", "Step 1: Alignment", bam_file)
    run_command(f"samtools sort -o {sorted_bam} {bam_file}", "Step 2: Sorting", sorted_bam)
    run_command(f"samtools index {sorted_bam}", "Step 2-1: Indexing", f"{sorted_bam}.bai")
    run_command(f"gatk MarkDuplicates -I {sorted_bam} -O {dedup_bam} -M {metrics_file}", "Step 3: MarkDuplicates", dedup_bam)
    run_command(f"samtools index {dedup_bam}", "Step 3-1: Dedup Indexing", f"{dedup_bam}.bai")

    # Coverage analysis over combined target regions
    print("\n[INFO] Running Mosdepth (Combined Targets)...")
    mosdepth_prefix = os.path.join(DATA_DIR, f"{base_name}_coverage")
    run_command(f"mosdepth --by {TARGETS_BED} --thresholds 1,10,20,30,50,100 --threads {THREADS} {mosdepth_prefix} {dedup_bam}", "Step 3-2: Mosdepth Coverage", f"{mosdepth_prefix}.mosdepth.summary.txt")

    # Variant calling restricted to combined target intervals
    run_command(f"gatk HaplotypeCaller -R {REF_FILE} -I {dedup_bam} -O {raw_vcf} -L {TARGETS_BED}", "Step 4: Variant Calling", raw_vcf)

    # SnpEff functional annotation
    print("\n[INFO] Checking SnpEff Database...")
    if not os.path.exists(os.path.join(SNPEFF_DB_DIR, "snpEffectPredictor.bin")):
        print("[CRITICAL ERROR] SnpEff database not found!")
        sys.exit(1)

    if os.path.exists(raw_vcf):
        cmd_snpeff = f"java -Xmx4g -jar {SNPEFF_JAR} -canon hg38 {raw_vcf} > {snpeff_vcf}"
        run_command(cmd_snpeff, "Step 5: SnpEff Annotation", snpeff_vcf)

    # Generate tiered clinical Excel report
    if os.path.exists(snpeff_vcf):
        generate_tiered_report(snpeff_vcf, excel_report)

    # Aggregate QC metrics into MultiQC report
    print("\n[INFO] Generating MultiQC Quality Report...")
    run_command(f"multiqc {DATA_DIR} -o {DATA_DIR} -n {base_name}_MultiQC_Report.html --force", "Step 6: MultiQC", f"{DATA_DIR}/{base_name}_MultiQC_Report.html")

    print("\n[INFO] Pipeline Completed Successfully!")

if __name__ == "__main__":
    main()
