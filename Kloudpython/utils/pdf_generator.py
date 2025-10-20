from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import os
import pytz


def get_ist_time():
    """Get current time in Indian Standard Time (IST)"""
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist)


def generate_receipt_pdf(order_data, output_path):
    """
    Generate a PDF receipt for an order
    
    elements:
        order_data (dict): Dictionary containing order information
            - order_id (str): Order ID
            - user_email (str): User email
            - items (list): List of order items
            - total (float): Total amount
            - current_date (str): Order date
        output_path (str): Path where PDF should be saved
    
    Returns:
        str: Path to the generated PDF file
    """
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Create the PDF document
    doc = SimpleDocTemplate(output_path, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=12,
        alignment=TA_LEFT
    )
    
    # Title
    title = Paragraph("KloudCart Receipt", title_style)
    elements.append(title)
    elements.append(Spacer(1, 20))
    
    # Company info
    company_info = Paragraph(
        "<b>KloudCart E-Commerce</b><br/>"
        "Your Trusted Online Shopping Partner<br/>"
        "Email: support@kloudcart.com",
        header_style
    )
    elements.append(company_info)
    elements.append(Spacer(1, 20))
    
    # Order details
    order_details = [
        ["Order ID:", order_data.get('order_id', '')],
        ["Customer:", order_data.get('user_email', '')],
        ["Order Date:", order_data.get('current_date', get_ist_time().strftime("%B %d, %Y at %I:%M %p"))],
        ["", ""]  # Empty row for spacing
    ]
    
    order_table = Table(order_details, colWidths=[2*inch, 4*inch])
    order_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    elements.append(order_table)
    elements.append(Spacer(1, 20))
    
    # Items table header
    items_header = ["#", "Product Name", "Category", "Qty", "Unit Price (₹)", "Subtotal (₹)"]
    
    # Items data
    items_data = [items_header]
    for i, item in enumerate(order_data.get('items', []), 1):
        items_data.append([
            str(i),
            item.get('name', ''),
            item.get('category', 'N/A'),
            str(item.get('quantity', 0)),
            f"{float(item.get('price', 0)):.2f}",
            f"{float(item.get('subtotal', 0)):.2f}"
        ])
    
    # Create items table
    items_table = Table(items_data, colWidths=[0.5*inch, 2.5*inch, 1.5*inch, 0.8*inch, 1.2*inch, 1.2*inch])
    items_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        
        # Data rows
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    
    elements.append(items_table)
    elements.append(Spacer(1, 20))
    
    # Total section
    total_amount = float(order_data.get('total', 0))
    total_data = [
        ["", "", "", "", "Total Amount:", f"₹{total_amount:.2f}"]
    ]
    
    total_table = Table(total_data, colWidths=[0.5*inch, 2.5*inch, 1.5*inch, 0.8*inch, 1.2*inch, 1.2*inch])
    total_table.setStyle(TableStyle([
        ('ALIGN', (4, 0), (5, 0), 'RIGHT'),
        ('FONTNAME', (4, 0), (5, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (4, 0), (5, 0), 12),
        ('BACKGROUND', (4, 0), (5, 0), colors.lightblue),
        ('TEXTCOLOR', (4, 0), (5, 0), colors.darkblue),
        ('GRID', (4, 0), (5, 0), 1, colors.black),
    ]))
    
    elements.append(total_table)
    elements.append(Spacer(1, 30))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        textColor=colors.grey
    )
    
    footer = Paragraph(
        "Thank you for shopping with KloudCart!<br/>"
        "This is a computer-generated receipt.<br/>"
        "For support, contact us at support@kloudcart.com",
        footer_style
    )
    elements.append(footer)
    
    # Build PDF
    doc.build(elements)
    
    return output_path


def create_receipts_directory():
    """Create the receipts directory if it doesn't exist"""
    receipts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'receipts')
    os.makedirs(receipts_dir, exist_ok=True)
    return receipts_dir
