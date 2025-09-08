# Bus Pass Management System

*partialy done

A comprehensive, role-based web application built with Flask to manage a college's bus pass system. It handles student registration, fee payments, bus card requests, and real-time bus entry verification via QR code scanning. The system provides distinct dashboards and functionalities for different user roles: Admin, Accountant, Staff, and Student.

## Features

### Role-Based Access Control

-   **Admin**:
    -   System-wide dashboard with key metrics (total students, active cards, pending requests, fees collected).
    -   Full CRUD (Create, Read, Update, Delete) functionality for managing users (Admins, Accountants, Staff, Students).
    -   Manage bus locations, routes, and associated fees.
    -   Approve or reject student card requests (new, cancel, replace).
    -   View and manage all student profiles.
    -   Send system-wide or user-specific notifications.

-   **Accountant**:
    -   Financial dashboard with statistics on paid, pending, and overdue fees.
    -   View all student profiles with a focus on fee status.
    -   Update student fee status, dues, and fines.
    -   Track all payments and update their status (e.g., paid, failed, refunded).
    -   Generate financial reports, including fee collection by location and month.

-   **Staff**:
    -   Scan student QR codes to instantly verify bus pass and fee status.
    -   Record student bus entries with timestamps.
    -   View recent scan history and daily/weekly/monthly entry statistics.
    -   Add new students to the system.

-   **Student**:
    -   Personalized dashboard showing profile summary, card status, and recent payments.
    -   View and edit their own profile (critical changes require admin approval).
    -   Submit card requests for new, replacement, or cancellation.
    -   View payment history and make new fee payments.
    -   Receive and view notifications regarding payments, card status, and profile updates.

### Core Functionalities

-   **Authentication**: Secure user registration and login system with password hashing.
-   **QR Code Integration**: Uses `html5-qrcode` on the frontend for staff to scan and verify student passes.
-   **Dynamic Form Handling**: Robust forms with server-side validation using Flask-WTF.
-   **Database Management**: Uses SQLAlchemy ORM for structured and maintainable database interactions.
-   **Notification System**: Keeps users informed about important status changes.

## Technologies Used

-   **Backend**: Python, Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF
-   **Database**: SQLite (default for development), PostgreSQL (supported for production)
-   **Frontend**: HTML, Jinja2, CSS, JavaScript, `html5-qrcode`
-   **Deployment**: Gunicorn

## Project Structure

```
BusPassManager/
├── app.py                # Flask app factory, initialization, and config
├── main.py               # Application entry point
├── extension.py          # Flask extension initializations (db, login_manager)
├── my_models.py          # SQLAlchemy database models
├── forms.py              # WTForms form definitions
├── requirements.txt      # Python dependencies
├── package.json          # Node.js dependencies
├── routes/               # Flask Blueprints for modular routing
│   ├── __init__.py
│   ├── admin.py
│   ├── accountant.py
│   ├── auth.py
│   ├── staff.py
│   └── student.py
└── templates/            # Jinja2 HTML templates
    ├── admin/
    ├── accountant/
    ├── staff/
    ├── student/
    └── login.html        # Shared template for auth pages
```

## Setup and Installation

### Prerequisites

-   Python 3.11+
-   Node.js and npm

### Steps

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd BusPassManager
    ```

2.  **Set up the Python virtual environment:**
    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Install Node.js dependencies:**
    ```bash
    npm install
    ```

5.  **Run the application:**
    ```bash
    python main.py
    ```

6.  The application will start on `http://127.0.0.1:5000`.

## Usage

1.  Access the application in your browser at `http://127.0.0.1:5000`. You will be redirected to the login page.

2.  **Default Admin Credentials**:
    The application automatically creates a default admin user on the first run.
    -   **Username**: `admin`
    -   **Password**: `admin123`

3.  **Create Users**:
    -   Log in as the admin to access the admin dashboard.
    -   Navigate to "Manage Users" to create new accounts for Staff, Accountants, and Students.

4.  **Student Registration**:
    -   Alternatively, students can create their own accounts using the "Register" link on the login page. Their profile will be initialized, and they can then fill in their details.

## License

This project is licensed under the ISC License. See the `package.json` file for details.
