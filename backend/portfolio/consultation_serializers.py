from rest_framework import serializers
from .models import ConsultationSettings, DayOff, Booking
from datetime import datetime, timedelta, time, date
import re


class ConsultationSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsultationSettings
        fields = [
            'id', 'meeting_duration_minutes', 'buffer_time_minutes',
            'monday_hours', 'tuesday_hours', 'wednesday_hours', 
            'thursday_hours', 'friday_hours', 'saturday_hours', 'sunday_hours',
            'booking_enabled', 'advance_booking_days', 'minimum_notice_hours',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_meeting_duration_minutes(self, value):
        if value < 15 or value > 480:  # 15 minutes to 8 hours
            raise serializers.ValidationError(
                "Meeting duration must be between 15 minutes and 8 hours"
            )
        return value
    
    def validate_buffer_time_minutes(self, value):
        if value < 0 or value > 120:  # 0 to 2 hours
            raise serializers.ValidationError(
                "Buffer time must be between 0 and 120 minutes"
            )
        return value
    
    def validate_working_hours_format(self, hours_str):
        """Validate working hours format (e.g., '09:00-17:00')"""
        if not hours_str or not hours_str.strip():
            return None  # Empty means day off
        
        pattern = r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]-([0-1]?[0-9]|2[0-3]):[0-5][0-9]$'
        if not re.match(pattern, hours_str.strip()):
            raise serializers.ValidationError(
                f"Invalid hours format: '{hours_str}'. Use format like '09:00-17:00'"
            )
        
        # Validate that start time is before end time
        start_str, end_str = hours_str.strip().split('-')
        start_time = datetime.strptime(start_str, '%H:%M').time()
        end_time = datetime.strptime(end_str, '%H:%M').time()
        
        if start_time >= end_time:
            raise serializers.ValidationError(
                f"Start time must be before end time in '{hours_str}'"
            )
        
        return hours_str.strip()
    
    def validate_monday_hours(self, value):
        return self.validate_working_hours_format(value)
    
    def validate_tuesday_hours(self, value):
        return self.validate_working_hours_format(value)
    
    def validate_wednesday_hours(self, value):
        return self.validate_working_hours_format(value)
    
    def validate_thursday_hours(self, value):
        return self.validate_working_hours_format(value)
    
    def validate_friday_hours(self, value):
        return self.validate_working_hours_format(value)
    
    def validate_saturday_hours(self, value):
        return self.validate_working_hours_format(value)
    
    def validate_sunday_hours(self, value):
        return self.validate_working_hours_format(value)


