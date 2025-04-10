# Healthcare System - Microservice Architecture

## Overview

This is a healthcare system built using a microservice architecture with Django and Docker. The system is designed to manage various aspects of healthcare operations including patient management, appointment scheduling, medical records, pharmacy, billing, and laboratory services.

## System Architecture

The system is composed of the following microservices:

1. **Auth Service** - Handles user authentication and authorization
2. **User Service** - Manages user profiles and information
3. **Medical Record Service** - Manages electronic health records (EHR)
4. **Appointment Service** - Handles appointment scheduling
5. **Pharmacy Service** - Manages prescriptions and pharmacy inventory
6. **Billing Service** - Handles billing and insurance processing
7. **Laboratory Service** - Manages medical tests and reports
8. **Notification Service** - Handles email and SMS notifications

## User Roles

The system supports the following user roles:

- Patient
- Doctor
- Nurse
- Administrator
- Pharmacist
- Insurance Provider
- Laboratory Technician

## Features

- User Authentication & Authorization
- Electronic Health Records (EHR) Management
- Appointment Scheduling
- Billing & Insurance Processing
- Prescription & Pharmacy Management
- Medical Test & Report Management
- Notification & Communication (email, SMS alerts)

## Technology Stack

- **Backend**: Django, Django REST Framework
- **Database**: PostgreSQL
- **Caching & Message Broker**: Redis
- **API Gateway**: Nginx
- **Containerization**: Docker, Docker Compose
- **Authentication**: JWT (JSON Web Tokens)
- **Documentation**: Swagger/OpenAPI

## Getting Started

### Prerequisites

- Docker and Docker Compose

### Installation

1. Clone the repository
2. Run the following command to start all services:

```bash
docker-compose up -d
```

3. Access the API at `http://localhost/api/`
4. Access the API documentation at `http://localhost/api/auth/swagger/`

## Development

Each microservice follows a similar structure:

```
service-name/
├── Dockerfile
├── requirements.txt
├── manage.py
├── core/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── app/
    ├── __init__.py
    ├── models.py
    ├── serializers.py
    ├── views.py
    └── tests.py
```

To add a new feature to a service, follow these steps:

1. Create models in the appropriate service
2. Create serializers for the models
3. Create views and endpoints
4. Update the service's URLs
5. Test the new feature

## API Documentation

Each service provides its own Swagger documentation at `/swagger/` endpoint.

## License

This project is licensed under the MIT License.
