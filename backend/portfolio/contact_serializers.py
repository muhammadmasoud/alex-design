from rest_framework import serializers
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)

class ContactSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100, help_text="Your full name")
    email = serializers.EmailField(help_text="Your email address")
    message = serializers.CharField(max_length=2000, help_text="Your message")
    service = serializers.CharField(max_length=100, required=False, help_text="Service you're interested in")
    
    def validate_name(self, value):
        """Validate name field"""
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters long.")
        return value.strip()
    
    def validate_message(self, value):
        """Validate message field"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Message must be at least 10 characters long.")
        return value.strip()
    
    def send_email(self):
        """Send the contact email"""
        try:
            name = self.validated_data['name']
            email = self.validated_data['email']
            message = self.validated_data['message']
            service = self.validated_data.get('service', '')
            
            # Email subject
            if service:
                subject = f"🏗️ New Service Inquiry: {service} - Alex Design"
            else:
                subject = f"💬 New Contact Message - Alex Design"
            
            # Professional HTML email template
            html_body = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>New Contact Form Submission</title>
                <style>
                    * {{
                        margin: 0;
                        padding: 0;
                        box-sizing: border-box;
                    }}
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        background-color: #f8f9fa;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        background-color: #ffffff;
                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    }}
                    .header {{
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 30px 20px;
                        text-align: center;
                    }}
                    .header h1 {{
                        font-size: 28px;
                        font-weight: 300;
                        margin-bottom: 8px;
                    }}
                    .header p {{
                        font-size: 16px;
                        opacity: 0.9;
                    }}
                    .content {{
                        padding: 40px 30px;
                    }}
                    .info-card {{
                        background-color: #f8f9fa;
                        border-left: 4px solid #667eea;
                        padding: 20px;
                        margin: 20px 0;
                        border-radius: 0 8px 8px 0;
                    }}
                    .info-row {{
                        display: flex;
                        margin-bottom: 12px;
                        align-items: center;
                    }}
                    .info-label {{
                        font-weight: 600;
                        color: #495057;
                        min-width: 120px;
                        font-size: 14px;
                    }}
                    .info-value {{
                        color: #212529;
                        font-size: 14px;
                    }}
                    .message-section {{
                        margin-top: 30px;
                    }}
                    .message-section h3 {{
                        color: #495057;
                        font-size: 18px;
                        margin-bottom: 15px;
                        border-bottom: 2px solid #e9ecef;
                        padding-bottom: 8px;
                    }}
                    .message-content {{
                        background-color: #ffffff;
                        border: 1px solid #e9ecef;
                        border-radius: 8px;
                        padding: 20px;
                        font-size: 14px;
                        line-height: 1.6;
                        color: #495057;
                    }}
                    .action-buttons {{
                        text-align: center;
                        margin: 30px 0;
                    }}
                    .reply-button {{
                        display: inline-block;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        text-decoration: none;
                        padding: 12px 30px;
                        border-radius: 25px;
                        font-weight: 600;
                        font-size: 14px;
                        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                    }}
                    .footer {{
                        background-color: #f8f9fa;
                        padding: 25px 30px;
                        text-align: center;
                        border-top: 1px solid #e9ecef;
                    }}
                    .footer p {{
                        color: #6c757d;
                        font-size: 12px;
                        margin-bottom: 8px;
                    }}
                    .company-info {{
                        color: #495057;
                        font-size: 13px;
                        font-weight: 500;
                    }}
                    .service-badge {{
                        display: inline-block;
                        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                        color: white;
                        padding: 4px 12px;
                        border-radius: 15px;
                        font-size: 12px;
                        font-weight: 600;
                        text-transform: uppercase;
                        letter-spacing: 0.5px;
                    }}
                    @media (max-width: 600px) {{
                        .container {{
                            margin: 0;
                            border-radius: 0;
                        }}
                        .content {{
                            padding: 20px 15px;
                        }}
                        .header {{
                            padding: 20px 15px;
                        }}
                        .header h1 {{
                            font-size: 24px;
                        }}
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🏗️ Alex Design</h1>
                        <p>New Contact Form Submission</p>
                    </div>
                    
                    <div class="content">
                        <div class="info-card">
                            <div class="info-row">
                                <span class="info-label">👤 Name:</span>
                                <span class="info-value"><strong>{name}</strong></span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">📧 Email:</span>
                                <span class="info-value"><a href="mailto:{email}" style="color: #667eea; text-decoration: none;">{email}</a></span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">🕒 Received:</span>
                                <span class="info-value">{self._get_current_datetime()}</span>
                            </div>
                            {f'<div class="info-row"><span class="info-label">🎯 Service:</span><span class="info-value"><span class="service-badge">{service}</span></span></div>' if service else ''}
                        </div>
                        
                        <div class="message-section">
                            <h3>💬 Message Details</h3>
                            <div class="message-content">
                                {message.replace(chr(10), '<br>')}
                            </div>
                        </div>
                        
                        <div class="action-buttons">
                            <a href="mailto:{email}?subject=Re: Your inquiry to Alex Design" class="reply-button">
                                📧 Reply to {name.split()[0]}
                            </a>
                        </div>
                    </div>
                    
                    <div class="footer">
                        <div class="company-info">Alex Design Studio</div>
                        <p>Professional Architecture & Design Services</p>
                        <p>This email was automatically generated from your website contact form.</p>
                        <p style="color: #28a745; font-weight: 600;">🌟 Respond promptly to convert this lead!</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Plain text version for email clients that don't support HTML
            email_body = f"""
