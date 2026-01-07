#!/usr/bin/env python3
"""
QR Code Label Generator for SL655 Template
Generates sequential QR codes for keg tracking labels.
"""

import argparse
import qrcode
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
import io
import sys
import os


def generate_qr_code(url, size_inches=1.2):
    """
    Generate a QR code image for the given URL.

    Args:
        url: The URL to encode in the QR code
        size_inches: Size of the QR code in inches

    Returns:
        QR code image object
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=1,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    return img


def create_qr_overlay(start_num, count, base_url, prefix="ITEM-"):
    """
    Create a PDF overlay with QR codes positioned for the SL655 template.

    The SL655 template has 24 labels in a 4x6 grid on letter-sized paper.

    Args:
        start_num: Starting item number
        count: Number of labels to generate
        base_url: Base URL for QR codes
        prefix: Prefix for item IDs (e.g., "ITEM-", "KEG-")

    Returns:
        PDF buffer with QR codes
    """
    # Create a PDF in memory
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=letter)

    # SL655 template specifications (letter size: 8.5" x 11")
    # 4 columns x 6 rows = 24 labels per sheet
    cols = 4
    rows = 6

    # Label dimensions and positioning (from SL655-XW specs)
    # SL655: 1.5" x 1.5" labels on letter size sheet (8.5" x 11")
    label_width = 1.5 * inch
    label_height = 1.5 * inch

    # Margins from specs
    left_margin = 0.78125 * inch
    top_margin = 0.5 * inch

    # Spacing between labels from specs
    horizontal_spacing = 0.3125 * inch
    vertical_spacing = 0.2 * inch

    # Calculate starting position (top-left corner of first label)
    start_x = left_margin
    start_y = 11 * inch - top_margin  # Letter height minus top margin

    # Total spacing between label starts (label size + gap)
    x_spacing = label_width + horizontal_spacing
    y_spacing = label_height + vertical_spacing

    # QR code size
    qr_size = 1.2 * inch

    labels_per_page = cols * rows
    current_num = start_num

    for i in range(count):
        if i > 0 and i % labels_per_page == 0:
            # Start a new page
            c.showPage()

        # Calculate position in grid
        page_index = i % labels_per_page
        col = page_index % cols
        row = page_index // cols

        # Calculate QR code position (centered in label with extra top padding)
        x = start_x + (col * x_spacing) + (label_width - qr_size) / 2
        y = start_y - (row * y_spacing) - label_height + (label_height - qr_size) / 2 + 0.05 * inch

        # Generate QR code for this item number
        item_id = f"{prefix}{current_num:04d}"
        url = f"{base_url}{item_id}"

        # Save QR code to temporary buffer
        qr_img = generate_qr_code(url)
        img_buffer = io.BytesIO()
        qr_img.save(img_buffer, format='PNG')
        img_buffer.seek(0)

        # Draw QR code on canvas
        c.drawImage(ImageReader(img_buffer), x, y,
                    width=qr_size, height=qr_size, preserveAspectRatio=True)

        # Add text below QR code (closer to QR code)
        text_y = y - 0.1 * inch
        c.setFont("Helvetica", 8)
        c.drawCentredString(x + qr_size/2, text_y, item_id)

        current_num += 1

    c.save()
    packet.seek(0)
    return packet


def merge_pdfs(template_path, overlay_buffer, output_path):
    """
    Merge the QR code overlay with the template PDF.

    Args:
        template_path: Path to the SL655.pdf template
        overlay_buffer: Buffer containing the QR code overlay
        output_path: Path for the output PDF
    """
    # Read the template
    template_pdf = PdfReader(template_path)
    overlay_pdf = PdfReader(overlay_buffer)

    writer = PdfWriter()

    # Merge each page
    num_overlay_pages = len(overlay_pdf.pages)

    for i in range(num_overlay_pages):
        # Get template page (use first page for all overlays)
        template_page = template_pdf.pages[0]

        # Get overlay page
        overlay_page = overlay_pdf.pages[i]

        # Merge them
        template_page.merge_page(overlay_page)
        writer.add_page(template_page)

    # Write output
    with open(output_path, 'wb') as output_file:
        writer.write(output_file)


def main():
    parser = argparse.ArgumentParser(
        description='Generate QR code labels for kegs using SL655 template'
    )
    parser.add_argument(
        '--start',
        type=int,
        default=1,
        help='Starting keg number (default: 1)'
    )
    parser.add_argument(
        '--count',
        type=int,
        required=True,
        help='Number of labels to generate'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='output/labels.pdf',
        help='Output PDF filename (default: output/labels.pdf)'
    )
    parser.add_argument(
        '--template',
        type=str,
        default='templates/SL655.pdf',
        help='Path to SL655.pdf template (default: templates/SL655.pdf)'
    )
    parser.add_argument(
        '--base-url',
        type=str,
        required=True,
        help='Base URL for QR codes (e.g., https://example.com/item/)'
    )
    parser.add_argument(
        '--prefix',
        type=str,
        default='ITEM-',
        help='Prefix for item IDs (default: ITEM-)'
    )

    args = parser.parse_args()

    # Ensure output directory exists
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Generating {args.count} labels starting from {args.prefix}{args.start:04d}...")

    # Create QR code overlay
    overlay = create_qr_overlay(args.start, args.count, args.base_url, args.prefix)

    # Merge with template
    print(f"Merging with template: {args.template}")
    merge_pdfs(args.template, overlay, args.output)

    print(f"✓ Successfully created {args.output}")
    print(f"  Labels: {args.prefix}{args.start:04d} through {args.prefix}{args.start + args.count - 1:04d}")

    # Calculate number of sheets
    sheets = (args.count + 23) // 24  # 24 labels per sheet
    print(f"  Total sheets: {sheets}")


if __name__ == '__main__':
    main()
