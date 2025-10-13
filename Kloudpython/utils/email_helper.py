from flask_mail import Mail, Message
from flask import current_app
import os
from datetime import datetime


def send_receipt_email(user_email, order_data, pdf_path):
    """
    Send PDF receipt to user's email
    
    Args:

        user_email (str): Recipient email address
        order_data (dict): Order information for email content
        pdf_path (str): Path to the PDF file to attach
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Initialize Flask-Mail
        mail = Mail(current_app)
        
        # Create message
        msg = Message(
            subject="Your KloudCart Order Receipt",
            sender=current_app.config['MAIL_USERNAME'],
            recipients=[user_email]
        )
        
        # Email body
        msg.body = f"""
Dear Valued Customer,

Thank you for your order on KloudCart!

Order Details:
- Order ID: {order_data['order_id']}
- Order Date: {order_data['current_date']}
- Total Amount: ₹{order_data['total']:.2f}

Your receipt is attached to this email. Please keep it for your records.

If you have any questions about your order, please don't hesitate to contact our support team.

Thank you for shopping with KloudCart!

Best regards,
KloudCart Team
support@kloudcart.com
        """
        
        # HTML version of the email
        msg.html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">
                    Thank you for your order!
                </h2>
                
                <p>Dear Valued Customer,</p>
                
                <p>Thank you for your order on <strong>KloudCart</strong>!</p>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="color: #2c3e50; margin-top: 0;">Order Details:</h3>
                    <ul style="list-style: none; padding: 0;">
                        <li><strong>Order ID:</strong> {order_data['order_id']}</li>
                        <li><strong>Order Date:</strong> {order_data['current_date']}</li>
                        <li><strong>Total Amount:</strong> ₹{order_data['total']:.2f}</li>
                    </ul>
                </div>
                
                <p>Your receipt is attached to this email. Please keep it for your records.</p>
                
                <p>If you have any questions about your order, please don't hesitate to contact our support team.</p>
                
                <p>Thank you for shopping with <strong>KloudCart</strong>!</p>
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
                    <p style="color: #666; font-size: 14px;">
                        Best regards,<br>
                        <strong>KloudCart Team</strong><br>
                        <a href="mailto:support@kloudcart.com" style="color: #3498db;">support@kloudcart.com</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Attach PDF file
        if os.path.exists(pdf_path):
            with current_app.open_resource(pdf_path) as pdf_file:
                msg.attach(
                    filename=f"KloudCart_Receipt_{order_data['order_id']}.pdf",
                    content_type="application/pdf",
                    data=pdf_file.read()
                )
        
        # Send email
        mail.send(msg)
        
        return True
        
    except Exception as e:
        current_app.logger.error(f"Failed to send email to {user_email}: {str(e)}")
        return False


def get_user_email_from_db(user_email):
    """
    Get user email from MongoDB users collection
    This is a helper function to verify user exists in the database
    
    Args:
        user_email (str): User email to verify
    
    Returns:
        str: User email if found, None otherwise
    """
    try:
        from ..db import get_users_collection
        
        users_collection = get_users_collection()
        user = users_collection.find_one({"email": user_email})
        
        if user:
            return user["email"]
        return None
        
    except Exception as e:
        current_app.logger.error(f"Failed to get user email from database: {str(e)}")
        return None


def cleanup_pdf_file(pdf_path):
    """
    Optionally delete the PDF file after sending email
    
    Args:
        pdf_path (str): Path to the PDF file to delete
    
    Returns:
        bool: True if file deleted successfully, False otherwise
    """
    try:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
            return True
        return False
    except Exception as e:
        current_app.logger.error(f"Failed to delete PDF file {pdf_path}: {str(e)}")
        return False
