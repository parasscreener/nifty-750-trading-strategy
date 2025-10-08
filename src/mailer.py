import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

logger = logging.getLogger(__name__)

class EmailSender:
    """Gmail SMTP email sender"""

    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 465
        self.sender_email = os.environ.get('EMAIL_USER')
        self.sender_password = os.environ.get('EMAIL_PASS')
        self.default_recipient = os.environ.get('EMAIL_TO', 'paras.m.parmar@gmail.com')

        if not all([self.sender_email, self.sender_password]):
            logger.warning("EMAIL_USER and EMAIL_PASS not set")

    def send_html_email(self, html_content: str, subject: str, recipient: str = None) -> bool:
        """Send HTML email via Gmail SMTP"""
        try:
            if not self.sender_email or not self.sender_password:
                logger.error("Email credentials not available")
                return False

            recipient = recipient or self.default_recipient

            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = recipient

            html_part = MIMEText(html_content, "html", "utf-8")
            message.attach(html_part)

            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=30) as server:
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)

            logger.info(f"Email sent successfully to {recipient}")
            return True

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"Email authentication failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Email sending error: {e}")
            return False

    def send_daily_report(self, html_content: str, recipient: str = None) -> bool:
        """Send daily trading report"""
        from datetime import datetime

        now = datetime.now()
        subject = f"Nifty 750 Trading Signals - {now.strftime('%Y-%m-%d')} (9:30 AM IST)"

        return self.send_html_email(html_content, subject, recipient)

    def test_connection(self) -> bool:
        """Test email connection and credentials"""
        try:
            if not self.sender_email or not self.sender_password:
                logger.error("Email credentials not set")
                return False

            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=15) as server:
                server.login(self.sender_email, self.sender_password)
                logger.info("Email connection test successful")
                return True
        except Exception as e:
            logger.error(f"Email connection test failed: {e}")
            return False

def send_daily_trading_report(html_content: str, csv_file: str = None, recipient: str = None) -> bool:
    """Convenience function to send daily report"""
    try:
        sender = EmailSender()
        return sender.send_daily_report(html_content, recipient)
    except Exception as e:
        logger.error(f"Failed to send daily report: {e}")
        return False

def send_error_alert(error_message: str, recipient: str = None) -> bool:
    """Send error notification email"""
    try:
        sender = EmailSender()
        subject = "Trading System Error Alert"

        html_content = f'''
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: red;">Trading System Error</h2>
            <p><strong>Error Message:</strong> {error_message}</p>
            <p><strong>Time:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            <p><em>Please check the GitHub Actions logs for more details.</em></p>
        </body>
        </html>
        '''

        return sender.send_html_email(html_content, subject, recipient)
    except Exception as e:
        logger.error(f"Failed to send error alert: {e}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Test email system
    try:
        sender = EmailSender()
        if sender.test_connection():
            print("Email system configured correctly")
        else:
            print("Email system not configured")
    except Exception as e:
        print(f"Email test error: {e}")
