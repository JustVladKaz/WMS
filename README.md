# Warehouse Management System (WMS)

![Alt text](https://imgur.com/a/MSBclSN)

### Authors

- Khoja Rinas  
- Kazarin Vladislav Alekseevich  
- Mohammed Abdelhafiz Salem Abdelha

<br>

The Warehouse Management System (WMS) is a web-based Django application designed to streamline warehouse operations by managing inventory, orders, and reporting in real-time. This system implements role-based access (administrators and employees) to ensure that only authorized personnel can perform critical actions such as editing products or finalizing orders. WMS aims to reduce manual errors, improve stock accuracy, and provide timely insights through low-stock alerts and sales reports.


## Table of Contents
1. [Key Features](#key-features)
2. [Technical Specifications](#technical-specifications)
3. [Installation and Setup](#installation-and-setup)
4. [Usage Guide](#usage-guide)
5. [Project Structure](#project-structure)
6. [Security Measures](#security-measures)
7. [Future Improvements](#future-improvements)
8. [License](#license)



## Key Features

- **Role-Based Access**  
  - **Administrator**: Full control over product management, order processing, reports, and user administration.  
  - **Employee**: Can view product details, place orders, and cancel pending orders.

- **Inventory Management**  
  - Add, edit, or remove products with advanced search and filter capabilities.  
  - Automatic stock updates upon order placement or cancellation.

- **Order Processing**  
  - Place orders for available products (quantity check enforced).  
  - Administrators can complete or cancel orders with real-time stock adjustments.

- **Reporting**  
  - **Low Stock Report**: Quickly identify products with stock of 5 or fewer.  
  - **Sales Report**: Summaries of daily sales. Auto-generation of the daily report at 23:59 if not manually generated.

- **Non-Functional Requirements**  
  - **Dependability**: Consistent, error-free operations with input validation and database constraints.  
  - **Performance**: Quick order processing and report generation.  
  - **Scalability**: Easy upgrade from SQLite to MySQL/PostgreSQL with potential for advanced features.  
  - **Usability**: Intuitive interface with clear dashboards and tooltips.



## Technical Specifications

- **Framework & Language**  
  - **Backend**: Django (Python)  
  - **Frontend**: HTML, CSS, and Django templates  
  - **Database**: SQLite (upgradable to MySQL/PostgreSQL via `settings.py` modifications)

- **Models**  
  - **User**: Manages login credentials and roles (admin, employee).  
  - **Product**: Contains product details including name, quantity, and price.  
  - **Order**: Tracks product orders with quantity, status (pending, completed, canceled), and timestamps.  
  - **Report**: Stores daily sales and low-stock reports.

- **Security & Validation**  
  - Uses Django’s built-in authentication system with hashed passwords.  
  - CSRF protection is enabled on all forms.  
  - Django ORM prevents SQL injection, and output auto-escaping prevents XSS.

- **Logging & Debugging**  
  - Django’s logging system captures errors and user activities for effective debugging.

---

## Installation and Setup

Follow these steps to set up the project locally:

1. **Check Python Installation**  
   Verify that Python is installed:
   ```bash
   python --version
   # or
   python3 --version
2. **Clone or Download the Project**  
   Either clone the repository or unzip the project folder:
   ```bash
    git clone https://github.com/yourusername/WMS.git
    cd WMS
3. **Create and Activate a Virtual Environment**  
   Create a virtual environment:
   ```bash
    python -m venv env
    ```
	For Linux/Mac:
   ```bash
    source env/bin/activate
    ```
    For Windows:
   ```bash
    env\Scripts\activate
    ```

    You should see (env) in your terminal indicating activation.

4. **Install Dependencies**  
Install required packages:
    ```bash
    pip install -r requirements.txt
5. **Apply Migrations & Setup Database**  
Set up the database:
    ```bash
    python manage.py migrate
6. **Run the Development Server**  
Start the server:
    ```bash
    python manage.py runserver
Access the application at http://127.0.0.1:8000/.

<br>

# Usage Guide

## 1. Login
- Access the login page at `[your_localhost_address]/login/`.
- Use provided credentials or create new users via the admin panel.
- **Example credentials:**
  - **Admin:** `admin013 / AdminAdmin#013`
  - **Employee:** `employee01 / HNfzAf3BzmXWIK0`
  - **Employee:** `employee02 / XWIK0zmHNfzAf3B`

## 2. Employee Functionality
- **View Products:** Browse the product list with advanced search features.
- **Place Orders:** Submit orders with quantity checks ensuring stock availability.
- **Cancel Orders:** Cancel pending orders before administrative confirmation.

## 3. Administrator Functionality
- **Dashboard:** Monitor quick stats like pending orders, low stock, and daily revenue.
- **Manage Products:** Add, edit, or delete products.
- **Manage Orders:** View all orders and perform actions such as canceling or completing them.
- **Generate Reports:**
  - **Low Stock Report:** Identifies items at or below the stock threshold.
  - **Sales Report:** Generate summaries of daily sales manually or rely on auto-generation at `23:59`.

## 4. Logout
- Always log out after finishing your tasks to secure your session.

<br><br>

# Project Structure

```
WMS/
├── db.sqlite3
├── README.md
├── requirements.txt
├── manage.py
├── wms/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── ...
├── apps/
│   ├── products/
│   │   ├── models.py
│   │   ├── views.py
│   │   └── ...
│   ├── orders/
│   │   ├── models.py
│   │   ├── views.py
│   │   └── ...
│   ├── reports/
│   │   ├── models.py
│   │   ├── views.py
│   │   └── ...
│   └── users/
│       ├── models.py
│       ├── views.py
│       └── ...
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   └── ...
└── static/
    ├── css/
    ├── js/
    └── ...
```

<br><br>

# Security Measures

### 1. Hashed Passwords
- No plain-text storage; Django’s User model handles secure hashing.

### 2. CSRF Tokens
- All forms include CSRF tokens, mitigating cross-site request forgery attacks.

### 3. XSS & SQL Injection Protection
- Using Django’s template engine for output escaping.
- ORM usage avoids raw SQL queries.

### 4. Access Control
- Decorators (e.g., `@login_required`) ensure only authenticated users can access specific views.
- Role checks (admin vs. employee) to restrict unauthorized actions.

# Security Measures

### 1. Hashed Passwords
- No plain-text storage; Django’s User model handles secure hashing.

### 2. CSRF Tokens
- All forms include CSRF tokens, mitigating cross-site request forgery attacks.

### 3. XSS & SQL Injection Protection
- Using Django’s template engine for output escaping.
- ORM usage avoids raw SQL queries.

### 4. Access Control
- Decorators (e.g., `@login_required`) ensure only authenticated users can access specific views.
- Role checks (admin vs. employee) to restrict unauthorized actions.

<br><br>

# Future Improvements

### API Integration
- Incorporate Django REST Framework for external services or third-party integrations.

### Advanced Notifications
- Email or SMS alerts for low stock or critical orders.

### Automated Testing
- Expand unit and integration tests using pytest or Django’s test suite.

### Multi-Warehouse Support
- Add features to handle multiple warehouse locations within a single application instance.

