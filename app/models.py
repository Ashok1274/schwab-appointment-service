
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class AppointmentStatus(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"


@dataclass
class Appointment:
    appointment_id: str
    provider_id: str
    start_time: datetime
    end_time: datetime
    status: AppointmentStatus = AppointmentStatus.ACTIVE