class DayOffSerializer(serializers.ModelSerializer):
    class Meta:
        model = DayOff
        fields = ['id', 'date', 'reason', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate_date(self, value):
        # Don't allow past dates
        if value < date.today():
            raise serializers.ValidationError(
                "Cannot create day off for past dates"
            )
        return value


class BookingSerializer(serializers.ModelSerializer):
    end_time = serializers.SerializerMethodField()
    is_past = serializers.SerializerMethodField()
    can_be_cancelled = serializers.SerializerMethodField()
    
    class Meta:
        model = Booking
        fields = [
            'id', 'client_name', 'client_email', 'client_phone',
            'date', 'time', 'end_time', 'duration_minutes',
            'project_details', 'message', 'status', 'admin_notes',
            'cancellation_reason', 'is_past', 'can_be_cancelled',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'end_time', 'is_past', 'can_be_cancelled']
    
    def get_end_time(self, obj):
        return obj.get_end_time()
    
    def get_is_past(self, obj):
        return obj.is_past()
    
    def get_can_be_cancelled(self, obj):
        return obj.can_be_cancelled()
    
    def validate_date(self, value):
        # Get consultation settings
        settings = ConsultationSettings.get_settings()
        
        # Check if booking is enabled
        if not settings.booking_enabled:
            raise serializers.ValidationError(
                "Consultation bookings are currently disabled"
            )
        
        # Check minimum notice
        min_notice_datetime = datetime.now() + timedelta(hours=settings.minimum_notice_hours)
        if value < min_notice_datetime.date():
            raise serializers.ValidationError(
                f"Bookings require at least {settings.minimum_notice_hours} hours notice"
            )
        
        # Check advance booking limit
        max_advance_date = date.today() + timedelta(days=settings.advance_booking_days)
        if value > max_advance_date:
            raise serializers.ValidationError(
                f"Cannot book more than {settings.advance_booking_days} days in advance"
            )
        
        # Check if it's a working day
        weekday = value.weekday()  # 0=Monday, 6=Sunday
        if not settings.is_working_day(weekday):
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            raise serializers.ValidationError(
                f"{day_names[weekday]} is not a working day"
            )
        
        # Check if it's a day off
        if DayOff.objects.filter(date=value).exists():
            day_off = DayOff.objects.get(date=value)
            reason_text = f" ({day_off.reason})" if day_off.reason else ""
            raise serializers.ValidationError(
                f"This date is not available for bookings{reason_text}"
            )
        
        return value
    
    def validate_time(self, value):
        return value
    
    def validate(self, data):
        """Validate the booking as a whole"""
        date_val = data.get('date')
        time_val = data.get('time')
        duration = data.get('duration_minutes')
        
        if not all([date_val, time_val, duration]):
            return data
        
        # Get consultation settings
        settings = ConsultationSettings.get_settings()
        
        # Set duration from settings if not provided
        if not duration:
            data['duration_minutes'] = settings.meeting_duration_minutes
            duration = settings.meeting_duration_minutes
        
        # Check if time is within working hours
        weekday = date_val.weekday()
        working_hours = settings.get_working_hours_for_day(weekday)
        
        if working_hours:
            start_str, end_str = working_hours.split('-')
            work_start = datetime.strptime(start_str, '%H:%M').time()
            work_end = datetime.strptime(end_str, '%H:%M').time()
            
            # Calculate end time of consultation
            consultation_start = datetime.combine(date_val, time_val)
            consultation_end = consultation_start + timedelta(minutes=duration)
            consultation_end_time = consultation_end.time()
            
            if time_val < work_start or consultation_end_time > work_end:
                raise serializers.ValidationError(
                    f"Consultation time must be within working hours: {working_hours}"
                )
        
        # Check for conflicts with existing bookings
        existing_bookings = Booking.objects.filter(
            date=date_val,
            status__in=['pending', 'confirmed']
        ).exclude(pk=self.instance.pk if self.instance else None)
        
        consultation_start = datetime.combine(date_val, time_val)
        consultation_end = consultation_start + timedelta(minutes=duration)
        
        for booking in existing_bookings:
            existing_start = datetime.combine(booking.date, booking.time)
            existing_end = existing_start + timedelta(minutes=booking.duration_minutes)
            
            # Add buffer time
            buffer_minutes = settings.buffer_time_minutes
            existing_end_with_buffer = existing_end + timedelta(minutes=buffer_minutes)
            consultation_start_with_buffer = consultation_start - timedelta(minutes=buffer_minutes)
            
            # Check for overlap
            if (consultation_start < existing_end_with_buffer and 
                consultation_end > existing_start):
                raise serializers.ValidationError(
                    f"Time slot conflicts with existing booking at {booking.time}"
                )
        
        # Check monthly booking limit for new bookings
        client_email = data.get('client_email')
        if client_email and Booking.has_monthly_booking(client_email, date_val):
            # Don't apply this restriction if updating an existing booking
            if not self.instance:
                from calendar import month_name
                month_year = f"{month_name[date_val.month]} {date_val.year}"
                raise serializers.ValidationError(
                    f"You already have a consultation booked for {month_year}. "
                    f"Each client is limited to one consultation per month. "
                    f"Please choose a date in a different month or contact us to reschedule your existing booking."
                )
        
        return data
    
    def validate_client_email(self, value):
        # Basic email validation (Django already does this, but we can add custom rules)
        if value and len(value) > 254:
            raise serializers.ValidationError("Email address is too long")
        return value
    
    def validate_client_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Client name is required")
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Client name must be at least 2 characters")
        return value.strip()


class PublicBookingSerializer(BookingSerializer):
    """Serializer for public booking creation (excludes admin fields)"""
    
    class Meta:
        model = Booking
        fields = [
            'client_name', 'client_email', 'client_phone',
            'date', 'time', 'duration_minutes',
            'project_details', 'message'
        ]
    
    def create(self, validated_data):
        # Set default duration from settings if not provided
        if 'duration_minutes' not in validated_data:
            settings = ConsultationSettings.get_settings()
            validated_data['duration_minutes'] = settings.meeting_duration_minutes
        
        # Set status to pending for public bookings
        validated_data['status'] = 'pending'
        
        return super().create(validated_data)


class AvailableTimeSlotsSerializer(serializers.Serializer):
    """Serializer for available time slots request/response"""
    date = serializers.DateField()
    available_slots = serializers.ListField(
        child=serializers.TimeField(),
        read_only=True
    )
    
    def validate_date(self, value):
        # Basic validation - detailed validation happens in the view
        if value < date.today():
            raise serializers.ValidationError("Cannot get slots for past dates")
        return value
