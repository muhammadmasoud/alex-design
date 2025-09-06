from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db import transaction
from datetime import datetime, timedelta, time, date
from .models import ConsultationSettings, DayOff, Booking
from .consultation_serializers import (
    ConsultationSettingsSerializer, DayOffSerializer, 
    BookingSerializer, PublicBookingSerializer, AvailableTimeSlotsSerializer
)
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class ConsultationSettingsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing consultation settings (admin only)
    """
    serializer_class = ConsultationSettingsSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        return ConsultationSettings.objects.all()
    
    def list(self, request, *args, **kwargs):
        """Always return the single settings instance"""
        settings_instance = ConsultationSettings.get_settings()
        serializer = self.get_serializer(settings_instance)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """Update existing settings instead of creating new ones"""
        settings_instance = ConsultationSettings.get_settings()
        serializer = self.get_serializer(settings_instance, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        """Update existing settings"""
        settings_instance = ConsultationSettings.get_settings()
        serializer = self.get_serializer(settings_instance, data=request.data, partial=kwargs.get('partial', False))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DayOffViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing days off (admin only)
    """
    queryset = DayOff.objects.all()
    serializer_class = DayOffSerializer
    permission_classes = [IsAdminUser]
    ordering = ['date']
    
    def get_queryset(self):
        # Only show future days off by default
        queryset = super().get_queryset()
        show_past = self.request.query_params.get('show_past', 'false').lower() == 'true'
        
        if not show_past:
            queryset = queryset.filter(date__gte=date.today())
        
        return queryset.order_by('date')


