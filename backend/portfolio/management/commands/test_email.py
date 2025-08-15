from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Test email configuration with detailed diagnostics'

    def add_arguments(self, parser):
        parser.add_argument(
            '--to',
            type=str,
            help='Email address to send test email to',
            default='test@example.com'
        )
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Show detailed configuration debug info',
        )

    def handle(self, *args, **options):
        to_email = options['to']
        debug = options['debug']
        
        self.stdout.write(self.style.HTTP_INFO('🔧 EMAIL CONFIGURATION DIAGNOSTICS'))
        self.stdout.write('=' * 50)
        
        # Check environment variables
        self.stdout.write(self.style.HTTP_INFO('Environment Variables:'))
        env_vars = {
            'EMAIL_HOST_USER': os.environ.get('EMAIL_HOST_USER', ''),
            'EMAIL_HOST_PASSWORD': os.environ.get('EMAIL_HOST_PASSWORD', ''),
            'DEFAULT_FROM_EMAIL': os.environ.get('DEFAULT_FROM_EMAIL', ''),
            'CONTACT_EMAIL': os.environ.get('CONTACT_EMAIL', ''),
            'DJANGO_ENV': os.environ.get('DJANGO_ENV', ''),
            'PRODUCTION': os.environ.get('PRODUCTION', ''),
        }
        
        for key, value in env_vars.items():
            status = '✅ SET' if value else '❌ NOT SET'
            display_value = '***hidden***' if 'PASSWORD' in key and value else value
            self.stdout.write(f'  {key}: {status} ({display_value})')
        
        self.stdout.write('')
        
        # Check Django settings
        self.stdout.write(self.style.HTTP_INFO('Django Email Settings:'))
        settings_vars = {
            'EMAIL_BACKEND': getattr(settings, 'EMAIL_BACKEND', 'NOT SET'),
            'EMAIL_HOST': getattr(settings, 'EMAIL_HOST', 'NOT SET'),
            'EMAIL_PORT': getattr(settings, 'EMAIL_PORT', 'NOT SET'),
            'EMAIL_USE_TLS': getattr(settings, 'EMAIL_USE_TLS', 'NOT SET'),
            'EMAIL_HOST_USER': 'SET' if getattr(settings, 'EMAIL_HOST_USER', '') else 'NOT SET',
            'EMAIL_HOST_PASSWORD': 'SET' if getattr(settings, 'EMAIL_HOST_PASSWORD', '') else 'NOT SET',
            'DEFAULT_FROM_EMAIL': getattr(settings, 'DEFAULT_FROM_EMAIL', 'NOT SET'),
            'CONTACT_EMAIL': getattr(settings, 'CONTACT_EMAIL', 'NOT SET'),
        }
        
        for key, value in settings_vars.items():
            status_color = self.style.SUCCESS if 'SET' in str(value) and value != 'NOT SET' else self.style.ERROR
            self.stdout.write(f'  {key}: {status_color(value)}')
        
        self.stdout.write('')
        self.stdout.write('=' * 50)
        
        # Test sending email
        try:
            subject = '🏗️ Alex Design - Email Configuration Test'
            message = '''
This is a test email from your Alex Design website to verify that email configuration is working correctly.

If you receive this email, your contact form should work properly!

Technical Details:
- Django Email Backend: SMTP
- SMTP Server: smtp.gmail.com
- Port: 587
- TLS: Enabled

Best regards,
Alex Design System
            '''
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@alexdesign.com')
            
            self.stdout.write(f'📧 Sending test email...')
            self.stdout.write(f'   From: {from_email}')
            self.stdout.write(f'   To: {to_email}')
            self.stdout.write(f'   Subject: {subject}')
            self.stdout.write('')
            
            success = send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=[to_email],
                fail_silently=False,
            )
            
            if success:
                self.stdout.write(
                    self.style.SUCCESS('✅ TEST EMAIL SENT SUCCESSFULLY!')
                )
                self.stdout.write(
                    self.style.SUCCESS('   Check your inbox (and spam folder)')
                )
                self.stdout.write(
                    self.style.SUCCESS('   Your contact form should now work!')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('❌ FAILED TO SEND TEST EMAIL')
                )
                self.stdout.write(
                    self.style.WARNING('   Check your email configuration')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ ERROR SENDING EMAIL: {str(e)}')
            )
            self.stdout.write('')
            self.stdout.write(self.style.WARNING('🔧 TROUBLESHOOTING STEPS:'))
            self.stdout.write('1. Create Gmail App Password (not regular password)')
            self.stdout.write('2. Enable 2-Factor Authentication on Gmail')
            self.stdout.write('3. Create .env file with proper credentials')
            self.stdout.write('4. Restart Django application')
            self.stdout.write('')
            self.stdout.write(self.style.HTTP_INFO('📖 See PRODUCTION_EMAIL_SETUP.md for detailed instructions'))