🏗️ ALEX DESIGN - NEW CONTACT FORM SUBMISSION

==================================================

👤 CUSTOMER DETAILS:
   Name: {name}
   Email: {email}
   Received: {self._get_current_datetime()}
   {f'Service Interest: {service}' if service else 'Type: General Inquiry'}

💬 MESSAGE:
{message}

==================================================

📧 QUICK ACTIONS:
   • Reply directly to this email to respond to {name}
   • Add {email} to your contacts
   • Follow up within 24 hours for best results

🌟 This is a potential new client - respond promptly!

---
Alex Design Studio
Professional Architecture & Design Services
This email was automatically generated from your website.
            """
            
            # Get recipient email from settings
            recipient_email = getattr(settings, 'CONTACT_EMAIL', 'mohamedaboelhamd765@gmail.com')
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@alexdesign.com')
            
            print(f"Attempting to send email from {from_email} to {recipient_email}")
            
            # Send email
            success = send_mail(
                subject=subject,
                message=email_body,
                from_email=from_email,
                recipient_list=[recipient_email],
                html_message=html_body,
                fail_silently=False,
            )
            
            if success:
                logger.info(f"Contact email sent successfully from {email}")
                print(f"Professional email template sent successfully!")
                return True
            else:
                logger.error(f"Failed to send contact email from {email}")
                print(f"Email sending failed!")
                return False
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error sending contact email: {error_msg}")
            print(f"Email error: {error_msg}")
            
            # Enhanced debugging for production
            print(f"Email configuration debug:")
            print(f"  EMAIL_HOST_USER: {'SET' if getattr(settings, 'EMAIL_HOST_USER', '') else 'NOT SET'}")
            print(f"  EMAIL_HOST_PASSWORD: {'SET' if getattr(settings, 'EMAIL_HOST_PASSWORD', '') else 'NOT SET'}")
            print(f"  EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'NOT SET')}")
            print(f"  EMAIL_PORT: {getattr(settings, 'EMAIL_PORT', 'NOT SET')}")
            print(f"  EMAIL_USE_TLS: {getattr(settings, 'EMAIL_USE_TLS', 'NOT SET')}")
            print(f"  FROM_EMAIL: {from_email}")
            print(f"  TO_EMAIL: {recipient_email}")
            
            # Don't raise the exception, just return False
            return False
    
    def _get_current_datetime(self):
        """Get current datetime in a nice format"""
        from datetime import datetime
        return datetime.now().strftime("%B %d, %Y at %I:%M %p")
    
    def save(self):
        """Send the email when save is called"""
        return self.send_email()
