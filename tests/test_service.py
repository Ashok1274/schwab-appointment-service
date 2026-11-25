
import pytest
from datetime import datetime, timezone, timedelta

from app.service import (
    AppointmentService,
    InvalidAppointmentError,
    BookingConflictError,
)
from app.models import AppointmentStatus


def make_time(hour, minute=0):
    return datetime(
        2026, 11, 26, hour, minute,
        tzinfo=timezone.utc
    )


def test_successful_booking():
    service = AppointmentService()

    appointment = service.book_appointment(
        "A101", "P101", make_time(10), make_time(11)
    )

    assert appointment.appointment_id == "A101"
    assert appointment.provider_id == "P101"
    assert appointment.status == AppointmentStatus.ACTIVE


def test_same_provider_overlap_is_rejected():
    service = AppointmentService()

    service.book_appointment(
        "A101", "P101", make_time(10), make_time(11)
    )

    with pytest.raises(BookingConflictError):
        service.book_appointment(
            "A102", "P101", make_time(10, 30), make_time(11, 30)
        )

    assert len(service.appointments) == 1


def test_adjacent_appointments_are_allowed():
    service = AppointmentService()

    service.book_appointment(
        "A101", "P101", make_time(10), make_time(11)
    )

    service.book_appointment(
        "A102", "P101", make_time(11), make_time(12)
    )

    assert len(service.appointments) == 2


def test_different_providers_can_book_same_time():
    service = AppointmentService()

    service.book_appointment(
        "A101", "P101", make_time(10), make_time(11)
    )

    service.book_appointment(
        "A102", "P102", make_time(10), make_time(11)
    )

    assert len(service.appointments) == 2


def test_cancelled_appointment_does_not_block_booking():
    service = AppointmentService()

    service.book_appointment(
        "A101", "P101", make_time(10), make_time(11)
    )

    result = service.cancel_appointment("A101")

    assert result == "Appointment cancelled successfully."

    service.book_appointment(
        "A102", "P101", make_time(10), make_time(11)
    )

    assert len(service.appointments) == 2
    assert service.appointments["A101"].status == AppointmentStatus.CANCELLED


def test_cancelling_missing_appointment():
    service = AppointmentService()

    result = service.cancel_appointment("UNKNOWN")

    assert result == "Appointment not found."
    assert len(service.appointments) == 0


def test_cancelling_already_cancelled_appointment():
    service = AppointmentService()

    service.book_appointment(
        "A101", "P101", make_time(10), make_time(11)
    )

    service.cancel_appointment("A101")
    result = service.cancel_appointment("A101")

    assert result == "Appointment is already cancelled."


@pytest.mark.parametrize("appointment_id,provider_id", [
    ("", "P101"),
    ("A101", ""),
    ("   ", "P101"),
    ("A101", "   "),
])
def test_missing_identifiers_are_rejected(
    appointment_id, provider_id
):
    service = AppointmentService()

    with pytest.raises(InvalidAppointmentError):
        service.book_appointment(
            appointment_id,
            provider_id,
            make_time(10),
            make_time(11)
        )

    assert len(service.appointments) == 0


def test_invalid_timestamp_type_is_rejected():
    service = AppointmentService()

    with pytest.raises(InvalidAppointmentError):
        service.book_appointment(
            "A101", "P101", "2026-11-26 10:00",
            make_time(11)
        )

    assert len(service.appointments) == 0


def test_naive_timestamp_is_rejected():
    service = AppointmentService()

    naive_time = datetime(2026, 11, 26, 10, 0)

    with pytest.raises(InvalidAppointmentError):
        service.book_appointment(
            "A101", "P101", naive_time, make_time(11)
        )

    assert len(service.appointments) == 0


def test_non_utc_timestamp_is_rejected():
    service = AppointmentService()

    india_time = timezone(timedelta(hours=5, minutes=30))

    start = datetime(2026, 11, 26, 10, 0, tzinfo=india_time)
    end = datetime(2026, 11, 26, 11, 0, tzinfo=india_time)

    with pytest.raises(InvalidAppointmentError):
        service.book_appointment("A101", "P101", start, end)

    assert len(service.appointments) == 0


@pytest.mark.parametrize("start_hour,end_hour", [
    (10, 10),
    (11, 10),
])
def test_non_positive_duration_is_rejected(
    start_hour, end_hour
):
    service = AppointmentService()

    with pytest.raises(InvalidAppointmentError):
        service.book_appointment(
            "A101", "P101",
            make_time(start_hour),
            make_time(end_hour)
        )

    assert len(service.appointments) == 0


def test_duplicate_appointment_id_is_rejected():
    service = AppointmentService()

    service.book_appointment(
        "A101", "P101", make_time(10), make_time(11)
    )

    with pytest.raises(InvalidAppointmentError):
        service.book_appointment(
            "A101", "P102", make_time(12), make_time(13)
        )

    assert len(service.appointments) == 1


def test_new_appointment_starts_before_existing_and_overlaps():
    service = AppointmentService()

    service.book_appointment(
        "A101", "P101", make_time(10), make_time(11)
    )

    with pytest.raises(BookingConflictError):
        service.book_appointment(
            "A102", "P101", make_time(9), make_time(10, 30)
        )

    assert len(service.appointments) == 1


def test_new_appointment_fully_contains_existing():
    service = AppointmentService()

    service.book_appointment(
        "A101", "P101", make_time(10), make_time(11)
    )

    with pytest.raises(BookingConflictError):
        service.book_appointment(
            "A102", "P101", make_time(9), make_time(12)
        )

    assert len(service.appointments) == 1


def test_cancelled_appointment_id_cannot_be_reused():
    service = AppointmentService()

    service.book_appointment(
        "A101", "P101", make_time(10), make_time(11)
    )
    service.cancel_appointment("A101")

    with pytest.raises(InvalidAppointmentError):
        service.book_appointment(
            "A101", "P101", make_time(12), make_time(13)
        )

    assert len(service.appointments) == 1


def test_failed_cancellation_does_not_change_existing_data():
    service = AppointmentService()

    original = service.book_appointment(
        "A101", "P101", make_time(10), make_time(11)
    )

    result = service.cancel_appointment("UNKNOWN")

    assert result == "Appointment not found."
    assert len(service.appointments) == 1
    assert service.appointments["A101"] is original
    assert original.status == AppointmentStatus.ACTIVE


def test_whitespace_around_ids_is_normalized():
    service = AppointmentService()

    appointment = service.book_appointment(
        " A101 ", " P101 ", make_time(10), make_time(11)
    )

    assert appointment.appointment_id == "A101"
    assert appointment.provider_id == "P101"
    assert "A101" in service.appointments


def test_concurrent_overlapping_bookings_only_one_succeeds():
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    service = AppointmentService()
    barrier = Barrier(2)

    def attempt_booking(appointment_id):
        barrier.wait()

        try:
            service.book_appointment(
                appointment_id,
                "P101",
                make_time(10),
                make_time(11),
            )
            return "success"
        except BookingConflictError:
            return "conflict"

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(
            executor.map(
                attempt_booking,
                ["A101", "A102"],
            )
        )

    assert results.count("success") == 1
    assert results.count("conflict") == 1
    assert len(service.appointments) == 1


def test_new_appointment_starts_inside_existing_and_ends_after():
    service = AppointmentService()

    service.book_appointment(
        "A101", "P101", make_time(10), make_time(11)
    )

    with pytest.raises(BookingConflictError):
        service.book_appointment(
            "A102", "P101", make_time(10, 30), make_time(12)
        )
    assert len(service.appointments) == 1
