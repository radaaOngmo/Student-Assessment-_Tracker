# Student Assessment Tracker

A Python Tkinter desktop application using SQLite, with a Bhutan-inspired maroon, gold, and ivory interface.

## Run

1. Install Python 3.10 or newer.
2. Open this folder in VS Code.
3. Install the image dependency for profile pictures:

   ```powershell
   python -m pip install -r requirements.txt
   ```

4. In the terminal, run:

   ```powershell
   python main.py
   ```

Tkinter and SQLite are included with standard Windows Python installations. Pillow is listed in requirements.txt so users can choose and preview PNG/JPEG profile pictures. Keep the `assets` folder alongside the Python files.

## Accounts

You can create a student account from the sign-in screen. Passwords are masked by default; click the eye-style control next to a password field to show or hide the text.

A demonstration administrator and student are created on first run:

- Administrator: `admin` / `Admin123!`
- Student: `student` / `Student123!`

Change or remove demo credentials before using the application with real personal information. Public registration creates student accounts only; administrator accounts can manage user accounts.

## Features

- Account registration and sign-in with salted PBKDF2 password hashes
- Per-user task isolation
- Add, view, search, update, delete, and complete tasks
- Low, Medium, and High priority levels
- Pending, In Progress, and Completed statuses
- Validated optional due dates, dashboard statistics, and priority/status visual summaries
- Completed Tasks page filtered by the actual task status
- Small Samtse College of Education logo and Bhutan-inspired maroon, gold, and ivory styling
- Local image assets stored in the `assets` folder
- Administrator user management
- Settings to edit full name, change password after current-password verification, and select a local PNG/JPEG profile picture
- SQLite persistent storage in `student_assessment_tracker.db`

## Troubleshooting

- Run `python main.py` from this project folder so the `components` and `interfaces` packages can be imported.
- If a dashboard fails to open, the application displays the exception details. Copy the full message from the dialog or terminal when requesting help.
- Keep `student_assessment_tracker.db` when updating the Python files if you want to preserve registered accounts and tasks.
