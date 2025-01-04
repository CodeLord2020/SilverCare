# Silvercare - Elderly Assistance Platform

Silvercare is a web-based platform designed to connect elderly individuals with helpers for various tasks and assistance needs. Built using Django's MVT architecture, the platform facilitates task posting, helper applications, and secure communication between users.

## Live Demo
Visit our site: [https://silvercare.onrender.com/](https://silvercare.onrender.com/)

## Features

### User Authentication & Management
- User registration with email verification
- Secure login system
- Password reset functionality
- Password change capability
- Profile management
- User role management (Elderly users & Helpers)

### Task Management
- Task creation and posting by elderly users
- Detailed task descriptions and requirements
- Task categories and priority levels
- Task status tracking (Open, In Progress, Completed)
- Task search functionality
- Advanced filtering options
  - By location
  - By task type
  - By status
  - By date range

### Helper Applications
- Easy application process for helpers
- Application status tracking
- Application history
- Helper profile with experience and skills

### Review System
- Post-task completion ratings
- Detailed review submissions
- Rating history for helpers
- Overall rating calculation
- Public review display on profiles

### Communication System
- Real-time messaging between users
- Status Notifications

## Technical Stack

- **Backend**: Django 4.2+
- **Frontend**: 
  - HTML5
  - CSS3
  - JavaScript
  - Bootstrap 5
- **Database**: SQLite (Development) / PostgreSQL (Production)
- **Real-time Features**: Django Channels
- **Additional Libraries**:
  - django-crispy-forms
  - django-cloudinary-storage
  - django-widget-tweaks
  - django-admin-rangefilter
  - django-phonenumber-field
  - django-import-export
  - channels
  - Whitenoise
  - Redis

## Installation

### Prerequisites
- Python 3.8+
- pip
- Virtual environment (recommended)

### Local Development Setup

1. Clone the repository:
```bash
git clone https://github.com/CodeLord2020/SilverCare
cd silvercare
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

6. Create superuser:
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

### Production Deployment

Additional steps for production:

1. Update `settings.py`:
   - Set `DEBUG = False`
   - Configure `ALLOWED_HOSTS`
   - Set up proper email backend
   - Configure static files

2. Set up PostgreSQL database
3. Configure HTTPS
4. Set up Redis for Channels (real-time features)


## Testing

Run the test suite:
```bash
python manage.py test
```

## Security Features
- CSRF protection
- XSS prevention
- Secure password hashing
- Session security
- Form validation
- Input sanitization

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/CodeLord2020/SilverCare/blob/main/LICENSE) file for details.

## Contact

Adebayo Rasheed - [rasheedbabatunde76@gmail.com](mailto:rasheedbabatunde76@gmail.com)

Project Link: [https://github.com/CodeLord2020/SilverCare](https://github.com/CodeLord2020/SilverCare)

