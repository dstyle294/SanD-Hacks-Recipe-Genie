import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

# SMTP Configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USER)

class NotificationService:
    @staticmethod
    def send_expiry_email(user_email: str, user_name: str, items: list):
        if not all([SMTP_USER, SMTP_PASSWORD]):
            print("⚠️ SMTP credentials not set. Skipping email.")
            return

        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = "⏰ Recipe Genie: Ingredients Expiring Soon!"
        message["From"] = FROM_EMAIL
        message["To"] = user_email

        # Create HTML content
        items_html = "<ul>"
        for item in items:
            urgency_color = "#f87171" if item['urgency'] == "high" else "#fbbf24" if item['urgency'] == "medium" else "#4ade80"
            items_html += f"<li style='color: {urgency_color}; margin-bottom: 8px;'><strong>{item['name']}</strong> - Expires in {item['days']} days ({item['storage']})</li>"
        items_html += "</ul>"

        html_content = f"""
            <div style="font-family: sans-serif; background: #0f172a; color: #f8fafc; padding: 40px; border-radius: 20px; max-width: 600px; margin: auto;">
                <h1 style="color: #2dd4bf; margin-top: 0;">Hello {user_name}!</h1>
                <p style="font-size: 16px; line-height: 1.6;">Some of your ingredients are reaching their expiration date. Better use them soon!</p>
                <div style="background: #1e293b; padding: 20px; border-radius: 12px; margin: 24px 0;">
                    {items_html}
                </div>
                <p style="margin-top: 30px; text-align: center;">
                    <a href="http://localhost:5173" style="background: #0d9488; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">Check My Pantry</a>
                </p>
                <p style="font-size: 12px; color: #64748b; margin-top: 40px; text-align: center;">
                    You received this because you have notifications enabled in Recipe Genie.
                </p>
            </div>
        """

        message.attach(MIMEText(html_content, "html"))

        try:
            # Connect to SMTP server
            if SMTP_PORT == 465:
                # SSL connection
                server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
            else:
                # STARTTLS connection
                server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
                server.starttls()
            
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(FROM_EMAIL, user_email, message.as_string())
            server.quit()
            
            print(f"📧 Notification email sent to {user_email} via SMTP")
            return 200
        except Exception as e:
            print(f"❌ Failed to send email via SMTP: {e}")
            return None
