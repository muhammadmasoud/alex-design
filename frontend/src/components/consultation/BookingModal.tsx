import { useState, useEffect } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Calendar } from "@/components/ui/calendar";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { CalendarIcon, Clock, User, Mail, Phone, MessageSquare } from "lucide-react";
import { format, addDays } from "date-fns";
import { toast } from "@/hooks/use-toast";
import { api, endpoints } from "@/lib/api";
import { PublicConsultationSettings, AvailableSlots, PublicBookingData, DayOff } from "@/types";

interface BookingModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export default function BookingModal({ open, onOpenChange }: BookingModalProps) {
  const [currentStep, setCurrentStep] = useState<'date' | 'time' | 'details'>('date');
  const [selectedDate, setSelectedDate] = useState<Date | undefined>();
  const [selectedTime, setSelectedTime] = useState<string>('');
  const [availableSlots, setAvailableSlots] = useState<string[]>([]);
  const [settings, setSettings] = useState<PublicConsultationSettings | null>(null);
  const [daysOff, setDaysOff] = useState<DayOff[]>([]);
  const [formData, setFormData] = useState({
    client_name: '',
    client_email: '',
    client_phone: '',
    project_details: '',
    message: ''
  });
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [monthlyBookingCheck, setMonthlyBookingCheck] = useState<{
    checked: boolean;
    hasBooking: boolean;
    month?: string;
  }>({ checked: false, hasBooking: false });

  // Fetch consultation settings when modal opens
  useEffect(() => {
    if (open) {
      fetchSettings();
      fetchDaysOff();
    }
  }, [open]);

  // Fetch available slots when date changes
  useEffect(() => {
    if (selectedDate && settings) {
      fetchAvailableSlots(selectedDate);
    }
  }, [selectedDate, settings]);

