# Appointment Booking Service – Design Specification

## 1. Objective

Build a bounded appointment-booking service that prevents overlapping active appointments for the same provider and supports appointment cancellation.

The implementation focuses on booking correctness, input validation, understandable code and focused automated tests. It does not attempt to build a complete scheduling product.

## 2. Scope

### Included

- Create an appointment.
- Validate appointment identifiers and timestamps.
- Normalize identifiers by removing leading and trailing whitespace.
- Reject non-positive appointment durations.
- Detect overlapping active appointments for the same provider.
- Allow adjacent appointments.
- Allow appointments for different providers at the same time.
- Cancel existing appointments.
- Return clear results for missing or already-cancelled appointments.
- Protect booking and cancellation operations against concurrent threads within one process.
- Automated tests for the required and additional edge-case scenarios.

### Excluded

- Frontend
- Authentication and authorization
- Notifications
- Recurring appointments
- Calendar integration
- External database
- Deployment

## 3. Service Boundary

The implementation has two main components:

- **Appointment model:** Represents appointment information and its status.
- **Appointment service:** Handles validation, conflict detection, booking and cancellation.

The service uses an in-memory Python dictionary as its storage mechanism.

## 4. Data Model

Each appointment contains:

| Field | Type | Description |
|---|---|---|
| appointment_id | string | Unique appointment identifier |
| provider_id | string | Provider identifier |
| start_time | datetime | Appointment start timestamp |
| end_time | datetime | Appointment end timestamp |
| status | AppointmentStatus | ACTIVE or CANCELLED |

New appointments default to ACTIVE status.

Appointment IDs remain reserved after cancellation and cannot be reused.

## 5. Booking Invariant

A provider must not have two overlapping active appointments.

Two intervals overlap when:

`new_start < existing_end and new_end > existing_start`

The comparison uses strict inequalities. Therefore, appointments that meet exactly at an endpoint are considered adjacent, not overlapping.

The conflict check only considers appointments belonging to the same provider and excludes cancelled appointments.

## 6. Booking Workflow

1. Receive appointment ID, provider ID, start time and end time.
2. Validate that both identifiers are non-empty strings.
3. Normalize identifiers by removing leading and trailing whitespace.
4. Validate that timestamps are datetime objects with UTC offsets of zero.
5. Reject an end time that is earlier than or equal to the start time.
6. Acquire the service lock.
7. Reject duplicate appointment IDs.
8. Check for overlapping active appointments for the same provider.
9. Create and store the appointment only after all checks pass.
10. Release the lock and return the created appointment.

Invalid input or a booking conflict raises a clear exception. No appointment is stored for a failed booking.

The duplicate check, conflict check and insertion are protected by the same lock so that concurrent booking threads cannot interleave these operations.

## 7. Cancellation Workflow

1. Receive an appointment ID.
2. Validate and normalize the identifier.
3. Acquire the service lock.
4. Look up the appointment.
5. If it does not exist, return an appointment-not-found result.
6. If it is already cancelled, return an already-cancelled result.
7. Otherwise, change its status to CANCELLED.
8. Release the lock and return the result.

Cancelled appointments are ignored during future conflict checks.

## 8. Persistence and Concurrency

The implementation uses a Python dictionary keyed by appointment ID.

This approach is appropriate for the minimal prototype permitted when no starter project is supplied.

The service uses Python's `threading.RLock` to protect booking and cancellation operations within a single Python process. For booking, duplicate-ID checking, conflict detection and insertion happen inside the same critical section. This protects threads using the same service instance from interleaving these operations. The lock does not coordinate separate processes or application servers.

Data is stored only in memory and is lost when the process terminates. There are no database transactions or durable persistence guarantees.

For a production system, conflict detection and insertion should be performed atomically using an appropriate database transaction and concurrency-control strategy.

## 9. Time Handling and Assumptions

- Appointment timestamps must be Python datetime values with a UTC offset of zero.
- Naive timestamps are rejected.
- Non-UTC offset timestamps are rejected.
- Appointment intervals use start-inclusive and end-exclusive semantics.
- Appointment IDs must be unique and remain reserved after cancellation.
- Leading and trailing whitespace is removed from appointment and provider IDs.
- Only ACTIVE appointments block a provider's time.
- Cancellation changes status rather than deleting the appointment.

## 10. Testing Strategy

Automated tests use pytest.

The test suite contains 23 tests and covers:

- Successful booking.
- Same-provider overlap rejection.
- Adjacent appointment acceptance.
- Different-provider booking at the same time.
- Cancellation and subsequent rebooking.
- Cancellation of missing appointments.
- Repeated cancellation.
- Missing or blank identifiers.
- Invalid timestamp types.
- Naive timestamps.
- Non-UTC timestamps.
- Zero and negative durations.
- Duplicate appointment IDs.
- Overlap when a new appointment starts before an existing appointment.
- Overlap when a new appointment fully contains an existing appointment.
- Prevention of reusing a cancelled appointment ID.
- No data changes after a failed cancellation.
- Identifier whitespace normalization.
- Concurrent overlapping booking attempts, verifying that only one succeeds.

The local test command is:

`python -m pytest -v`

The latest local test run completed successfully with **23 passed**.

## 11. Limitations and Follow-up Risks

- In-memory data is not persistent.
- The lock protects threads within one service instance and one process only.
- There is no coordination across multiple processes or servers.
- There is no HTTP API or user interface.
- No authentication or authorization is implemented.
- There is no audit history or external monitoring.

A production implementation would require durable persistence, database-level atomic conflict prevention, authentication and authorization, audit logging, monitoring and operational error handling.

## 12. Conclusion

The implementation provides the requested booking-conflict and cancellation functionality within the assessment's bounded scope. The booking invariant is enforced through validation, overlap checks and process-local locking. The 23 automated tests cover the required scenarios, additional edge cases and concurrent booking attempts.