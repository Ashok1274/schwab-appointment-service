# Appointment Booking Service

A minimal Python appointment-booking service that prevents overlapping active appointments for the same provider and supports cancellation.

## 1. Features

- Book appointments for providers.
- Prevent overlapping active appointments for the same provider.
- Allow adjacent appointments.
- Allow different providers to book at the same time.
- Cancel existing appointments.
- Validate appointment identifiers, timestamps and durations.
- Normalize appointment and provider IDs by removing leading and trailing whitespace.
- Use UTC timestamps.
- Protect booking and cancellation operations against concurrent threads within one process using `threading.RLock`.
- Store appointments in an in-memory dictionary.

## 2. Project Structure

```text
schwab-appointment-service/
│
├── app/
│   ├── __init__.py
│   ├── models.py
│   └── service.py
│
├── tests/
│   └── test_service.py
│
├── DESIGN_SPECIFICATION.md
├── AI_USAGE_RECORD.md
├── README.md
├── requirements.txt
└── .gitignore
```

## 3. Requirements

- Python 3
- pip
- pytest

## 4. Setup Instructions

Clone or download the project and open its root directory.

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it.

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Windows CMD:

```cmd
.venv\Scripts\activate.bat
```

Mac/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## 5. Run Automated Tests

Execute:

```bash
python -m pytest -v
```

The test suite contains 24 tests covering successful booking, overlap rejection, adjacent appointments, different providers, cancellation, invalid inputs, identifier normalization and concurrent booking attempts.

Latest local test result:

**24 passed**

## 6. Booking Invariant

A provider cannot have two overlapping active appointments.

The overlap condition is:

```python
new_start < existing_end and new_end > existing_start
```

Appointments use start-inclusive and end-exclusive intervals. Therefore, adjacent appointments are allowed.

Cancelled appointments do not block future bookings. Appointment IDs remain reserved after cancellation.

## 7. Time Handling

All appointment timestamps must be timezone-aware UTC datetime values.

Naive timestamps and timestamps with non-zero UTC offsets are rejected.

## 8. Storage and Concurrency

Appointments are stored in an in-memory Python dictionary.

A process-local `threading.RLock` protects the booking check-and-insert operation and cancellation operation. This prevents concurrent threads using the same service instance from creating overlapping active appointments.

The lock does not provide coordination across multiple processes or application servers.

Data is not persistent and will be lost when the process terminates.

A production implementation would require durable storage and database-level atomic conflict prevention.

## 9. Documentation

See:

- `DESIGN_SPECIFICATION.md` for architecture, assumptions, booking invariant, concurrency behavior and limitations.
- `AI_USAGE_RECORD.md` for AI assistance, decisions and verification information.