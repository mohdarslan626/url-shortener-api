# URL Shortener API

A production-ready URL Shortener API built with **Django** and **Django REST Framework**. The application allows users to create short URLs, generate custom aliases, track click analytics, generate QR codes, and manage their own URLs securely using JWT authentication.

## Features

- JWT Authentication
- User Registration & Login
- URL Shortening
- Custom Alias
- URL Expiration
- QR Code Generation
- Click Analytics
- User Dashboard
- Search URLs
- Ordering
- Pagination
- Object-Level Permissions

## Tech Stack

* Python
* Django
* Django REST Framework
* SQLite (Development)
* JWT Authentication (Simple JWT)
* Pillow & QRCode
* VS Code REST Client (API Testing)

## API Testing

This project includes an `api.http` file for testing all endpoints using the **REST Client** extension in Visual Studio Code.

### Setup

1. Install the **REST Client** extension in VS Code.
2. Start the Django development server:

   ```bash
   python manage.py runserver
   ```
3. Open the `api.http` file.
4. Register a new user.
5. Login to receive an **Access Token**.
6. Replace `YOUR_ACCESS_TOKEN_HERE` with the generated access token.
7. Click **Send Request** to test the available API endpoints.

## Available Endpoints

* Register User
* Login
* Refresh Access Token
* Create Short URL
* Redirect to Original URL
* Get URL Analytics
* Get My URLs

## Future Improvements

* Object-level permissions
* Update & Delete URLs
* Dashboard statistics
* Redis caching
* Swagger/OpenAPI documentation
* Docker support
* CI/CD with GitHub Actions
* Production deployment
