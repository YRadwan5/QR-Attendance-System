# QR Attendance System — User Stories

## Project Actors
- Administrator
- Instructor
- Student

## US-01 — Sign In

**Epic:** Account Management

**User Story:** As a registered user, I want to sign in using my credentials so that I can securely access my dashboard.

### Scenario 1: Successful Login
- Given the user has a registered account
- When the user enters valid credentials
- Then the system displays the appropriate dashboard.

### Scenario 2: Invalid Login
- Given the user is on the login page
- When the user enters an incorrect password
- Then the system rejects the login attempt and displays an error message.

## US-02 — Create Course

**Epic:** Course Management

**User Story:** As an instructor, I want to create a course so that I can manage student attendance.

### Scenario 1: Successful Course Creation
- Given the instructor is authenticated
- When the instructor enters a valid course name and unique course code
- Then the course is created and displayed in the instructor's dashboard.

### Scenario 2: Duplicate Course Code
- Given a course code already exists
- When the instructor attempts to create another course using that code
- Then the system rejects the request.

## US-03 — Enroll Students

**Epic:** Course Management

**User Story:** As an instructor, I want to enroll students in my courses so that they can participate in attendance sessions.

### Scenario 1: Successful Enrollment
- Given a registered student and an existing course
- When the instructor enters the student's ID
- Then the student is added to the course roster.

### Scenario 2: Duplicate Enrollment
- Given the student is already enrolled in the course
- When the instructor attempts to enroll the student again
- Then the system rejects the duplicate enrollment.

## US-04 — Create Attendance Session

**Epic:** QR Session Management

**User Story:** As an instructor, I want to create a timed attendance session so that students can register their attendance during a lecture.

### Scenario 1: Valid Session
- Given the instructor owns an existing course
- When the instructor creates a session with a valid duration
- Then the system creates an active attendance session.

### Scenario 2: Invalid Duration
- Given the instructor is creating a session
- When the instructor enters a duration outside the allowed range of 1–180 minutes
- Then the system rejects the request.

## US-05 — Generate Session QR Code

**Epic:** QR Session Management

**User Story:** As an instructor, I want to generate a unique QR code so that students can access an attendance session.

### Scenario 1: Generate QR Code
- Given an attendance session is active
- When the instructor views the session
- Then the system displays a downloadable QR code.

### Scenario 2: Expired Session
- Given an attendance session has expired
- When the instructor requests its QR code
- Then the system denies access to the expired QR code.

## US-06 — Scan QR Code

**Epic:** QR Session Management

**User Story:** As a student, I want to scan or upload a QR code so that I can submit my attendance.

### Scenario 1: Valid QR Image
- Given the student is enrolled in the course and the session is active
- When the student submits a valid session QR image
- Then the system reads the code and records attendance.

### Scenario 2: Invalid QR Image
- Given the student is on the attendance page
- When the student uploads an image without a readable QR code
- Then the system displays an error and does not record attendance.

## Additional User Stories

**US-07 — Validate Student and Session**

As a student, I want the system to validate my enrollment and session so that only authorized attendance is accepted.

**US-08 — Record Attendance**

As a student, I want my attendance to be recorded so that my participation is documented.

**US-09 — View Attendance History**

As a student, I want to view my attendance history so that I can review my attendance status.

**US-10 — View Class Roster**

As an instructor, I want to view enrolled students so that I can manage my class.

**US-11 — Prevent Duplicate Check-in**

As an instructor, I want duplicate attendance submissions to be prevented so that attendance records remain accurate.

**US-12 — Export Attendance Report**

As an instructor, I want to export attendance reports as CSV files so that I can review and analyze attendance records.

**US-13 — View and Edit Profile**

As a registered user, I want to view and update my profile name so that my account information remains accurate.

**US-14 — Request Attendance Correction**

As a student, I want to request correction of an absent attendance record for a completed session so that attendance errors can be reviewed by my instructor.

**US-15 — Register Account**

As a student, I want to create an account so that I can access the attendance system.