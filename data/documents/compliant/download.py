"""
Download Clinical Trial Protocol PDFs from ctg-studies.json.

Usage:
    python download.py                  # download all protocols
    python download.py --limit 10       # download first 10
    python download.py --output ./pdfs  # custom output directory
"""

import json
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: 'requests' library is required. Install it with: pip install requests")
    sys.exit(1)

# Paths
SCRIPT_DIR = Path(__file__).resolve().parent
STUDIES_JSON = SCRIPT_DIR / "ctg-studies.json"
DEFAULT_OUTPUT = SCRIPT_DIR / "protocols"
BASE_PDF_URL = "https://cdn.clinicaltrials.gov/large-docs"


def load_studies():
    """Load study records from ctg-studies.json."""
    if not STUDIES_JSON.exists():
        print(f"Error: {STUDIES_JSON} not found.")
        sys.exit(1)

    with open(STUDIES_JSON, "r") as f:
        data = json.load(f)

    # Handle list or dict with 'studies' key
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "studies" in data:
        return data["studies"]
    return []


def get_pdf_info(study):
    """
    Extract NCT ID and PDF filename from a study record.
    Returns (nct_id, filename) or (None, None) if no protocol PDF is available.
    """
    try:
        nct_id = study["protocolSection"]["identificationModule"]["nctId"]
    except (KeyError, TypeError):
        return None, None

    try:
        large_docs = study["documentSection"]["largeDocumentModule"]["largeDocs"]
        for doc in large_docs:
            if doc.get("hasProtocol", False):
                return nct_id, doc["filename"]
    except (KeyError, TypeError):
        pass

    return nct_id, None


def build_pdf_url(nct_id, filename):
    """Build the CDN download URL for a protocol PDF."""
    last_two = nct_id[-2:]
    return f"{BASE_PDF_URL}/{last_two}/{nct_id}/{filename}"


def download_pdf(url, output_path, timeout=30):
    """Download a PDF file. Returns True on success."""
    try:
        response = requests.get(url, timeout=timeout, stream=True)
        if response.status_code == 200:
            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        return False
    except requests.RequestException:
        return False


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Download clinical trial protocol PDFs from ctg-studies.json"
    )
    parser.add_argument(
        "--output", "-o",
        default=str(DEFAULT_OUTPUT),
        help=f"Output directory for downloaded PDFs (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=None,
        help="Maximum number of PDFs to download",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.5,
        help="Delay in seconds between downloads (default: 0.5)",
    )
    args = parser.parse_args()

    # Load studies
    studies = load_studies()
    print(f"Loaded {len(studies)} studies from {STUDIES_JSON.name}")

    if not studies:
        print("No studies found.")
        sys.exit(1)

    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Download
    downloaded = 0
    skipped = 0
    failed = 0
    limit = args.limit or len(studies)

    print(f"\nDownloading protocol PDFs to: {output_dir.resolve()}\n")
    print(f"{'NCT ID':<18} {'Status':<12} {'Details'}")
    print("-" * 70)

    for study in studies:
        if downloaded >= limit:
            break

        nct_id, filename = get_pdf_info(study)

        if not nct_id or not filename:
            skipped += 1
            if nct_id:
                print(f"{nct_id:<18} {'SKIP':<12} No protocol PDF available")
            continue

        output_path = output_dir / f"{nct_id}_{filename}"
        if output_path.exists():
            print(f"{nct_id:<18} {'EXISTS':<12} {output_path.name}")
            downloaded += 1
            continue

        url = build_pdf_url(nct_id, filename)
        success = download_pdf(url, output_path)

        if success:
            size_mb = output_path.stat().st_size / (1024 * 1024)
            print(f"{nct_id:<18} {'OK':<12} {output_path.name} ({size_mb:.1f} MB)")
            downloaded += 1
        else:
            print(f"{nct_id:<18} {'FAIL':<12} {url}")
            failed += 1

        time.sleep(args.delay)

    print("-" * 70)
    print(f"\nDone. Downloaded: {downloaded} | Skipped: {skipped} | Failed: {failed}")
    print(f"Output directory: {output_dir.resolve()}")


if __name__ == "__main__":
    main()