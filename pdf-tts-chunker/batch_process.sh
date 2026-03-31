#!/usr/bin/env bash
# Batch-process all PDFs in a directory.
# Usage: ./batch_process.sh [pdf_dir] [output_dir] [extra options]
#
# Examples:
#   ./batch_process.sh ./pdfs ./output
#   ./batch_process.sh ./pdfs ./output --force-ocr --remove-nonsense -c 800,1600,3200
#   ./batch_process.sh ./pdfs ./output --dpi 400 -v 100

PDF_DIR="${1:-.}"
OUTPUT_DIR="${2:-./output}"
shift 2 2>/dev/null || true   # any remaining args are forwarded to the python script

PDF_FILES=( "$PDF_DIR"/*.pdf "$PDF_DIR"/*.PDF )
FOUND=()
for f in "${PDF_FILES[@]}"; do
    [[ -f "$f" ]] && FOUND+=("$f")
done

if [[ ${#FOUND[@]} -eq 0 ]]; then
    echo "No PDF files found in: $PDF_DIR"
    exit 1
fi

echo "Found ${#FOUND[@]} PDF(s) in $PDF_DIR"
echo "Output directory: $OUTPUT_DIR"
echo "---"

python3 "$(dirname "$0")/pdf_ocr_chunker.py" \
    --output-dir "$OUTPUT_DIR" \
    "$@" \
    "${FOUND[@]}"
