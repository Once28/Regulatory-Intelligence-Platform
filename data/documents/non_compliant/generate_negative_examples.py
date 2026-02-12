"""
Generate negative examples (non-compliant versions) from compliant protocols.

This script creates fake/negative examples by redacting crucial information
from compliant protocol PDFs, making them non-compliant for testing purposes.

Usage:
    python generate_negative_examples.py                    # process all protocols
    python generate_negative_examples.py --limit 5          # process first 5
    python generate_negative_examples.py --input ../compliant/protocols --output ./protocols
"""

import sys
import re
import argparse
from pathlib import Path
from typing import List

try:
    import fitz  # PyMuPDF
except ImportError:
    print("Error: 'PyMuPDF' is required. Install it with: pip install pymupdf")
    sys.exit(1)


# Patterns to identify crucial information that should be redacted
CRUCIAL_PATTERNS = [
    # Protocol identifiers
    (r'\bNCT\d{8}\b', 'PROTOCOL_ID'),  # NCT IDs
    (r'\bProtocol\s+(?:Number|ID|Version)[:\s]+([A-Z0-9\-]+)', 'PROTOCOL_ID'),
    (r'\bVersion\s+(\d+\.?\d*)\b', 'VERSION'),
    
    # Dates (various formats)
    (r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', 'DATE'),  # MM/DD/YYYY or DD/MM/YYYY
    (r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b', 'DATE'),
    (r'\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b', 'DATE'),  # YYYY-MM-DD
    
    # Signatures and signatories
    (r'\b(?:Signature|Signed|Signatory)[:\s]+([A-Z][a-z]+\s+[A-Z][a-z]+)', 'SIGNATURE'),
    (r'\b(?:Principal\s+)?Investigator[:\s]+([A-Z][a-z]+\s+[A-Z][a-z]+)', 'INVESTIGATOR'),
    (r'\b(?:Dr\.|Dr|MD|PhD|Ph\.D\.)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)', 'INVESTIGATOR'),
    
    # Email addresses
    (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'EMAIL'),
    
    # Phone numbers
    (r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', 'PHONE'),
    (r'\b\(\d{3}\)\s*\d{3}[-.]?\d{4}\b', 'PHONE'),
    
    # Institutional identifiers
    (r'\bIRB\s+(?:Number|ID|#)[:\s]+([A-Z0-9\-]+)', 'IRB_ID'),
    (r'\bInstitutional\s+Review\s+Board[:\s]+([A-Z0-9\-]+)', 'IRB_ID'),
    
    # Version and amendment numbers
    (r'\bAmendment\s+(\d+)\b', 'AMENDMENT'),
    (r'\bProtocol\s+Amendment\s+(\d+)\b', 'AMENDMENT'),
    
    # Approval dates
    (r'\b(?:Approved|Approval)\s+Date[:\s]+([\d/]+)', 'APPROVAL_DATE'),
    (r'\bDate\s+of\s+Approval[:\s]+([\d/]+)', 'APPROVAL_DATE'),
]


def redact_text_in_pdf(pdf_path: Path, output_path: Path, redaction_types: List[str] = None) -> dict:
    """
    Redact crucial information from a PDF and save as a new non-compliant version.
    
    Args:
        pdf_path: Path to source compliant PDF
        output_path: Path to save redacted PDF
        redaction_types: List of redaction types to apply (None = all)
    
    Returns:
        Dictionary with redaction statistics
    """
    doc = fitz.open(pdf_path)
    total_redactions = 0
    redaction_counts = {}
    
    # If no specific types specified, use all patterns
    patterns_to_use = CRUCIAL_PATTERNS
    if redaction_types:
        patterns_to_use = [p for p in CRUCIAL_PATTERNS if p[1] in redaction_types]
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        page_redactions = 0
        
        # Get page text for pattern matching
        page_text = page.get_text("text")
        
        # Try to find and redact text using text search
        for pattern_str, redaction_type in patterns_to_use:
            try:
                # Find all matches in the page text
                matches = list(re.finditer(pattern_str, page_text, re.IGNORECASE))
                
                for match in matches:
                    matched_text = match.group()
                    
                    # Use PyMuPDF's search_for to find exact text locations
                    # This returns rectangles where the text appears
                    text_instances = page.search_for(matched_text, flags=fitz.TEXT_DEHYPHENATE)
                    
                    for rect in text_instances:
                        # Add small padding around the text for better visual redaction
                        rect.x0 -= 1
                        rect.y0 -= 1
                        rect.x1 += 1
                        rect.y1 += 1
                        
                        # Add redaction annotation (black fill)
                        page.add_redact_annot(rect, fill=(0, 0, 0))
                        page_redactions += 1
                        
                        # Track by type
                        if redaction_type not in redaction_counts:
                            redaction_counts[redaction_type] = 0
                        redaction_counts[redaction_type] += 1
                        
                        # Limit redactions per pattern to avoid over-redaction
                        if redaction_counts[redaction_type] >= 50:
                            break
                            
            except Exception as e:
                # Skip patterns that cause errors (e.g., invalid regex)
                continue
        
        # Apply all redactions to the page
        if page_redactions > 0:
            page.apply_redactions()
            total_redactions += page_redactions
    
    # Get page count before closing
    page_count = len(doc)
    
    # Save the redacted PDF
    doc.save(output_path)
    doc.close()
    
    return {
        "total_redactions": total_redactions,
        "by_type": redaction_counts,
        "pages": page_count,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Generate non-compliant protocol versions by redacting crucial information"
    )
    parser.add_argument(
        "--input", "-i",
        default="../compliant/protocols",
        help="Input directory containing compliant protocol PDFs (default: ../compliant/protocols)",
    )
    parser.add_argument(
        "--output", "-o",
        default="./protocols",
        help="Output directory for non-compliant PDFs (default: ./protocols)",
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=None,
        help="Maximum number of PDFs to process",
    )
    parser.add_argument(
        "--types",
        nargs="+",
        choices=["PROTOCOL_ID", "VERSION", "DATE", "SIGNATURE", "INVESTIGATOR", 
                 "EMAIL", "PHONE", "IRB_ID", "AMENDMENT", "APPROVAL_DATE"],
        default=None,
        help="Specific types of information to redact (default: all)",
    )
    args = parser.parse_args()
    
    # Set up paths
    script_dir = Path(__file__).resolve().parent
    input_dir = (script_dir / args.input).resolve()
    output_dir = (script_dir / args.output).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find PDF files
    if not input_dir.exists():
        print(f"Error: Input directory not found: {input_dir}")
        sys.exit(1)
    
    pdf_files = sorted(input_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"No PDF files found in {input_dir}")
        sys.exit(1)
    
    limit = args.limit or len(pdf_files)
    pdf_files = pdf_files[:limit]
    
    print(f"Generating non-compliant versions from {len(pdf_files)} protocol(s)")
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")
    if args.types:
        print(f"Redaction types: {', '.join(args.types)}")
    else:
        print("Redaction types: ALL")
    print()
    print(f"{'Source File':<45} {'Status':<10} {'Redactions':>12} {'Details'}")
    print("-" * 100)
    
    processed = 0
    failed = 0
    
    for pdf_path in pdf_files:
        output_path = output_dir / pdf_path.name
        
        # Skip if already exists
        if output_path.exists():
            print(f"{pdf_path.name:<45} {'EXISTS':<10}")
            processed += 1
            continue
        
        try:
            stats = redact_text_in_pdf(pdf_path, output_path, args.types)
            details = ", ".join([f"{k}:{v}" for k, v in stats["by_type"].items()])
            print(f"{pdf_path.name:<45} {'OK':<10} {stats['total_redactions']:>12} {details}")
            processed += 1
        except Exception as e:
            print(f"{pdf_path.name:<45} {'FAIL':<10} {str(e)[:50]}")
            failed += 1
    
    print("-" * 100)
    print(f"\nDone. Processed: {processed} | Failed: {failed}")
    print(f"Non-compliant protocols saved to: {output_dir.resolve()}")


if __name__ == "__main__":
    main()