  // Check monthly booking limit when email and date are available
  useEffect(() => {
    if (formData.client_email && selectedDate) {
      checkMonthlyBooking(formData.client_email, selectedDate);
    } else {
      setMonthlyBookingCheck({ checked: false, hasBooking: false });
    }
  }, [formData.client_email, selectedDate]);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      const response = await api.get(endpoints.consultations.settings);
      setSettings(response.data);
    } catch (error: any) {
      console.error('Error fetching consultation settings:', error);
      toast({
        title: "Error",
        description: "Failed to load consultation settings. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchDaysOff = async () => {
    try {
      const response = await api.get(endpoints.consultations.daysOff);
      setDaysOff(response.data.results || response.data);
    } catch (error: any) {
      console.error('Error fetching days off:', error);
      // Don't show error toast for days off as it's not critical
    }
  };

  const fetchAvailableSlots = async (date: Date) => {
    try {
      setLoading(true);
      const response = await api.get(endpoints.consultations.availableSlots, {
        params: { date: format(date, 'yyyy-MM-dd') }
      });
      const data: AvailableSlots = response.data;
      setAvailableSlots(data.available_slots);
    } catch (error: any) {
      console.error('Error fetching available slots:', error);
      setAvailableSlots([]);
      toast({
        title: "Error",
        description: "Failed to load available time slots. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const checkMonthlyBooking = async (email: string, date: Date) => {
    if (!email || !date) {
      setMonthlyBookingCheck({ checked: false, hasBooking: false });
      return;
    }

    try {
      const response = await api.get(endpoints.consultations.checkMonthly, {
        params: { 
          email: email,
          date: format(date, 'yyyy-MM-dd')
        }
      });
      
      setMonthlyBookingCheck({
        checked: true,
        hasBooking: response.data.has_monthly_booking,
        month: response.data.month
      });

      // Show warning if user already has a booking this month
      if (response.data.has_monthly_booking) {
        toast({
          title: "Monthly Limit Reached",
          description: `You already have a consultation booked for ${response.data.month}. Each client can only book one consultation per month.`,
          variant: "destructive",
        });
      }
    } catch (error: any) {
      console.error('Error checking monthly booking:', error);
      setMonthlyBookingCheck({ checked: false, hasBooking: false });
    }
  };

  const handleDateSelect = (date: Date | undefined) => {
    if (date && settings) {
      const today = new Date();
      const minDate = addDays(today, Math.ceil(settings.minimum_notice_hours / 24));
      const maxDate = addDays(today, settings.advance_booking_days);

      if (date < minDate || date > maxDate) {
        toast({
          title: "Invalid Date",
          description: `Please select a date between ${format(minDate, 'PPP')} and ${format(maxDate, 'PPP')}.`,
          variant: "destructive",
        });
        return;
      }

      setSelectedDate(date);
      setSelectedTime(''); // Reset selected time when date changes
    }
  };

  const handleTimeSelect = (time: string) => {
    setSelectedTime(time);
  };

  const handleSubmit = async () => {
    if (!selectedDate || !selectedTime || !formData.client_name || !formData.client_email) {
      toast({
        title: "Missing Information",
        description: "Please fill in all required fields.",
        variant: "destructive",
      });
      return;
    }

    // Check for monthly booking limit
    if (monthlyBookingCheck.checked && monthlyBookingCheck.hasBooking) {
      toast({
        title: "Monthly Limit Reached",
        description: `You already have a consultation booked for ${monthlyBookingCheck.month}. Each client can only book one consultation per month.`,
        variant: "destructive",
      });
      return;
    }

    try {
      setSubmitting(true);
      
      const bookingData: PublicBookingData = {
        client_name: formData.client_name,
        client_email: formData.client_email,
        client_phone: formData.client_phone || undefined,
        date: format(selectedDate, 'yyyy-MM-dd'),
        time: selectedTime,
        duration_minutes: settings?.meeting_duration_minutes,
        project_details: formData.project_details || undefined,
        message: formData.message || undefined,
      };

      await api.post(endpoints.consultations.book, bookingData);

      toast({
        title: "Booking Successful!",
        description: "Your consultation has been booked. You will receive a confirmation email shortly.",
      });

      // Reset form and close modal
      resetForm();
      onOpenChange(false);

    } catch (error: any) {
      console.error('Error submitting booking:', error);
      const errorMessage = error.response?.data?.error || error.response?.data?.message || "Failed to book consultation. Please try again.";
      toast({
        title: "Booking Failed",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setSubmitting(false);
    }
  };

  const resetForm = () => {
    setCurrentStep('date');
    setSelectedDate(undefined);
    setSelectedTime('');
    setAvailableSlots([]);
    setMonthlyBookingCheck({ checked: false, hasBooking: false });
    setFormData({
      client_name: '',
      client_email: '',
      client_phone: '',
      project_details: '',
      message: ''
    });
  };

  const handleClose = () => {
    resetForm();
    onOpenChange(false);
  };

  const isWorkingDay = (date: Date): boolean => {
    if (!settings) return false;
    
    const dayNames = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
    const dayName = dayNames[date.getDay()] as keyof typeof settings.working_hours;
    const workingHours = settings.working_hours[dayName];
    
    return Boolean(workingHours && workingHours.trim());
  };

  const isDayOff = (date: Date): boolean => {
    const dateString = format(date, 'yyyy-MM-dd');
    return daysOff.some(dayOff => dayOff.date === dateString);
  };

  const getWorkingHours = (date: Date): string => {
    if (!settings) return '';
    
    const dayNames = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
    const dayName = dayNames[date.getDay()] as keyof typeof settings.working_hours;
    
    return settings.working_hours[dayName] || '';
  };

  if (!settings?.booking_enabled) {
    return (
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Consultation Booking</DialogTitle>
          </DialogHeader>
          <div className="text-center py-8">
            <p className="text-muted-foreground">
              Consultation bookings are currently not available. Please contact us directly for appointments.
            </p>
            <Button onClick={handleClose} className="mt-4">
              Close
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    );
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="w-[95vw] max-w-4xl max-h-[90vh] overflow-hidden flex flex-col p-0">
        <DialogHeader className="px-4 py-6 border-b shrink-0">
          <DialogTitle className="text-xl font-semibold">Book a Consultation</DialogTitle>
        </DialogHeader>

        <div className="flex-1 overflow-y-auto px-4 pb-4">
          <Tabs value={currentStep} className="w-full">
            <TabsList className="grid w-full grid-cols-3 mb-6 mt-4 h-auto">
              <TabsTrigger 
                value="date" 
                disabled={false}
                onClick={() => setCurrentStep('date')}
                className="flex flex-col gap-1 py-3 px-2"
              >
                <CalendarIcon className="w-4 h-4" />
                <span className="text-xs">Date</span>
              </TabsTrigger>
              <TabsTrigger 
                value="time" 
                disabled={!selectedDate}
                onClick={() => selectedDate && setCurrentStep('time')}
                className="flex flex-col gap-1 py-3 px-2"
              >
                <Clock className="w-4 h-4" />
                <span className="text-xs">Time</span>
              </TabsTrigger>
              <TabsTrigger 
                value="details" 
                disabled={!selectedDate || !selectedTime}
                onClick={() => selectedDate && selectedTime && setCurrentStep('details')}
                className="flex flex-col gap-1 py-3 px-2"
              >
                <User className="w-4 h-4" />
                <span className="text-xs">Details</span>
              </TabsTrigger>
            </TabsList>

          <TabsContent value="date" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Choose a Date</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-center w-full">
                  <Calendar
                    mode="single"
                    selected={selectedDate}
                    onSelect={handleDateSelect}
                    disabled={(date) => {
                      if (!settings) return true;
                      
                      const today = new Date();
                      const minDate = addDays(today, Math.ceil(settings.minimum_notice_hours / 24));
                      const maxDate = addDays(today, settings.advance_booking_days);
                      
                      return date < minDate || date > maxDate || !isWorkingDay(date) || isDayOff(date);
                    }}
                    className="rounded-md border w-full max-w-md"
                    classNames={{
                      months: "flex flex-col space-y-4 w-full",
                      month: "space-y-4 w-full",
                      caption: "flex justify-center pt-1 relative items-center",
                      caption_label: "text-base sm:text-lg font-medium",
                      nav: "space-x-1 flex items-center",
                      nav_button: "h-8 w-8 sm:h-10 sm:w-10 bg-transparent p-0 opacity-50 hover:opacity-100",
                      nav_button_previous: "absolute left-1",
                      nav_button_next: "absolute right-1",
                      table: "w-full border-collapse space-y-1",
                      head_row: "flex w-full",
                      head_cell: "text-muted-foreground rounded-md flex-1 h-8 sm:h-10 font-normal text-xs sm:text-sm flex items-center justify-center",
                      row: "flex w-full mt-1",
                      cell: "flex-1 h-8 sm:h-10 text-center text-xs sm:text-sm p-0 relative [&:has([aria-selected].day-range-end)]:rounded-r-md [&:has([aria-selected].day-outside)]:bg-accent/50 [&:has([aria-selected])]:bg-accent first:[&:has([aria-selected])]:rounded-l-md last:[&:has([aria-selected])]:rounded-r-md focus-within:relative focus-within:z-20",
                      day: "h-full w-full p-0 font-medium text-xs sm:text-base aria-selected:opacity-100 flex items-center justify-center rounded-md hover:bg-accent hover:text-accent-foreground",
                      day_range_end: "day-range-end",
                      day_selected: "bg-primary text-primary-foreground hover:bg-primary hover:text-primary-foreground focus:bg-primary focus:text-primary-foreground",
                      day_today: "bg-accent text-accent-foreground font-bold",
                      day_outside: "day-outside text-muted-foreground opacity-50 aria-selected:bg-accent/50 aria-selected:text-muted-foreground aria-selected:opacity-30",
                      day_disabled: "text-muted-foreground opacity-50",
                      day_range_middle: "aria-selected:bg-accent aria-selected:text-accent-foreground",
                      day_hidden: "invisible",
                    }}
                  />
                </div>
                {selectedDate && (
                  <>
                    <div className="p-3 bg-muted rounded-md">
                      <p className="text-sm">
                        <strong>Selected:</strong> {format(selectedDate, 'PPP')}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        <strong>Working Hours:</strong> {getWorkingHours(selectedDate)}
                      </p>
                    </div>
                    <div className="flex justify-end pt-4">
                      <Button
                        onClick={() => setCurrentStep('time')}
                        className="w-full sm:w-auto min-w-[100px]"
                      >
                        Next
                      </Button>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="time" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Available Time Slots</CardTitle>
                {selectedDate && (
                  <p className="text-sm text-muted-foreground">
                    {format(selectedDate, 'PPP')}
                  </p>
                )}
              </CardHeader>
              <CardContent className="space-y-4">
                {loading ? (
                  <div className="text-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
                    <p className="mt-2 text-sm text-muted-foreground">Loading available times...</p>
                  </div>
                ) : availableSlots.length === 0 ? (
                  <div className="text-center py-8">
                    <p className="text-muted-foreground">No available time slots for this date.</p>
                    <Button 
                      variant="outline" 
                      onClick={() => setCurrentStep('date')}
                      className="mt-4"
                    >
                      Choose Different Date
                    </Button>
                  </div>
                ) : (
                  <>
                    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2">
                      {availableSlots.map((slot) => (
                        <Button
                          key={slot}
                          variant={selectedTime === slot ? "default" : "outline"}
                          onClick={() => handleTimeSelect(slot)}
                          className="text-sm h-12 sm:h-10 font-medium"
                        >
                          {slot}
                        </Button>
                      ))}
                    </div>
                    <div className="flex flex-col sm:flex-row justify-between gap-3 pt-4">
                      <Button
                        variant="outline"
                        onClick={() => setCurrentStep('date')}
                        className="order-2 sm:order-1"
                      >
                        Back
                      </Button>
                      {selectedTime && (
                        <Button
                          onClick={() => setCurrentStep('details')}
                          className="order-1 sm:order-2"
                        >
                          Next
                        </Button>
                      )}
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="details" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Your Information</CardTitle>
                {selectedDate && selectedTime && (
                  <div className="text-sm text-muted-foreground">
                    <p>{format(selectedDate, 'PPP')} at {selectedTime}</p>
                    <p>Duration: {settings?.meeting_duration_minutes} minutes</p>
                  </div>
                )}
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="client_name">Full Name *</Label>
                    <div className="relative">
                      <User className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                      <Input
                        id="client_name"
                        placeholder="Your full name"
                        value={formData.client_name}
                        onChange={(e) => setFormData(prev => ({ ...prev, client_name: e.target.value }))}
                        className="pl-10"
                        required
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="client_email">Email *</Label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                      <Input
                        id="client_email"
                        type="email"
                        placeholder="your.email@example.com"
                        value={formData.client_email}
                        onChange={(e) => setFormData(prev => ({ ...prev, client_email: e.target.value }))}
                        className={`pl-10 ${monthlyBookingCheck.checked && monthlyBookingCheck.hasBooking ? 'border-destructive' : ''}`}
                        required
                      />
                    </div>
                    {monthlyBookingCheck.checked && monthlyBookingCheck.hasBooking && (
                      <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-md">
                        <p className="text-sm text-destructive">
                          <strong>Monthly Limit Reached:</strong> You already have a consultation booked for {monthlyBookingCheck.month}. 
                          Each client can only book one consultation per month.
                        </p>
                      </div>
                    )}
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="client_phone">Phone (Optional)</Label>
                  <div className="relative">
                    <Phone className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="client_phone"
                      type="tel"
                      placeholder="Your phone number"
                      value={formData.client_phone}
                      onChange={(e) => setFormData(prev => ({ ...prev, client_phone: e.target.value }))}
                      className="pl-10"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="project_details">Project Details (Optional)</Label>
                  <Textarea
                    id="project_details"
                    placeholder="Tell us about your project or what you'd like to discuss..."
                    value={formData.project_details}
                    onChange={(e) => setFormData(prev => ({ ...prev, project_details: e.target.value }))}
                    rows={3}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="message">Additional Message (Optional)</Label>
                  <div className="relative">
                    <MessageSquare className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Textarea
                      id="message"
                      placeholder="Any additional information or special requests..."
                      value={formData.message}
                      onChange={(e) => setFormData(prev => ({ ...prev, message: e.target.value }))}
                      className="pl-10 pt-10"
                      rows={3}
                    />
                  </div>
                </div>

                <div className="flex flex-col sm:flex-row gap-3 pt-4">
                  <Button
                    variant="outline"
                    onClick={() => setCurrentStep('time')}
                    className="order-2 sm:order-1"
                  >
                    Back
                  </Button>
                  <Button
                    onClick={handleSubmit}
                    disabled={
                      submitting || 
                      !formData.client_name || 
                      !formData.client_email ||
                      (monthlyBookingCheck.checked && monthlyBookingCheck.hasBooking)
                    }
                    className="flex-1 order-1 sm:order-2"
                  >
                    {submitting ? "Booking..." : "Book Consultation"}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
        </div>
      </DialogContent>
    </Dialog>
  );
}
