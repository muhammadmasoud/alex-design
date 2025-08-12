from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = 'Test email configuration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--to',
            type=str,
            help='Email address to send test email to',
            default='test@example.com'
        )

    def handle(self, *args, **options):
        to_email = options['to']
        
        try:
            subject = 'Test Email from Alex Design'
            message = 'This is a test email to verify email configuration is working.'
            from_email = settings.DEFAULT_FROM_EMAIL
            
            self.stdout.write(f'Sending test email to: {to_email}')
            self.stdout.write(f'From: {from_email}')
            
            success = send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=[to_email],
                fail_silently=False,
            )
            
            if success:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Test email sent successfully to {to_email}')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('❌ Failed to send test email')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error sending email: {str(e)}')
            )
            self.stdout.write(
                self.style.WARNING('Make sure to configure email settings in .env file')
            )
