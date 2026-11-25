# QR Attendance System
Python web application implementing US-01 through US-15 from the supplied story map and stories. English responsive UI; SQLite persists data automatically. Python 3.11–3.13 recommended.

## Windows setup (PowerShell)
```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```
Open http://127.0.0.1:8000. On the first start, the terminal prints a randomly generated administrator password. Email: admin@example.com. Alternatively set `$env:ADMIN_PASSWORD = 'YourStrongPassword123!'` before first start. The database is created in the project directory. Keep it private; deleting it erases records. Admin creates instructor accounts; students register themselves or are created by admin. The role is never self-selected during public registration.

## Demo
1. Admin creates an instructor account.
2. Register a student with a unique student ID; sign in as instructor in a separate browser profile/private window.
3. Create a course, enroll the student, start a timed session.
4. Download the QR image. Sign in as student in the other browser and upload it or capture it with a camera. Submit attendance.
5. Try submitting again, end the session, check history, submit a correction, and export a CSV as instructor.

## Tests
Install the optional test dependency: `python -m pip install httpx` and run `python -m unittest -v test_app`. The test uses a temporary database and does not change live data. The included test-results.txt records the integration run.

## Scope and limitations
Local educational application, not a production security certification. Camera capture requires localhost or HTTPS and permission; image upload works without camera. To use across devices, run `python -m uvicorn app:app --host 0.0.0.0 --port 8000` on a trusted LAN and use the computer's LAN IP; use HTTPS for browser camera and set HTTPS_ONLY=1 for secure cookies. Do not expose directly to the internet: production requires TLS, rate limiting, upload limits at proxy, backups, password recovery and operational monitoring. Static QR tokens can be shared during their validity period; physical presence is not guaranteed. Sessions use UTC. Public registration is student-only, instructor creation is admin-controlled. Current enrollment is used for historical reporting, so late enrollment can show earlier sessions; historical enrollment snapshots are not implemented. Physical webcam and multiple real devices have not been tested in this environment.Project documentation update.
