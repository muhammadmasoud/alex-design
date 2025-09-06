import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from "@/components/ui/table";
import { Switch } from "@/components/ui/switch";
import { 
  Settings, 
  Plus, 
  Edit, 
  Trash2, 
  Calendar as CalendarIcon, 
  Clock, 
  Mail,
  Phone,
  CheckCircle,
  XCircle,
  AlertCircle
} from "lucide-react";
import { format } from "date-fns";
import { toast } from "@/hooks/use-toast";
import { api, endpoints } from "@/lib/api";
import { 
  ConsultationSettings, 
  DayOff, 
  Booking 
} from "@/types";

interface ConsultationManagementProps {
  onUpdate: () => void;
}

export default function ConsultationManagement({ onUpdate }: ConsultationManagementProps) {
  const [activeTab, setActiveTab] = useState("bookings");
  const [settings, setSettings] = useState<ConsultationSettings | null>(null);
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [daysOff, setDaysOff] = useState<DayOff[]>([]);
  const [loading, setLoading] = useState(false);
  const [editingSettings, setEditingSettings] = useState(false);
  const [newDayOff, setNewDayOff] = useState({ date: '', reason: '' });
  const [addingDayOff, setAddingDayOff] = useState(false);
  const [dayOffDialogOpen, setDayOffDialogOpen] = useState(false);
  const [cancelDialogOpen, setCancelDialogOpen] = useState(false);
  const [selectedBooking, setSelectedBooking] = useState<Booking | null>(null);
  const [cancellationReason, setCancellationReason] = useState('');

  useEffect(() => {
    fetchSettings();
    fetchBookings();
    fetchDaysOff();
  }, []);

  const fetchSettings = async () => {
    try {
      const response = await api.get(endpoints.admin.consultationSettings);
      setSettings(response.data.results?.[0] || response.data);
    } catch (error: any) {
      console.error('Error fetching consultation settings:', error);
      toast({
        title: "Error",
        description: "Failed to load consultation settings",
        variant: "destructive",
      });
    }
  };

  const fetchBookings = async () => {
    try {
      setLoading(true);
      const response = await api.get(endpoints.admin.bookings);
      setBookings(response.data.results || response.data);
    } catch (error: any) {
      console.error('Error fetching bookings:', error);
      toast({
        title: "Error",
        description: "Failed to load bookings",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchDaysOff = async () => {
    try {
      console.log('Fetching days off from:', endpoints.admin.daysOff);
      const response = await api.get(endpoints.admin.daysOff);
      console.log('Days off response:', response.data);
      setDaysOff(response.data.results || response.data);
    } catch (error: any) {
      console.error('Error fetching days off:', error);
      console.error('Error response:', error.response?.data);
      toast({
        title: "Error",
        description: "Failed to load days off",
        variant: "destructive",
      });
    }
  };

  const updateSettings = async (updatedSettings: ConsultationSettings) => {
    try {
      const response = await api.post(endpoints.admin.consultationSettings, updatedSettings);
      setSettings(response.data);
      setEditingSettings(false);
      toast({
        title: "Success",
        description: "Consultation settings updated successfully",
      });
      onUpdate();
    } catch (error: any) {
      console.error('Error updating settings:', error);
      toast({
        title: "Error",
        description: "Failed to update consultation settings",
        variant: "destructive",
      });
    }
  };

  const updateBookingStatus = async (bookingId: number, status: string, reason?: string) => {
    try {
      const payload: any = { status };
      if (reason) {
        payload.cancellation_reason = reason;
      }
      
      await api.post(`${endpoints.admin.bookings}${bookingId}/update_status/`, payload);
      fetchBookings();
      toast({
        title: "Success",
        description: "Booking status updated successfully",
      });
      onUpdate();
    } catch (error: any) {
      console.error('Error updating booking status:', error);
      toast({
        title: "Error",
        description: "Failed to update booking status",
        variant: "destructive",
      });
    }
  };

  const addDayOff = async () => {
    console.log('Add Day Off called with:', newDayOff);
    
    if (!newDayOff.date) {
      toast({
        title: "Error",
        description: "Please select a date",
        variant: "destructive",
      });
      return;
    }

    try {
      setAddingDayOff(true);
      console.log('Making API call to:', endpoints.admin.daysOff);
      const response = await api.post(endpoints.admin.daysOff, newDayOff);
      console.log('API response:', response.data);
      
      fetchDaysOff();
      setNewDayOff({ date: '', reason: '' });
      setDayOffDialogOpen(false);
      toast({
        title: "Success",
        description: "Day off added successfully",
      });
      onUpdate();
    } catch (error: any) {
      console.error('Error adding day off:', error);
      console.error('Error response:', error.response?.data);
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to add day off",
        variant: "destructive",
      });
    } finally {
      setAddingDayOff(false);
    }
  };

  const deleteDayOff = async (dayOffId: number) => {
    try {
      await api.delete(`${endpoints.admin.daysOff}${dayOffId}/`);
      fetchDaysOff();
      toast({
        title: "Success",
        description: "Day off removed successfully",
      });
      onUpdate();
    } catch (error: any) {
      console.error('Error deleting day off:', error);
      toast({
        title: "Error",
        description: "Failed to remove day off",
        variant: "destructive",
      });
    }
  };

  const handleCancelBooking = (booking: Booking) => {
    setSelectedBooking(booking);
    setCancellationReason('');
    setCancelDialogOpen(true);
  };

  const confirmCancelBooking = async () => {
    if (!selectedBooking) return;
    
    await updateBookingStatus(selectedBooking.id!, 'cancelled', cancellationReason);
    setCancelDialogOpen(false);
    setSelectedBooking(null);
    setCancellationReason('');
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'pending':
        return <Badge variant="outline" className="text-yellow-700 border-yellow-700"><AlertCircle className="w-3 h-3 mr-1" />Pending</Badge>;
      case 'confirmed':
        return <Badge variant="outline" className="text-green-700 border-green-700"><CheckCircle className="w-3 h-3 mr-1" />Confirmed</Badge>;
      case 'cancelled':
        return <Badge variant="outline" className="text-red-700 border-red-700"><XCircle className="w-3 h-3 mr-1" />Cancelled</Badge>;
      case 'completed':
        return <Badge variant="outline" className="text-blue-700 border-blue-700"><CheckCircle className="w-3 h-3 mr-1" />Completed</Badge>;
      case 'no_show':
        return <Badge variant="outline" className="text-gray-700 border-gray-700"><XCircle className="w-3 h-3 mr-1" />No Show</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Consultation Management</CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="bookings">
                <CalendarIcon className="w-4 h-4 mr-2" />
                Bookings
              </TabsTrigger>
              <TabsTrigger value="schedule">
                <Clock className="w-4 h-4 mr-2" />
                Schedule
              </TabsTrigger>
              <TabsTrigger value="settings">
                <Settings className="w-4 h-4 mr-2" />
                Settings
              </TabsTrigger>
            </TabsList>

            <TabsContent value="bookings" className="space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-semibold">Recent Bookings</h3>
                <Button onClick={fetchBookings} variant="outline" size="sm">
                  Refresh
                </Button>
              </div>
              
              {loading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
                  <p className="mt-2 text-sm text-muted-foreground">Loading bookings...</p>
                </div>
              ) : bookings.length === 0 ? (
                <div className="text-center py-8">
                  <CalendarIcon className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                  <p className="text-muted-foreground">No bookings found</p>
                </div>
              ) : (
                <div className="border rounded-lg">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Client</TableHead>
                        <TableHead>Date & Time</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {bookings.map((booking) => (
                        <TableRow key={booking.id}>
                          <TableCell>
                            <div>
                              <p className="font-medium">{booking.client_name}</p>
                              <p className="text-sm text-muted-foreground flex items-center">
                                <Mail className="w-3 h-3 mr-1" />
                                {booking.client_email}
                              </p>
                              {booking.client_phone && (
                                <p className="text-sm text-muted-foreground flex items-center">
                                  <Phone className="w-3 h-3 mr-1" />
                                  {booking.client_phone}
                                </p>
                              )}
                            </div>
                          </TableCell>
                          <TableCell>
                            <div>
                              <p className="font-medium">{format(new Date(booking.date), 'PPP')}</p>
                              <p className="text-sm text-muted-foreground">
                                {booking.time} - {booking.end_time} ({booking.duration_minutes} min)
                              </p>
                            </div>
                          </TableCell>
                          <TableCell>
                            {getStatusBadge(booking.status || 'pending')}
                          </TableCell>
                          <TableCell>
                            <div className="flex gap-2">
                              {booking.status === 'pending' && (
                                <>
                                  <Button
                                    size="sm"
                                    onClick={() => updateBookingStatus(booking.id!, 'confirmed')}
                                  >
                                    Confirm
                                  </Button>
                                  <Button
                                    size="sm"
                                    variant="outline"
                                    onClick={() => handleCancelBooking(booking)}
                                  >
                                    Cancel
                                  </Button>
                                </>
                              )}
                              {booking.status === 'confirmed' && !booking.is_past && (
                                <>
                                  <Button
                                    size="sm"
                                    variant="outline"
                                    onClick={() => updateBookingStatus(booking.id!, 'completed')}
                                  >
                                    Mark Complete
                                  </Button>
                                  <Button
                                    size="sm"
                                    variant="destructive"
                                    onClick={() => handleCancelBooking(booking)}
                                  >
                                    Cancel
                                  </Button>
                                </>
                              )}
                            </div>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              )}
            </TabsContent>

            <TabsContent value="schedule" className="space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-semibold">Days Off</h3>
                <Dialog open={dayOffDialogOpen} onOpenChange={setDayOffDialogOpen}>
                  <DialogTrigger asChild>
                    <Button>
                      <Plus className="w-4 h-4 mr-2" />
                      Add Day Off
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Add Day Off</DialogTitle>
                    </DialogHeader>
                    <div className="space-y-4">
                      <div>
                        <Label htmlFor="dayoff-date">Date</Label>
                        <Input
                          id="dayoff-date"
                          type="date"
                          value={newDayOff.date}
                          onChange={(e) => setNewDayOff(prev => ({ ...prev, date: e.target.value }))}
                          min={new Date().toISOString().split('T')[0]}
                        />
                      </div>
                      <div>
                        <Label htmlFor="dayoff-reason">Reason (Optional)</Label>
                        <Input
                          id="dayoff-reason"
                          placeholder="Holiday, Personal, etc."
                          value={newDayOff.reason}
                          onChange={(e) => setNewDayOff(prev => ({ ...prev, reason: e.target.value }))}
                        />
                      </div>
                      <Button onClick={addDayOff} disabled={addingDayOff} className="w-full">
                        {addingDayOff ? "Adding..." : "Add Day Off"}
                      </Button>
                    </div>
                  </DialogContent>
                </Dialog>
              </div>

              <div className="grid gap-4">
                {daysOff.map((dayOff) => (
                  <Card key={dayOff.id}>
                    <CardContent className="flex justify-between items-center p-4">
                      <div>
                        <p className="font-medium">{format(new Date(dayOff.date), 'PPP')}</p>
                        {dayOff.reason && (
                          <p className="text-sm text-muted-foreground">{dayOff.reason}</p>
                        )}
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => deleteDayOff(dayOff.id!)}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </TabsContent>

            <TabsContent value="settings" className="space-y-4">
              {settings && (
                <Card>
                  <CardHeader>
                    <div className="flex justify-between items-center">
                      <CardTitle>Consultation Settings</CardTitle>
                      <Button
                        variant="outline"
                        onClick={() => setEditingSettings(!editingSettings)}
                      >
                        <Edit className="w-4 h-4 mr-2" />
                        {editingSettings ? 'Cancel' : 'Edit'}
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    {editingSettings ? (
                      <SettingsForm
                        settings={settings}
                        onSave={updateSettings}
                        onCancel={() => setEditingSettings(false)}
                      />
                    ) : (
                      <SettingsDisplay settings={settings} />
                    )}
                  </CardContent>
                </Card>
              )}
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Cancellation Dialog */}
      <Dialog open={cancelDialogOpen} onOpenChange={setCancelDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Cancel Consultation</DialogTitle>
          </DialogHeader>
          {selectedBooking && (
            <div className="space-y-4">
              <div className="p-4 bg-muted rounded-lg">
                <p className="font-medium">{selectedBooking.client_name}</p>
                <p className="text-sm text-muted-foreground">
                  {format(new Date(selectedBooking.date), 'PPP')} at {selectedBooking.time}
                </p>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="cancellation-reason">Reason for Cancellation</Label>
                <p className="text-sm text-muted-foreground">
                  This message will be sent to the client via email
                </p>
                <Textarea
                  id="cancellation-reason"
                  placeholder="Please explain why the consultation needs to be cancelled..."
                  value={cancellationReason}
                  onChange={(e) => setCancellationReason(e.target.value)}
                  rows={4}
                />
              </div>

              <div className="flex gap-2">
                <Button
                  variant="destructive"
                  onClick={confirmCancelBooking}
                  className="flex-1"
                >
                  Cancel Consultation
                </Button>
                <Button
                  variant="outline"
                  onClick={() => setCancelDialogOpen(false)}
                  className="flex-1"
                >
                  Keep Consultation
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}

function SettingsDisplay({ settings }: { settings: ConsultationSettings }) {
  return (
    <div className="grid grid-cols-2 gap-6">
      <div className="space-y-4">
        <div>
          <Label className="text-sm font-medium">Booking Status</Label>
          <p className="text-sm">{settings.booking_enabled ? 'Enabled' : 'Disabled'}</p>
        </div>
        <div>
          <Label className="text-sm font-medium">Meeting Duration</Label>
          <p className="text-sm">{settings.meeting_duration_minutes} minutes</p>
        </div>
        <div>
          <Label className="text-sm font-medium">Buffer Time</Label>
          <p className="text-sm">{settings.buffer_time_minutes} minutes</p>
        </div>
        <div>
          <Label className="text-sm font-medium">Advance Booking</Label>
          <p className="text-sm">{settings.advance_booking_days} days</p>
        </div>
        <div>
          <Label className="text-sm font-medium">Minimum Notice</Label>
          <p className="text-sm">{settings.minimum_notice_hours} hours</p>
        </div>
      </div>
      <div className="space-y-4">
        <div>
          <Label className="text-sm font-medium">Working Hours</Label>
          <div className="text-sm space-y-1">
            <p>Monday: {settings.monday_hours || 'Day off'}</p>
            <p>Tuesday: {settings.tuesday_hours || 'Day off'}</p>
            <p>Wednesday: {settings.wednesday_hours || 'Day off'}</p>
            <p>Thursday: {settings.thursday_hours || 'Day off'}</p>
            <p>Friday: {settings.friday_hours || 'Day off'}</p>
            <p>Saturday: {settings.saturday_hours || 'Day off'}</p>
            <p>Sunday: {settings.sunday_hours || 'Day off'}</p>
          </div>
        </div>
      </div>
    </div>
  );
}

function SettingsForm({ 
  settings, 
  onSave, 
  onCancel 
}: { 
  settings: ConsultationSettings;
  onSave: (settings: ConsultationSettings) => void;
  onCancel: () => void;
}) {
  const [formData, setFormData] = useState<ConsultationSettings>(settings);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData);
  };

  const durationOptions = [
    { value: 15, label: "15 minutes (Quick chat)" },
    { value: 30, label: "30 minutes (Standard)" },
    { value: 45, label: "45 minutes (Detailed)" },
    { value: 60, label: "1 hour (Comprehensive)" },
    { value: 90, label: "1.5 hours (Extended)" },
    { value: 120, label: "2 hours (Full session)" }
  ];

  const bufferOptions = [
    { value: 0, label: "No buffer" },
    { value: 5, label: "5 minutes" },
    { value: 10, label: "10 minutes" },
    { value: 15, label: "15 minutes" },
    { value: 30, label: "30 minutes" }
  ];

  const noticeOptions = [
    { value: 2, label: "2 hours (Same day)" },
    { value: 12, label: "12 hours (Half day)" },
    { value: 24, label: "24 hours (1 day)" },
    { value: 48, label: "48 hours (2 days)" },
    { value: 72, label: "72 hours (3 days)" },
    { value: 168, label: "1 week" }
  ];

  const advanceOptions = [
    { value: 7, label: "1 week ahead" },
    { value: 14, label: "2 weeks ahead" },
    { value: 30, label: "1 month ahead" },
    { value: 60, label: "2 months ahead" },
    { value: 90, label: "3 months ahead" },
    { value: 180, label: "6 months ahead" }
  ];

  const timeSlots = [
    "08:00-12:00", "08:00-16:00", "08:00-17:00", "08:00-18:00",
    "09:00-13:00", "09:00-17:00", "09:00-18:00", "09:00-19:00",
    "10:00-14:00", "10:00-16:00", "10:00-18:00", "10:00-19:00",
    "11:00-15:00", "11:00-17:00", "11:00-19:00", "11:00-20:00",
    "12:00-16:00", "12:00-20:00", "13:00-17:00", "14:00-18:00"
  ];

  const updateWorkingHours = (day: string, hours: string) => {
    setFormData(prev => ({ ...prev, [`${day}_hours`]: hours }));
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-8">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left Column - Basic Settings */}
        <div className="space-y-6">
          <div className="space-y-4">
            <h3 className="text-lg font-medium">Basic Settings</h3>
            
            {/* Booking Status Toggle */}
            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div>
                <Label className="text-base font-medium">Booking System</Label>
                <p className="text-sm text-muted-foreground">
                  {formData.booking_enabled ? "Clients can book consultations online" : "Booking system is disabled"}
                </p>
              </div>
              <Switch
                checked={formData.booking_enabled}
                onCheckedChange={(checked) => setFormData(prev => ({ ...prev, booking_enabled: checked }))}
              />
            </div>

            {/* Meeting Duration */}
            <div className="space-y-3">
              <Label className="text-base font-medium">Meeting Duration</Label>
              <Select
                value={formData.meeting_duration_minutes.toString()}
                onValueChange={(value) => setFormData(prev => ({ ...prev, meeting_duration_minutes: parseInt(value) }))}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {durationOptions.map(option => (
                    <SelectItem key={option.value} value={option.value.toString()}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Buffer Time */}
            <div className="space-y-3">
              <Label className="text-base font-medium">Buffer Time Between Meetings</Label>
              <p className="text-sm text-muted-foreground">Time gap between consecutive bookings</p>
              <Select
                value={formData.buffer_time_minutes.toString()}
                onValueChange={(value) => setFormData(prev => ({ ...prev, buffer_time_minutes: parseInt(value) }))}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {bufferOptions.map(option => (
                    <SelectItem key={option.value} value={option.value.toString()}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Advance Booking */}
            <div className="space-y-3">
              <Label className="text-base font-medium">How Far in Advance</Label>
              <p className="text-sm text-muted-foreground">Maximum booking window</p>
              <Select
                value={formData.advance_booking_days.toString()}
                onValueChange={(value) => setFormData(prev => ({ ...prev, advance_booking_days: parseInt(value) }))}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {advanceOptions.map(option => (
                    <SelectItem key={option.value} value={option.value.toString()}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Minimum Notice */}
            <div className="space-y-3">
              <Label className="text-base font-medium">Minimum Notice Required</Label>
              <p className="text-sm text-muted-foreground">How early clients must book</p>
              <Select
                value={formData.minimum_notice_hours.toString()}
                onValueChange={(value) => setFormData(prev => ({ ...prev, minimum_notice_hours: parseInt(value) }))}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {noticeOptions.map(option => (
                    <SelectItem key={option.value} value={option.value.toString()}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>

        {/* Right Column - Working Hours */}
        <div className="space-y-6">
          <h3 className="text-lg font-medium">Working Hours</h3>
          <p className="text-sm text-muted-foreground">Set your availability for each day of the week</p>
          
          <div className="space-y-4">
            {[
              { key: 'monday', label: 'Monday', icon: '📅' },
              { key: 'tuesday', label: 'Tuesday', icon: '📅' },
              { key: 'wednesday', label: 'Wednesday', icon: '📅' },
              { key: 'thursday', label: 'Thursday', icon: '📅' },
              { key: 'friday', label: 'Friday', icon: '📅' },
              { key: 'saturday', label: 'Saturday', icon: '🎯' },
              { key: 'sunday', label: 'Sunday', icon: '🏖️' },
            ].map(({ key, label, icon }) => {
              const currentValue = (formData as any)[`${key}_hours`] || '';
              const isWorking = Boolean(currentValue);

              return (
                <div key={key} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center space-x-3">
                    <span className="text-lg">{icon}</span>
                    <div>
                      <Label className="font-medium">{label}</Label>
                      <p className="text-sm text-muted-foreground">
                        {isWorking ? currentValue : "Day off"}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Switch
                      checked={isWorking}
                      onCheckedChange={(checked) => {
                        updateWorkingHours(key, checked ? "09:00-17:00" : "");
                      }}
                    />
                    {isWorking && (
                      <Select
                        value={currentValue}
                        onValueChange={(value) => updateWorkingHours(key, value)}
                      >
                        <SelectTrigger className="w-32">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {timeSlots.map(slot => (
                            <SelectItem key={slot} value={slot}>
                              {slot}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      <div className="flex gap-3 pt-6 border-t">
        <Button type="submit" className="flex-1">
          <Settings className="w-4 h-4 mr-2" />
          Save Settings
        </Button>
        <Button type="button" variant="outline" onClick={onCancel} className="flex-1">
          Cancel
        </Button>
      </div>
    </form>
  );
}
