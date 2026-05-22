import requests
import argparse
import sys
import time
from pathlib import Path

PADDING = 50  # bp — covers splice sites, per Reviewer 2 suggestion


def fetch_exons_for_gene(gene_symbol, retries=3):
    """Fetch exon coordinates for a single gene from MyGene.info."""
    url = "https://mygene.info/v3/query"

    for attempt in range(retries):
        try:
            r = requests.get(
                url,
                params={
                    'q': gene_symbol,
                    'scopes': 'symbol',
                    'fields': 'symbol,exons',
                    'species': 'human',
                    'size': 5
                },
                timeout=15
            )
            r.raise_for_status()
            data = r.json()
            break
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2)
                continue
            print(f"[ERROR] API failed for {gene_symbol}: {e}", file=sys.stderr)
            return None

    hits = data.get('hits', [])
    if not hits:
        return None

    # Find best hit — must match symbol exactly and have exons
    best_hit = None
    for hit in hits:
        if hit.get('symbol', '').upper() != gene_symbol.upper():
            continue
        if 'exons' in hit and hit['exons']:
            best_hit = hit
            break

    if not best_hit:
        return None

    # Select best transcript and get its exons
    exons_data = best_hit.get('exons', [])
    if not exons_data:
        return None
    if not isinstance(exons_data, list):
        exons_data = [exons_data]

    transcript = select_best_transcript(exons_data)
    if not transcript:
        return None

    # Get chromosome from the transcript (not from genomic_pos_hg38)
    chr_raw = transcript.get('chr')
    if not chr_raw:
        return None
    chrom = f"chr{chr_raw}" if not str(chr_raw).startswith('chr') else str(chr_raw)

    positions = transcript.get('position', [])
    if not positions:
        return None

    # Convert 1-based inclusive (MyGene format) -> 0-based half-open (BED standard)
    exon_lines = []
    for pos in positions:
        if len(pos) >= 2:
            start = pos[0] - 1
            end = pos[1]
            exon_lines.append((chrom, start, end, gene_symbol))

    return exon_lines


def select_best_transcript(exons_data):
    """RefSeq NM_ preferred, longest as fallback.
    Strongly prefers transcripts on primary chromosomes (chr1-22, X, Y)
    over those on alt contigs (e.g., chr1_KQ458384v1_alt)."""
    # Primary chromosomes only — no underscores in name
    PRIMARY_CHROMS = set(
        [str(i) for i in range(1, 23)] + ['X', 'Y', 'MT', 'M']
    )

    def is_primary(t):
        c = str(t.get('chr', ''))
        return c in PRIMARY_CHROMS

    # Filter to primary chromosomes if any exist
    primary_transcripts = [t for t in exons_data if is_primary(t)]
    pool = primary_transcripts if primary_transcripts else exons_data

    # Within pool: RefSeq NM_ preferred
    nm_transcripts = [t for t in pool
                      if t.get('transcript', '').startswith('NM_')]
    if nm_transcripts:
        return max(nm_transcripts, key=lambda t: len(t.get('position', [])))
    return max(pool, key=lambda t: len(t.get('position', [])))


def merge_overlapping(lines):
    """Merge overlapping/adjacent exons within same gene."""
    if not lines:
        return []
    sorted_lines = sorted(lines, key=lambda x: (x[0], x[1]))
    merged = [sorted_lines[0]]
    for line in sorted_lines[1:]:
        lc, ls, le, lg = merged[-1]
        c, s, e, g = line
        if c == lc and g == lg and s <= le:
            merged[-1] = (c, ls, max(le, e), g)
        else:
            merged.append(line)
    return merged


def apply_padding(lines, padding):
    """Add padding around each exon for splice site coverage."""
    return [(c, max(0, s - padding), e + padding, g) for c, s, e, g in lines]


def deduplicate(lines):
    """Remove exact duplicate regions (same chrom/start/end)."""
    seen = set()
    unique = []
    for c, s, e, g in lines:
        key = (c, s, e)
        if key not in seen:
            seen.add(key)
            unique.append((c, s, e, g))
    return unique


def validate_bed(lines, gene_count):
    """Sanity check: warn if output looks gene-level instead of exon-level."""
    if not lines:
        print("[WARN] No regions generated!")
        return
    total_bp = sum(e - s for _, s, e, _ in lines)
    avg_per_gene = total_bp / max(gene_count, 1)

    print(f"\n=== BED Validation ===")
    print(f"Total regions:    {len(lines)}")
    print(f"Unique genes:     {gene_count}")
    print(f"Total bp:         {total_bp:,} ({total_bp/1e6:.2f} Mb)")
    print(f"Avg per gene:     {avg_per_gene:,.0f} bp")
    print(f"Regions/gene avg: {len(lines)/max(gene_count,1):.1f}")

    if avg_per_gene > 10000:
        print(f"⚠️  WARNING: avg >10kb/gene suggests gene-level regions!")
        print(f"   Expected exon-level: 1,000-5,000 bp per gene.")
    elif avg_per_gene < 200:
        print(f"⚠️  WARNING: avg <200bp/gene seems too small.")
    else:
        print(f"✓  Average region size looks correct for exon-level BED.")


def generate_bed(gene_list, output_file):
    print(f"[INFO] Fetching exon coordinates for {len(gene_list)} genes (GRCh38)...")
    print(f"[INFO] Padding: ±{PADDING} bp around each exon")
    print(f"[INFO] Transcript preference: RefSeq NM_ > longest\n")

    all_lines = []
    failed = []

    for i, gene in enumerate(gene_list, 1):
        if i % 25 == 0:
            print(f"  [{i}/{len(gene_list)}] processed...")

        exons = fetch_exons_for_gene(gene)
        if exons is None or len(exons) == 0:
            failed.append(gene)
            continue

        exons = merge_overlapping(exons)
        exons = apply_padding(exons, PADDING)
        all_lines.extend(exons)
        time.sleep(0.1)  # gentle rate limiting

    # Final cleanup
    all_lines = deduplicate(all_lines)
    all_lines.sort(key=lambda x: (x[0], x[1]))

    # Write BED file
    with open(output_file, 'w') as f:
        for c, s, e, g in all_lines:
            f.write(f"{c}\t{s}\t{e}\t{g}\n")

    successful_genes = set(g for _, _, _, g in all_lines)

    print(f"\n[SUCCESS] Wrote {len(all_lines)} regions to {output_file}")
    print(f"          Covering {len(successful_genes)} / {len(gene_list)} genes")

    if failed:
        print(f"\n⚠️  Failed lookups ({len(failed)}):")
        print(f"   {failed}")
        print(f"   These genes need manual coordinate lookup or symbol correction.")

    validate_bed(all_lines, len(successful_genes))


def main():
    parser = argparse.ArgumentParser(description="Generate exon-level BED for EVE")
    parser.add_argument('--genes', required=True, help='Text file: one gene symbol per line')
    parser.add_argument('--output', required=True, help='Output BED file path')
    args = parser.parse_args()

    gene_list = [g.strip() for g in Path(args.genes).read_text().splitlines()
                 if g.strip() and not g.startswith('#')]

    if not gene_list:
        print("[ERROR] No genes found in input file.")
        sys.exit(1)

    generate_bed(gene_list, args.output)


if __name__ == "__main__":
    main()
