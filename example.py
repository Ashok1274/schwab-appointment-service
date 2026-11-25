
from datetime import datetime, timezone

from app.service import AppointmentService, BookingConflictError


service = AppointmentService()

start = datetime(2026, 11, 26, 10, 0, tzinfo=timezone.utc)
end = datetime(2026, 11, 26, 11, 0, tzinfo=timezone.utc)

appointment = service.book_appointment(
    appointment_id="A101",
    provider_id="P101",
    start_time=start,
    end_time=end
)

print("Booking successful:", appointment.appointment_id)

try:
    service.book_appointment(
        appointment_id="A102",
        provider_id="P101",
        start_time=datetime(2026, 11, 26, 10, 30, tzinfo=timezone.utc),
        end_time=datetime(2026, 11, 26, 11, 30, tzinfo=timezone.utc)
    )
except BookingConflictError as error:
    print("Booking rejected:", error)

print(service.cancel_appointment("A101"))
