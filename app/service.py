
from datetime import datetime, timezone
from threading import RLock

from app.models import Appointment, AppointmentStatus


class InvalidAppointmentError(ValueError):
    """Raised when appointment details are invalid."""


class BookingConflictError(ValueError):
    """Raised when a provider already has an overlapping appointment."""


class AppointmentService:
    def __init__(self):
        self.appointments = {}
        self._lock = RLock()

    def _validate_appointment(
        self, appointment_id, provider_id, start_time, end_time
    ):
        if not isinstance(appointment_id, str) or not appointment_id.strip():
            raise InvalidAppointmentError("Appointment ID is required.")

        if not isinstance(provider_id, str) or not provider_id.strip():
            raise InvalidAppointmentError("Provider ID is required.")

        if not isinstance(start_time, datetime):
            raise InvalidAppointmentError("Start time must be a datetime.")

        if not isinstance(end_time, datetime):
            raise InvalidAppointmentError("End time must be a datetime.")

        if start_time.utcoffset() != timezone.utc.utcoffset(start_time):
            raise InvalidAppointmentError("Start time must be in UTC.")

        if end_time.utcoffset() != timezone.utc.utcoffset(end_time):
            raise InvalidAppointmentError("End time must be in UTC.")

        if end_time <= start_time:
            raise InvalidAppointmentError(
                "End time must be later than start time."
            )

    def _has_conflict(self, provider_id, new_start, new_end):
        for appointment in self.appointments.values():
            if appointment.status == AppointmentStatus.CANCELLED:
                continue

            if appointment.provider_id != provider_id:
                continue

           
            if (
                new_start < appointment.end_time
                and new_end > appointment.start_time
            ):
                return True

        return False

    def book_appointment(
        self, appointment_id, provider_id, start_time, end_time
    ):
        self._validate_appointment(
            appointment_id, provider_id, start_time, end_time
        )

      
        appointment_id = appointment_id.strip()
        provider_id = provider_id.strip()

    
        with self._lock:
            if appointment_id in self.appointments:
                raise InvalidAppointmentError(
                    "Appointment ID already exists."
                )

            if self._has_conflict(provider_id, start_time, end_time):
                raise BookingConflictError(
                    "Provider already has an overlapping appointment."
                )

            appointment = Appointment(
                appointment_id=appointment_id,
                provider_id=provider_id,
                start_time=start_time,
                end_time=end_time,
            )

            self.appointments[appointment_id] = appointment
            return appointment

    def cancel_appointment(self, appointment_id):
        if not isinstance(appointment_id, str) or not appointment_id.strip():
            raise InvalidAppointmentError("Appointment ID is required.")

        appointment_id = appointment_id.strip()

        with self._lock:
            appointment = self.appointments.get(appointment_id)

            if appointment is None:
                return "Appointment not found."

            if appointment.status == AppointmentStatus.CANCELLED:
                return "Appointment is already cancelled."

            appointment.status = AppointmentStatus.CANCELLED
            return "Appointment cancelled successfully."
