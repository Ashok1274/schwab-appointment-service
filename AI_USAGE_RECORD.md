# AI Usage and Verification Record

## 1. AI Tool Used

ChatGPT was used as a development assistant and technical reference during selected stages of the project.

## 2. Areas of AI Assistance

### 2.1 Code Development 

**Prompt Summary:** Explore implementation approaches for booking, concurrency handling and some code implementation.



**AI Response Summary:** AI suggested checking for overlapping active appointments, protecting booking operations against simultaneous conflicting requests and some code development.



**Review and Decision:** The suggestions were reviewed against the existing project structure, models, requirements, and Python environment. Relevant code suggestions were adapted to fit the existing service structure, imports, method integration, and tests rather than being used as a complete solution.



**Decision:** Suggestions were accepted with modifications where required for project integration.



**Files Influenced:**

- `app/service.py`
- `tests/test_service.py`

**Verification:** The integrated implementation was executed locally and tested for valid bookings, invalid inputs, overlap rejection, cancellation, and duplicate identifiers.

### 2.2 Technical Analysis

AI was used to understand technical concepts and evaluate whether suggested approaches were suitable for the project.



**Prompt Summaries and AI Response Summaries:**

| Topic explored                  | AI response summary                                                                                                                 | Decision                                |
| ------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------- |
| Appointment overlap detection   | Explained the interval comparison needed to reject overlapping active appointments for the same provider.                           | Accepted                               |
| Half-open intervals             | Explained how adjacent appointments can be allowed without treating them as overlapping.                                            | Accepted                                |
| Race conditions                 | Explained how simultaneous booking requests could both pass a conflict check if checking and insertion were not protected together. | Accepted                                |
| `threading.RLock`               | Explained how a lock protects critical sections within a process.                                                                   | Adapted to the in-memory implementation |
| Storage and locking limitations | Explained that in-memory data is not persistent and process-local locks do not coordinate separate application processes.           | Accepted and documented                 |

**Files and Decisions Influenced:**

- `tests/test_service.py` – boundary and concurrency test cases.


### 2.3 Test Review and Verification

**Prompt Summary:** Review the appointment service behavior and identify additional edge cases that should be covered by automated tests.



**AI Response Summary:** Suggested reviewing invalid timestamps, non-positive durations, missing identifiers, duplicate IDs, cancellation behavior, different overlap arrangements, and concurrent booking attempts.



**Review and Decision:** Relevant test suggestions were incorporated into the test suite and aligned with the implemented service behavior.



**Decision:** Suggestions were accepted or adapted according to the assessment requirements.



**Files Influenced:**

- `tests/test_service.py`

**Verification:** The full test suite was executed locally using `python -m pytest -v`.



**Latest test result: 24 passed.**

### 2.4 Documentation Preparation

AI assistance was used to draft and refine Markdown documentation, including:

- `README.md`
- `DESIGN_SPECIFICATION.md`
- `AI_USAGE_RECORD.md`

**Prompt Summary:** Prepare and refine documentation explaining project setup, implementation design, booking invariants, assumptions, technical decisions, and limitations.



**AI Response Summary:** Suggested documentation structure and wording for describing the service boundary, setup instructions, concurrency approach, and known limitations.



**Review and Decision:** The suggested content was reviewed and edited to reflect the actual implementation and avoid documenting unsupported functionality.



**Decision:** Relevant documentation suggestions were accepted with edits.



**Files Influenced:**

- `README.md`
- `DESIGN_SPECIFICATION.md`
- `AI_USAGE_RECORD.md`

**Verification:** Documentation was checked against the implemented code, test commands, and actual project limitations.

## 3. Reflection and Independent Review

AI assistance helped accelerate selected coding tasks and provided explanations of technical concepts. The suggestions were not treated as automatically correct or as a complete project solution.



The development process involved evaluating whether suggested approaches addressed the assessment requirements, understanding why particular technical decisions were appropriate, identifying necessary integration changes, and checking the resulting behavior through local testing.



The final implementation uses in-memory storage and process-local locking. It does not provide persistence across application restarts or coordination across multiple processes or application servers.


