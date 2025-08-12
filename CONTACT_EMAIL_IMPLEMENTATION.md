# Contact Form Email Implementation

## Overview
The contact form now supports sending emails directly to the business owner without requiring user authentication. Users can submit contact forms and the system will automatically send an email notification.

## Features Implemented

### 1. Backend Email System
- **Django Email Backend**: Uses Django's built-in `send_mail` function
- **SMTP Configuration**: Configurable for Gmail, Outlook, Yahoo, or custom SMTP servers
- **HTML & Text Emails**: Sends both HTML and plain text versions
- **Service Integration**: Includes service information when users inquire about specific services
- **Error Handling**: Comprehensive error handling and logging

### 2. Contact API Endpoint
- **URL**: `POST /api/contact/`
- **Authentication**: None required (public endpoint)
- **Request Format**:
  ```json
  {
    "name": "John Doe",
    "email": "john@example.com", 
    "message": "I'm interested in your services...",
    "service": "Architectural Design" // Optional
  }
  ```
- **Response Format**:
  ```json
  {
    "message": "Thank you for your message! We will get back to you soon.",
    "success": true
  }
  ```

### 3. Frontend Integration
- **No Authentication Required**: Users can send messages without signing up
- **Service Context**: When users click "Buy Now" on services, the contact form is pre-filled
- **Improved Error Handling**: Better user feedback for success/failure scenarios
- **Form Validation**: Client and server-side validation

## Setup Instructions

### Step 1: Configure Email Settings
1. **Copy the environment template**:
   ```bash
   cd backend
   cp .env.example .env
   ```

2. **Edit `.env` file with your email settings**:
   ```bash
   # For Gmail (recommended)
   EMAIL_HOST_USER=your_email@gmail.com
   EMAIL_HOST_PASSWORD=your_app_password_here
   DEFAULT_FROM_EMAIL=noreply@alexdesign.com
   CONTACT_EMAIL=owner@alexdesign.com
   ```

### Step 2: Gmail Setup (Recommended)
1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to Google Account settings
   - Security > 2-Step Verification > App passwords
   - Generate password for "Mail"
   - Use this password in `EMAIL_HOST_PASSWORD`

### Step 3: Alternative Email Providers

#### Outlook/Hotmail
```bash
EMAIL_HOST_USER=your_email@outlook.com
EMAIL_HOST_PASSWORD=your_password
# Settings.py already configured for Outlook
```

#### Yahoo Mail
```bash
EMAIL_HOST_USER=your_email@yahoo.com
EMAIL_HOST_PASSWORD=your_app_password
# Update EMAIL_HOST in settings.py to smtp.mail.yahoo.com
```

#### Custom SMTP Server
```bash
EMAIL_HOST_USER=your_email@yourdomain.com
EMAIL_HOST_PASSWORD=your_password
# Update EMAIL_HOST and EMAIL_PORT in settings.py
```

### Step 4: Test Email Configuration
```bash
cd backend
python manage.py test_email --to your_email@example.com
```

### Step 5: Development Mode (Console Backend)
For development/testing without actual email sending:

Edit `backend/backend/settings.py`:
```python
# Uncomment this line for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

This will print emails to the console instead of sending them.

## Email Template

### Subject Line
- **With Service**: "New Service Inquiry: [Service Name] - From [Customer Name]"
- **General**: "New Contact Form Submission - From [Customer Name]"

### Email Content
```
New contact form submission from Alex Design website:

Name: John Doe
Email: john@example.com
Service Interest: Architectural Design

Message:
I'm interested in your architectural design services for my new home project...

---
This email was sent from the contact form on your website.
Reply directly to this email to respond to John Doe.
```

## Security Features
- **Input Validation**: All form fields are validated
- **Rate Limiting**: Can be added if needed to prevent spam
- **HTML Sanitization**: User input is properly escaped
- **Error Logging**: Failed email attempts are logged

## Testing Workflow

### 1. Test Backend API
```bash
curl -X POST http://localhost:8000/api/contact/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "message": "This is a test message",
    "service": "Architectural Design"
  }'
```

### 2. Test Frontend Integration
1. Visit `http://localhost:8080/contact`
2. Fill out the contact form
3. Submit and check for success message
4. Check your email inbox for the notification

### 3. Test Service Integration
1. Visit `http://localhost:8080/services`
2. Click "Buy Now" on any service
3. Verify contact form is pre-filled
4. Submit and verify service information is included in email

## Error Handling

### Common Issues
1. **Authentication Failed**: Check email credentials
2. **Connection Refused**: Verify EMAIL_HOST and EMAIL_PORT
3. **Permission Denied**: Ensure app password is used for Gmail

### Logs
Check Django logs for email errors:
```bash
cd backend
python manage.py runserver
# Check console output for email-related errors
```

## Production Considerations

### 1. Environment Variables
Never commit email credentials to version control. Use environment variables or secure secret management.

### 2. Email Delivery
Consider using professional email services for production:
- **SendGrid**
- **Mailgun** 
- **Amazon SES**
- **Postmark**

### 3. Monitoring
Implement monitoring for:
- Failed email deliveries
- Spam protection
- Rate limiting
- Email bounce handling

### 4. GDPR Compliance
Consider data protection requirements when storing/processing contact form data.

## Files Modified/Created

### Backend Files
- `backend/backend/settings.py` - Email configuration
- `backend/portfolio/contact_serializers.py` - Contact form serializer
- `backend/portfolio/views.py` - Contact view added
- `backend/backend/urls.py` - Contact endpoint added
- `backend/portfolio/management/commands/test_email.py` - Email testing command
- `backend/.env.example` - Environment template

### Frontend Files
- `frontend/src/pages/Contact.tsx` - Enhanced error handling
- `frontend/src/lib/api.ts` - Contact endpoint (already existed)

The contact form is now fully functional and ready for production use!
