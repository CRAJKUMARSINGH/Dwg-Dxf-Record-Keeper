# ===============================================
# DRAWING EXTRACTOR - Files + ZIP + RAR
# Author: Grok (for RAJKUMAR SINGH CHAUHAN)
# ===============================================

import os
import sys
import shutil
import argparse
import zipfile
import tempfile
from pathlib import Path
from tqdm import tqdm
import logging
from datetime import datetime

# Optional but recommended
try:
    import rarfile
    RAR_SUPPORT = True
except ImportError:
    RAR_SUPPORT = False

# For PDF & Image filtering
import fitz  # PyMuPDF
import cv2
import numpy as np

# ========================= CONFIG =========================
DRAWING_EXTENSIONS = {'.dwg', '.dxf'}
PDF_EXT = '.pdf'
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp', '.gif', '.webp'}

# =========================================================

def setup_logging(target_dir):
    log_path = os.path.join(target_dir, "drawing_extraction_log.txt")
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s'
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logging.getLogger('').addHandler(console)
    return log_path

def is_drawing_pdf(pdf_path):
    """Heuristic: Is this PDF a CAD/Technical Drawing?"""
    try:
        doc = fitz.open(pdf_path)
        page = doc[0]
        text = page.get_text().strip()
        # If very little text → likely drawing
        if len(text) < 50:
            return True
        # Check for many vector items
        if len(page.get_drawings()) > 5:
            return True
        doc.close()
        return False
    except:
        return False

def is_drawing_image(image_path):
    """Simple but effective line-drawing / sketch detector"""
    try:
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return False
        # Edge density
        edges = cv2.Canny(img, 50, 150)
        edge_ratio = np.sum(edges > 0) / edges.size
        # High contrast + many edges = sketch
        if edge_ratio > 0.03 and np.std(img) > 40:
            return True
        return False
    except:
        return False

def process_file(file_path, target_base, source_base, dry_run=False, force=False):
    ext = Path(file_path).suffix.lower()
    # Calculate relative path from source base
    rel_path = os.path.relpath(file_path, start=source_base)
    
    if ext in DRAWING_EXTENSIONS:
        should_copy = True
    elif ext == PDF_EXT:
        should_copy = is_drawing_pdf(file_path)
    elif ext in IMAGE_EXTENSIONS:
        should_copy = is_drawing_image(file_path)
    else:
        should_copy = False

    if should_copy:
        target_path = os.path.join(target_base, rel_path)
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        
        if dry_run:
            logging.info(f"[DRY-RUN] Would copy: {file_path} → {target_path}")
        else:
            if os.path.exists(target_path) and not force:
                logging.warning(f"Skipped (already exists): {target_path}")
            else:
                shutil.copy2(file_path, target_path)
                logging.info(f"COPIED: {file_path} → {target_path}")
        return True
    else:
        logging.info(f"SKIPPED (not drawing): {file_path}")
        return False

def scan_archive(archive_path, target_base, dry_run=False, force=False):
    logging.info(f"Scanning archive: {archive_path}")
    temp_dir = None
    try:
        if archive_path.lower().endswith('.zip'):
            with zipfile.ZipFile(archive_path) as zf:
                for member in zf.namelist():
                    if member.endswith('/') or not any(member.lower().endswith(e) for e in 
                        list(DRAWING_EXTENSIONS | IMAGE_EXTENSIONS | {PDF_EXT})):
                        continue
                    with zf.open(member) as source, tempfile.NamedTemporaryFile(delete=False, suffix=Path(member).suffix) as temp:
                        shutil.copyfileobj(source, temp)
                        temp_path = temp.name
                    try:
                        # Create mirrored path
                        target_sub = os.path.join(Path(archive_path).stem, member)
                        full_target = os.path.join(target_base, target_sub)
                        os.makedirs(os.path.dirname(full_target), exist_ok=True)
                        
                        if not dry_run:
                            shutil.copy2(temp_path, full_target)
                            logging.info(f"EXTRACTED from ZIP: {archive_path}/{member} → {full_target}")
                    finally:
                        os.unlink(temp_path)
        
        elif archive_path.lower().endswith('.rar') and RAR_SUPPORT:
            rf = rarfile.RarFile(archive_path)
            for member in rf.infolist():
                if member.is_dir() or not any(member.filename.lower().endswith(e) for e in 
                    list(DRAWING_EXTENSIONS | IMAGE_EXTENSIONS | {PDF_EXT})):
                    continue
                temp_path = rf.read(member.filename)  # returns bytes
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(member.filename).suffix) as temp:
                    temp.write(temp_path)
                    temp_path = temp.name
                try:
                    target_sub = os.path.join(Path(archive_path).stem, member.filename)
                    full_target = os.path.join(target_base, target_sub)
                    if not dry_run:
                        shutil.copy2(temp_path, full_target)
                        logging.info(f"EXTRACTED from RAR: {archive_path}/{member.filename} → {full_target}")
                finally:
                    os.unlink(temp_path)
    except Exception as e:
        logging.error(f"Failed to process archive {archive_path}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Drawing Extractor - Files + ZIP + RAR")
    parser.add_argument('-s', '--source', required=True, help='Source root folder')
    parser.add_argument('-t', '--target', required=True, help='Target root folder')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--force', action='store_true', help='Overwrite existing files')
    args = parser.parse_args()

    if not os.path.exists(args.source):
        print("Source folder does not exist!")
        sys.exit(1)

    os.makedirs(args.target, exist_ok=True)
    setup_logging(args.target)

    logging.info(f"=== Drawing Extraction Started ===")
    logging.info(f"Source: {args.source}")
    logging.info(f"Target: {args.target}")
    if args.dry_run:
        logging.info("*** DRY RUN MODE ***")

    count_copied = 0
    count_scanned = 0

    for root, dirs, files in os.walk(args.source):
        for file in files:
            count_scanned += 1
            full_path = os.path.join(root, file)
            ext = Path(file).suffix.lower()

            if ext in {'.zip', '.rar'}:
                scan_archive(full_path, args.target, args.dry_run, args.force)
            elif ext in DRAWING_EXTENSIONS | IMAGE_EXTENSIONS | {PDF_EXT}:
                if process_file(full_path, args.target, args.source, args.dry_run, args.force):
                    count_copied += 1

    logging.info(f"\n=== SUMMARY ===")
    logging.info(f"Total files scanned : {count_scanned}")
    logging.info(f"Files copied        : {count_copied}")
    logging.info(f"Target folder       : {args.target}")
    print(f"\n✅ Done! Check log: {os.path.join(args.target, 'drawing_extraction_log.txt')}")

if __name__ == "__main__":
    main()