class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing bookings
    """
    queryset = Booking.objects.all()
    permission_classes = [IsAdminUser]  # Admin only for full CRUD
    ordering = ['-date', '-time']
    
    def get_serializer_class(self):
        return BookingSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            try:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(date__gte=start_date_obj)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(date__lte=end_date_obj)
            except ValueError:
                pass
        
        return queryset.order_by('-date', '-time')
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update booking status"""
        booking = self.get_object()
        new_status = request.data.get('status')
        cancellation_reason = request.data.get('cancellation_reason', '')
        
        if new_status not in [choice[0] for choice in Booking.STATUS_CHOICES]:
            return Response(
                {'error': 'Invalid status'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        old_status = booking.status
        booking.status = new_status
        
        # Store cancellation reason if provided
        if new_status == 'cancelled' and cancellation_reason:
            booking.cancellation_reason = cancellation_reason
        
        booking.save()
        
        # Send email notification if status changed to confirmed or cancelled
        if new_status != old_status and new_status in ['confirmed', 'cancelled']:
            self._send_status_update_email(booking, old_status, new_status, cancellation_reason)
        
        serializer = self.get_serializer(booking)
        return Response(serializer.data)
    
    def _send_status_update_email(self, booking, old_status, new_status, cancellation_reason=''):
        """Send email notification to client about status update"""
        try:
            if new_status == 'confirmed':
                subject = f"Consultation Confirmed - {booking.date}"
                message = f"""
Dear {booking.client_name},

Your consultation has been confirmed for:
Date: {booking.date}
Time: {booking.time}
Duration: {booking.duration_minutes} minutes

We look forward to meeting with you!

Best regards,
Alex Design Team
"""
            elif new_status == 'cancelled':
                subject = f"Consultation Cancelled - {booking.date}"
                message = f"""
Dear {booking.client_name},

We regret to inform you that your consultation scheduled for {booking.date} at {booking.time} has been cancelled.

{f"Reason: {cancellation_reason}" if cancellation_reason else ""}

Please contact us to reschedule at your convenience.

Best regards,
Alex Design Team
"""
            else:
                return
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [booking.client_email],
                fail_silently=False,
            )
            logger.info(f"Status update email sent to {booking.client_email} for booking {booking.id}")
        except Exception as e:
            logger.error(f"Failed to send status update email for booking {booking.id}: {e}")


class PublicBookingView(APIView):
    """
    Public API for creating consultation bookings
    """
    permission_classes = []  # No authentication required
    
    def post(self, request, *args, **kwargs):
        """Create a new consultation booking"""
        serializer = PublicBookingSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    booking = serializer.save()
                    
                    # Send confirmation email to client
                    self._send_booking_confirmation_email(booking)
                    
                    # Send notification email to admin
                    self._send_admin_notification_email(booking)
                
                return Response({
                    'message': 'Consultation booking created successfully',
                    'booking_id': booking.id,
                    'status': booking.status
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                logger.error(f"Error creating booking: {e}")
                return Response({
                    'error': 'Failed to create booking. Please try again.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _send_booking_confirmation_email(self, booking):
        """Send confirmation email to client"""
        try:
            subject = f"Consultation Booking Received - {booking.date}"
            message = f"""
Dear {booking.client_name},

Thank you for booking a consultation with Alex Design!

Your booking details:
Date: {booking.date}
Time: {booking.time}
Duration: {booking.duration_minutes} minutes
Status: {booking.get_status_display()}

We will review your booking and confirm it shortly. You will receive another email once your consultation is confirmed.

If you have any questions, please don't hesitate to contact us.

Best regards,
Alex Design Team
"""
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [booking.client_email],
                fail_silently=False,
            )
            logger.info(f"Confirmation email sent to {booking.client_email} for booking {booking.id}")
        except Exception as e:
            logger.error(f"Failed to send confirmation email for booking {booking.id}: {e}")
    
    def _send_admin_notification_email(self, booking):
        """Send notification email to admin"""
        try:
            subject = f"New Consultation Booking - {booking.date} {booking.time}"
            message = f"""
New consultation booking received:

Client: {booking.client_name}
Email: {booking.client_email}
Phone: {booking.client_phone or 'Not provided'}

Date: {booking.date}
Time: {booking.time}
Duration: {booking.duration_minutes} minutes

Project Details: {booking.project_details or 'Not provided'}
Message: {booking.message or 'Not provided'}

Please log in to the admin dashboard to confirm or manage this booking.
"""
            
            admin_email = getattr(settings, 'CONTACT_EMAIL', settings.DEFAULT_FROM_EMAIL)
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [admin_email],
                fail_silently=False,
            )
            logger.info(f"Admin notification email sent for booking {booking.id}")
        except Exception as e:
            logger.error(f"Failed to send admin notification email for booking {booking.id}: {e}")


class AvailableTimeSlotsView(APIView):
    """
    API for getting available time slots for a specific date
    """
    permission_classes = []  # No authentication required
    
    def get(self, request, *args, **kwargs):
        """Get available time slots for a specific date"""
        date_str = request.query_params.get('date')
        
        if not date_str:
            return Response({
                'error': 'Date parameter is required (format: YYYY-MM-DD)'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            requested_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({
                'error': 'Invalid date format. Use YYYY-MM-DD'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate date
        serializer = AvailableTimeSlotsSerializer(data={'date': requested_date})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate available slots
        available_slots = self._calculate_available_slots(requested_date)
        
        return Response({
            'date': requested_date,
            'available_slots': [slot.strftime('%H:%M') for slot in available_slots],
            'total_slots': len(available_slots)
        })
    
    def _calculate_available_slots(self, requested_date):
        """
        Smart algorithm to calculate available time slots
        """
        # Get consultation settings
        settings = ConsultationSettings.get_settings()
        
        # Check if bookings are enabled
        if not settings.booking_enabled:
            return []
        
        # Check minimum notice
        min_notice_datetime = datetime.now() + timedelta(hours=settings.minimum_notice_hours)
        if requested_date < min_notice_datetime.date():
            return []
        
        # Check advance booking limit
        max_advance_date = date.today() + timedelta(days=settings.advance_booking_days)
        if requested_date > max_advance_date:
            return []
        
        # Check if it's a working day
        weekday = requested_date.weekday()  # 0=Monday, 6=Sunday
        if not settings.is_working_day(weekday):
            return []
        
        # Check if it's a day off
        if DayOff.objects.filter(date=requested_date).exists():
            return []
        
        # Get working hours for the day
        working_hours = settings.get_working_hours_for_day(weekday)
        if not working_hours:
            return []
        
        # Parse working hours
        start_str, end_str = working_hours.split('-')
        work_start = datetime.strptime(start_str, '%H:%M').time()
        work_end = datetime.strptime(end_str, '%H:%M').time()
        
        # Get existing bookings for the day
        existing_bookings = Booking.objects.filter(
            date=requested_date,
            status__in=['pending', 'confirmed']
        ).order_by('time')
        
        # Generate all possible time slots
        available_slots = []
        meeting_duration = settings.meeting_duration_minutes
        buffer_time = settings.buffer_time_minutes
        slot_interval = 15  # Generate slots every 15 minutes
        
        # Start from working hours start time
        current_time = datetime.combine(requested_date, work_start)
        work_end_datetime = datetime.combine(requested_date, work_end)
        
        # If it's today, make sure we don't show past slots
        if requested_date == date.today():
            now = datetime.now()
            if current_time < now:
                # Round up to next 15-minute interval
                minutes_past_15 = now.minute % 15
                if minutes_past_15 > 0:
                    current_time = now.replace(minute=now.minute + (15 - minutes_past_15), second=0, microsecond=0)
                else:
                    current_time = now.replace(second=0, microsecond=0)
        
        while current_time + timedelta(minutes=meeting_duration) <= work_end_datetime:
            consultation_end = current_time + timedelta(minutes=meeting_duration)
            
            # Check if this slot conflicts with any existing booking
            is_available = True
            
            for booking in existing_bookings:
                existing_start = datetime.combine(booking.date, booking.time)
                existing_end = existing_start + timedelta(minutes=booking.duration_minutes)
                
                # Add buffer time around existing booking
                existing_start_with_buffer = existing_start - timedelta(minutes=buffer_time)
                existing_end_with_buffer = existing_end + timedelta(minutes=buffer_time)
                
                # Check for overlap
                if (current_time < existing_end_with_buffer and 
                    consultation_end > existing_start_with_buffer):
                    is_available = False
                    break
            
            if is_available:
                available_slots.append(current_time.time())
            
            # Move to next time slot
            current_time += timedelta(minutes=slot_interval)
        
        return available_slots


class ConsultationSettingsPublicView(APIView):
    """
    Public API for getting basic consultation settings (for frontend)
    """
    permission_classes = []  # No authentication required
    
    def get(self, request, *args, **kwargs):
        """Get public consultation settings"""
        settings = ConsultationSettings.get_settings()
        
        return Response({
            'booking_enabled': settings.booking_enabled,
            'meeting_duration_minutes': settings.meeting_duration_minutes,
            'advance_booking_days': settings.advance_booking_days,
            'minimum_notice_hours': settings.minimum_notice_hours,
            'working_hours': {
                'monday': settings.monday_hours or '',
                'tuesday': settings.tuesday_hours or '',
                'wednesday': settings.wednesday_hours or '',
                'thursday': settings.thursday_hours or '',
                'friday': settings.friday_hours or '',
                'saturday': settings.saturday_hours or '',
                'sunday': settings.sunday_hours or '',
            }
        })


class PublicDaysOffView(APIView):
    """
    Public API for fetching days off (to show as disabled dates in booking calendar)
    """
    permission_classes = []  # No authentication required
    
    def get(self, request, *args, **kwargs):
        """Get current and future days off"""
        try:
            # Only return current and future days off
            days_off = DayOff.objects.filter(date__gte=date.today()).order_by('date')
            
            # Return only necessary fields for calendar
            public_data = [
                {
                    'date': day_off.date,
                    'reason': day_off.reason  # Optional: might want to show reason on hover
                }
                for day_off in days_off
            ]
            
            return Response(public_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error fetching public days off: {e}")
            return Response({
                'error': 'Failed to load days off'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CheckMonthlyBookingView(APIView):
    """
    API for checking if a client can book in a specific month
    """
    permission_classes = []  # No authentication required
    
    def get(self, request, *args, **kwargs):
        """Check if client already has a booking in the specified month"""
        try:
            client_email = request.query_params.get('email')
            date_str = request.query_params.get('date')
            
            if not client_email or not date_str:
                return Response({
                    'error': 'Both email and date parameters are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response({
                    'error': 'Invalid date format. Use YYYY-MM-DD'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            has_booking = Booking.has_monthly_booking(client_email, target_date)
            
            return Response({
                'has_monthly_booking': has_booking,
                'can_book': not has_booking,
                'month': target_date.strftime('%B %Y')
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error checking monthly booking: {e}")
            return Response({
                'error': 'Failed to check monthly booking status'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
