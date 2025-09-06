import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Calendar } from "lucide-react";
import BookingModal from "./BookingModal";

interface BookConsultantButtonProps {
  variant?: "default" | "outline" | "secondary";
  size?: "default" | "sm" | "lg";
  className?: string;
}

export default function BookConsultantButton({
  variant = "default",
  size = "default",
  className = ""
}: BookConsultantButtonProps) {
  const [showBookingModal, setShowBookingModal] = useState(false);

  return (
    <>
      <Button
        variant={variant}
        size={size}
        className={className}
        onClick={() => setShowBookingModal(true)}
      >
        <Calendar className="mr-2 h-4 w-4" />
        Book a Consultation
      </Button>
      
      <BookingModal
        open={showBookingModal}
        onOpenChange={setShowBookingModal}
      />
    </>
  );
}
