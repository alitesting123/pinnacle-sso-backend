# app/services/email_service.py - COMPLETE REPLACEMENT
import logging
from typing import Dict
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.template_dir = Path(__file__).parent.parent / "api" / "templates" / "email"
        
        # Gmail configuration - FIXED SENDER
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = "ifthicaralikhan@gmail.com"  # FIXED SENDER EMAIL
        self.sender_password = "phcj svrj imuq mtgg"  # YOU NEED TO SET THIS
        self.sender_name = "Pinnacle Live"
    
    def _get_email_template(self) -> str:
        """Professional email template"""
        return """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; }
                .header { background: #1e40af; padding: 30px 20px; text-align: center; }
                .header h1 { color: white; margin: 0; font-size: 28px; }
                .content { padding: 30px 20px; background: #ffffff; }
                .button { display: inline-block; background: #3b82f6; color: white; padding: 15px 40px; 
                          text-decoration: none; border-radius: 5px; font-weight: bold; margin: 20px 0; }
                .button:hover { background: #2563eb; }
                .info-box { background: #f8fafc; padding: 20px; border-radius: 8px; 
                            border-left: 4px solid #3b82f6; margin: 20px 0; }
                .info-box h3 { color: #1e40af; margin-top: 0; }
                .footer { padding: 20px; text-align: center; color: #666; font-size: 12px; }
                .highlight { background: #fef3c7; padding: 2px 6px; border-radius: 3px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎬 Pinnacle Live</h1>
                    <p style="color: #e0e7ff; margin: 5px 0;">Event Production Proposal</p>
                </div>
                
                <div class="content">
                    <h2 style="color: #1e40af;">Your Proposal is Ready for Review</h2>
                    
                    <p>Hello <strong>{{client_name}}</strong>,</p>
                    
                    <p>Your event proposal from Pinnacle Live is ready for your review:</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{{temp_access_url}}" class="button">
                            📄 View My Proposal
                        </a>
                    </div>
                    
                    <div class="info-box">
                        <h3>⏱️ Important Access Information:</h3>
                        <ul style="margin: 10px 0;">
                            <li><strong>Proposal ID:</strong> <span class="highlight">#{{proposal_id}}</span></li>
                            <li><strong>Access Duration:</strong> 20 minutes after clicking the link</li>
                            <li><strong>Extend Session:</strong> You can extend by 10 minutes if needed</li>
                            <li><strong>Secure Link:</strong> Personalized and encrypted for your safety</li>
                        </ul>
                    </div>
                    
                    <div style="background: #fef2f2; padding: 15px; border-radius: 5px; border-left: 4px solid #ef4444; margin: 20px 0;">
                        <p style="margin: 0; color: #991b1b;">
                            <strong>⚠️ Note:</strong> This is a temporary access link. Each time you click it, 
                            a new 20-minute session begins. The link cannot be reused after the session expires.
                        </p>
                    </div>
                    
                    <p>If you have any questions about this proposal, please don't hesitate to reach out.</p>
                    
                    <p style="margin-top: 30px;">
                        Best regards,<br>
                        <strong>The Pinnacle Live Team</strong><br>
                        <a href="mailto:ifthikarali20@gmail.com" style="color: #3b82f6;">ifthikarali20@gmail.com</a>
                    </p>
                </div>
                
                <div class="footer">
                    <p>This email was sent from Pinnacle Live Event Production</p>
                    <p>© 2025 Pinnacle Live. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def render_template(self, template_content: str, variables: Dict[str, str]) -> str:
        """Simple template variable replacement"""
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"  # {{variable}}
            template_content = template_content.replace(placeholder, str(value))
        return template_content
    
    async def send_temp_access_email(
        self,
        recipient_email: str,
        client_name: str,
        temp_access_url: str,
        proposal_id: str
    ) -> bool:
        """
        Send temporary access email to client
        
        Args:
            recipient_email: Client's email (RECEIVER - can be anyone, even ali2@gmail.com for testing)
            client_name: Client's name
            temp_access_url: Generated temporary access URL
            proposal_id: Proposal/Job number
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        
        try:
            logger.info(f"Preparing to send email to {recipient_email} for proposal #{proposal_id}")
            
            # Load and render template
            template_content = self._get_email_template()
            
            email_html = self.render_template(template_content, {
                "client_name": client_name,
                "temp_access_url": temp_access_url,
                "proposal_id": proposal_id
            })
            
            # Create email message
            message = MIMEMultipart("alternative")
            message["Subject"] = f"🎬 Your Pinnacle Live Proposal #{proposal_id} is Ready"
            message["From"] = f"{self.sender_name} <{self.sender_email}>"  # Always from ifthikarali20@gmail.com
            message["To"] = recipient_email  # This changes per client
            message["Reply-To"] = self.sender_email
            
            # Attach HTML content
            html_part = MIMEText(email_html, "html")
            message.attach(html_part)
            
            # Send email via Gmail SMTP
            logger.info(f"Connecting to Gmail SMTP server...")
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.set_debuglevel(1)  # Enable debug output
                server.starttls()
                logger.info(f"Logging in as {self.sender_email}...")
                server.login(self.sender_email, self.sender_password)
                logger.info(f"Sending email to {recipient_email}...")
                server.send_message(message)
            
            logger.info(f"✅ EMAIL SENT SUCCESSFULLY!")
            logger.info(f"   From: {self.sender_email}")
            logger.info(f"   To: {recipient_email}")
            logger.info(f"   Proposal: #{proposal_id}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"❌ Gmail authentication failed! Check your app password.")
            logger.error(f"   Error: {str(e)}")
            logger.error(f"   Make sure you're using a Gmail App Password, not your regular password!")
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to send email to {recipient_email}")
            logger.error(f"   Error: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False

# Global email service instance
email_service = EmailService()


# ==========================================
# SETUP INSTRUCTIONS FOR GMAIL APP PASSWORD
# ==========================================
"""
TO SEND EMAILS, YOU MUST:

1. Enable 2-Factor Authentication on ifthikarali20@gmail.com
   - Go to: https://myaccount.google.com/security
   - Turn on 2-Step Verification

2. Generate App Password:
   - Go to: https://myaccount.google.com/apppasswords
   - Select app: "Mail"
   - Select device: "Other (Custom name)" → Type "Pinnacle Live API"
   - Click "Generate"
   - Copy the 16-character password (like: "abcd efgh ijkl mnop")

3. Update this file:
   - Replace "your-gmail-app-password" above with your actual app password
   - Example: self.sender_password = "abcd efgh ijkl mnop"

4. Test the email:
   - In the admin page, add ali2@gmail.com as recipient
   - Select any proposal
   - Click "Send Proposal via Email"
   - Check ali2@gmail.com inbox (might be in Spam first time)

NOTE: All emails will be sent FROM ifthikarali20@gmail.com
      The recipient (TO field) changes based on which client you select
"""