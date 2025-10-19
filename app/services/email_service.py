# app/services/email_service.py - COMPLETE FILE WITH WIDER LAYOUT AND ADDRESS
import logging
from typing import Dict
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        # FIXED SENDER EMAIL - All emails come from here
        self.sender_email = "ifthicaralikhan@gmail.com"
        self.sender_password = "phcj svrj imuq mtgg"
        self.sender_name = "Pinnacle Live"
        self.smtp_host = "smtp.gmail.com"
        self.smtp_port = 587
        
        self.template_dir = Path(__file__).parent.parent / "api" / "templates" / "email"
    
    def _get_fallback_template(self) -> str:
        """Professional white theme email template matching Pinnacle Live branding"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.5;
                    color: #1a1a1a;
                    background-color: #f5f5f5;
                    margin: 0;
                    padding: 0;
                }
                .email-wrapper {
                    background-color: #f5f5f5;
                    padding: 40px 20px;
                }
                .email-container { 
                    max-width: 700px;
                    margin: 0 auto; 
                    background-color: #ffffff;
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
                }
                
                /* Header - Clean white with logo */
                .header {
                    background-color: #ffffff;
                    padding: 40px 50px 30px 50px;
                    border-bottom: 1px solid #e5e5e5;
                }
                .logo {
                    display: flex;
                    align-items: baseline;
                    gap: 8px;
                    margin-bottom: 12px;
                }
                .logo-pinnacle {
                    font-size: 28px;
                    font-weight: 300;
                    letter-spacing: 0.5px;
                    color: #1a1a1a;
                }
                .logo-divider {
                    width: 2px;
                    height: 24px;
                    background-color: #B8860B;
                }
                .logo-live {
                    font-size: 18px;
                    font-weight: 400;
                    letter-spacing: 2px;
                    text-transform: uppercase;
                    color: #B8860B;
                }
                .header-subtitle {
                    font-size: 13px;
                    color: #666666;
                    letter-spacing: 0.5px;
                    text-transform: uppercase;
                }
                
                /* Content */
                .content {
                    padding: 40px 50px;
                    background-color: #ffffff;
                }
                .content h1 {
                    font-size: 24px;
                    font-weight: 300;
                    color: #1a1a1a;
                    margin: 0 0 20px 0;
                    letter-spacing: -0.5px;
                }
                .content p {
                    color: #333333;
                    margin: 0 0 16px 0;
                    font-size: 15px;
                    line-height: 1.5;
                }
                
                /* Proposal Details Box */
                .proposal-details {
                    background-color: #fafafa;
                    border-left: 3px solid #B8860B;
                    padding: 28px 32px;
                    margin: 30px 0;
                    border-radius: 4px;
                }
                .proposal-details h3 {
                    font-size: 14px;
                    font-weight: 600;
                    color: #1a1a1a;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                    margin: 0 0 20px 0;
                }
                .proposal-details-grid {
                    display: grid;
                    gap: 16px;
                }
                .detail-row {
                    display: grid;
                    grid-template-columns: 180px 1fr;
                    gap: 24px;
                    padding: 10px 0;
                    border-bottom: 1px solid #e5e5e5;
                    align-items: start;
                }
                .detail-row:last-child {
                    border-bottom: none;
                }
                .detail-label {
                    font-size: 14px;
                    color: #666666;
                    font-weight: 400;
                }
                .detail-value {
                    font-size: 14px;
                    color: #1a1a1a;
                    font-weight: 500;
                    line-height: 1.4;
                }
                .detail-value.highlight {
                    color: #B8860B;
                    font-size: 18px;
                    font-weight: 600;
                }
                
                /* CTA Button */
                .cta-section {
                    text-align: center;
                    margin: 40px 0;
                }
                .cta-button {
                    display: inline-block;
                    padding: 16px 48px;
                    background-color: #1a1a1a;
                    color: #ffffff !important;
                    text-decoration: none;
                    border-radius: 4px;
                    font-weight: 500;
                    font-size: 15px;
                    letter-spacing: 0.5px;
                    transition: background-color 0.2s ease;
                }
                .cta-button:hover {
                    background-color: #333333;
                }
                
                /* Session Info Box - Privacy Policy Style */
                .session-info {
                    background-color: #fffbf0;
                    border: 1px solid #f0e5d0;
                    border-radius: 4px;
                    padding: 20px 28px;
                    margin: 30px 0;
                }
                .session-info h4 {
                    font-size: 12px;
                    font-weight: 600;
                    color: #1a1a1a;
                    margin: 0 0 14px 0;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }
                .session-info ul {
                    margin: 0;
                    padding-left: 20px;
                    color: #333333;
                }
                .session-info li {
                    margin: 6px 0;
                    font-size: 13px;
                    line-height: 1.4;
                }
                
                /* Footer */
                .footer {
                    background-color: #fafafa;
                    padding: 32px 50px;
                    border-top: 1px solid #e5e5e5;
                    text-align: center;
                }
                .footer p {
                    font-size: 13px;
                    color: #666666;
                    margin: 6px 0;
                    line-height: 1.4;
                }
                .footer-signature {
                    margin: 24px 0 16px 0;
                    font-size: 14px;
                    color: #1a1a1a;
                }
                .footer-signature strong {
                    font-weight: 600;
                }
                .footer-link {
                    color: #B8860B;
                    text-decoration: none;
                }
                .footer-link:hover {
                    text-decoration: underline;
                }
                .footer-address {
                    margin-top: 20px;
                    padding-top: 20px;
                    border-top: 1px solid #e5e5e5;
                }
                .footer-address p {
                    font-size: 12px;
                    color: #666666;
                    line-height: 1.5;
                    margin: 3px 0;
                }
                .footer-address p strong {
                    color: #1a1a1a;
                    font-weight: 600;
                }
                .footer-legal {
                    margin-top: 20px;
                    padding-top: 20px;
                    border-top: 1px solid #e5e5e5;
                    font-size: 11px;
                    color: #999999;
                    line-height: 1.4;
                }
                
                /* Responsive */
                @media only screen and (max-width: 600px) {
                    .email-wrapper { padding: 20px 10px; }
                    .header, .content, .footer { padding: 24px 20px; }
                    .proposal-details { padding: 20px; }
                    .detail-row { 
                        grid-template-columns: 1fr; 
                        gap: 6px; 
                    }
                    .cta-button { padding: 14px 32px; font-size: 14px; }
                }
            </style>
        </head>
        <body>
            <div class="email-wrapper">
                <div class="email-container">
                    
                    <!-- Header -->
                    <div class="header">
                        <div class="logo">
                            <span class="logo-pinnacle">pinnacle</span>
                            <div class="logo-divider"></div>
                            <span class="logo-live">live<sup style="font-size: 10px;">™</sup></span>
                        </div>
                        <div class="header-subtitle">Event Production Proposal</div>
                    </div>
                    
                    <!-- Content -->
                    <div class="content">
                        <h1>Your Proposal is Ready for Review</h1>
                        
                        <p>Hello {{recipient_name}},</p>
                        
                        <p>We're pleased to share your comprehensive event production proposal. This document outlines our recommended equipment, services, and pricing for your upcoming event.</p>
                        
                        <!-- Proposal Details -->
                        <div class="proposal-details">
                            <h3>Proposal Summary</h3>
                            <div class="proposal-details-grid">
                                <div class="detail-row">
                                    <span class="detail-label">Proposal Number</span>
                                    <span class="detail-value">#{{proposal_id}}</span>
                                </div>
                                <div class="detail-row">
                                    <span class="detail-label">Client</span>
                                    <span class="detail-value">{{proposal_client_name}}</span>
                                </div>
                                <div class="detail-row">
                                    <span class="detail-label">Venue</span>
                                    <span class="detail-value">{{proposal_venue}}</span>
                                </div>
                                <div class="detail-row">
                                    <span class="detail-label">Total Investment</span>
                                    <span class="detail-value highlight">${{proposal_total_cost}}</span>
                                </div>
                            </div>
                        </div>
                        
                        <!-- CTA Button -->
                        <div class="cta-section">
                            <a href="{{temp_access_url}}" class="cta-button">
                                VIEW PROPOSAL
                            </a>
                        </div>
                        
                        <!-- Session Information - Privacy Policy Style -->
                        <div class="session-info">
                            <h4>Secure Access Information</h4>
                            <ul>
                                <li>This secure link expires 24 hours after opening</li>
                                <li>You can extend your session by 10 minutes if needed</li>
                                <li>Each new click creates a fresh 24-hour viewing session</li>
                                <li>This link is personalized and secure for your review</li>
                            </ul>
                        </div>
                        
                        <p style="margin-top: 32px;">We're excited to partner with you on this event. If you have any questions about the proposal or would like to discuss any aspect of the production plan, please don't hesitate to reach out.</p>
                        
                        <!-- Footer Signature -->
                        <div class="footer-signature">
                            <p style="margin-bottom: 4px;">Best regards,</p>
                            <p><strong>The Pinnacle Live Team</strong></p>
                            <p><a href="mailto:support@pinnaclelive.com" class="footer-link">support@pinnaclelive.com</a></p>
                        </div>
                    </div>
                    
                    <!-- Footer -->
                    <div class="footer">
                        <p><strong>Pinnacle Live</strong> | Event Production Excellence</p>
                        <p style="margin-top: 10px;">We elevate live event expectations for people and venues who demand better.</p>
                        
                        <!-- Company Address -->
                        <div class="footer-address">
                            <p><strong>Pinnacle Live</strong></p>
                            <p>1500 W. Shure Drive, Suite 100</p>
                            <p>Arlington Heights, IL 60004</p>
                            <p>312-500-0063</p>
                        </div>
                        
                        <div class="footer-legal">
                            <p>© 2025 Pinnacle Live. All rights reserved.</p>
                            <p style="margin-top: 6px;">You received this email because you were granted access to review an event production proposal. This is an automated message—please do not reply directly to this email.</p>
                        </div>
                    </div>
                    
                </div>
            </div>
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
        """Replace template variables"""
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            template_content = template_content.replace(placeholder, str(value))
        return template_content
    
    async def send_temp_access_email(
        self,
        recipient_email: str,
        recipient_name: str,
        temp_access_url: str,
        proposal_id: str,
        proposal_client_name: str,
        proposal_venue: str,
        proposal_total_cost: float
    ) -> bool:
        """
        Send proposal access email to the entered email address
        ALL EMAILS SENT FROM: ifthicaralikhan@gmail.com
        
        Args:
            recipient_email: The email address to send to (betterandbliss@gmail.com, etc.)
            recipient_name: Name for greeting
            temp_access_url: The secure access link
            proposal_id: Job number
            proposal_client_name: Client name from proposal
            proposal_venue: Venue from proposal
            proposal_total_cost: Total cost from proposal
        """
        
        try:
            # Load and render template
            template_content = self._get_fallback_template()
            
            email_html = self.render_template(template_content, {
                "recipient_name": recipient_name,
                "temp_access_url": temp_access_url,
                "proposal_id": proposal_id,
                "proposal_client_name": proposal_client_name,
                "proposal_venue": proposal_venue,
                "proposal_total_cost": f"{proposal_total_cost:,.2f}"
            })
            
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Pinnacle Live Proposal #{proposal_id} - {proposal_client_name}"
            msg['From'] = f"{self.sender_name} <{self.sender_email}>"
            msg['To'] = recipient_email
            
            # Attach HTML content
            html_part = MIMEText(email_html, 'html')
            msg.attach(html_part)
            
            # Send email via Gmail SMTP
            logger.info(f"📧 Sending email to {recipient_email}...")
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            logger.info("=" * 80)
            logger.info("✅ EMAIL SENT SUCCESSFULLY")
            logger.info("=" * 80)
            logger.info(f"From: {self.sender_name} <{self.sender_email}>")
            logger.info(f"To: {recipient_email}")
            logger.info(f"Subject: Proposal #{proposal_id} - {proposal_client_name}")
            logger.info(f"Access URL: {temp_access_url}")
            logger.info(f"Proposal: {proposal_client_name}")
            logger.info(f"Venue: {proposal_venue}")
            logger.info(f"Total: ${proposal_total_cost:,.2f}")
            logger.info("=" * 80)
            
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"❌ SMTP Authentication Failed: {str(e)}")
            logger.error("Check Gmail App Password or 2-Factor Authentication settings")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"❌ SMTP Error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to send email to {recipient_email}: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

# Global instance
email_service = EmailService()