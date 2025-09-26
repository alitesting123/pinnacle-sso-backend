# app/services/email_service.py
import logging
from typing import Dict
from pathlib import Path

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.template_dir = Path(__file__).parent.parent / "templates" / "email"
    
    def _get_fallback_template(self) -> str:
        """Simple fallback template"""
        return """
        <html>
        <body>
            <h2>Your Pinnacle Live Proposal is Ready</h2>
            <p>Hello {{client_name}},</p>
            <p>Your proposal is ready for review. Click the link below:</p>
            <p><a href="{{temp_access_url}}" style="background: #3b82f6; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View My Proposal</a></p>
            <p><strong>Important:</strong> This link expires in 20 minutes after clicking.</p>
            <p>Best regards,<br>Pinnacle Live Team</p>
        </body>
        </html>
        """
    
    def load_template(self, template_name: str) -> str:
        """Load email template from file"""
        template_path = self.template_dir / f"{template_name}.html"
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.warning(f"Template file not found: {template_path}, using fallback")
            return self._get_fallback_template()
    
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
        proposal_id: str = "306780"
    ) -> bool:
        """Send temporary access email to client"""
        
        try:
            # Load and render template
            template_content = self.load_template("temp_access")
            
            email_html = self.render_template(template_content, {
                "client_name": client_name,
                "temp_access_url": temp_access_url,
                "proposal_id": proposal_id
            })
            
            # For development - just log the email content
            logger.info("=" * 50)
            logger.info("DEVELOPMENT EMAIL")
            logger.info("=" * 50)
            logger.info(f"To: {recipient_email}")
            logger.info(f"Subject: Your Pinnacle Live Proposal is Ready")
            logger.info(f"Access URL: {temp_access_url}")
            logger.info("=" * 50)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send temp access email to {recipient_email}: {str(e)}")
            return False

# Global email service instance
email_service = EmailService()