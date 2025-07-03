# Chat Bot API - Authentication System

This document describes the authentication system implemented for the Chat Bot API.

## Overview

The authentication system provides:
- User registration and login
- JWT-based authentication
- User profile management
- Admin panel for user management
- Protected chat endpoints
- Database storage for users and chat history

## Features

### Authentication
- **Registration**: Users can register with email and password
- **Login**: JWT token-based authentication
- **Token Refresh**: Refresh tokens for extended sessions
- **Password Management**: Change password functionality
- **User Profiles**: Full name, email, and profile management

### Authorization
- **Role-based Access**: Regular users and administrators
- **Protected Endpoints**: Chat endpoints require authentication
- **Admin Panel**: Admin-only routes for user management

### Database
- **SQLite**: Default database (configurable)
- **Async Support**: SQLAlchemy with async support
- **Models**: User, ChatSession, ChatMessage
- **Migrations**: Automatic table creation

## API Endpoints

### Authentication Endpoints

#### Register User
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword",
  "full_name": "John Doe"
}
```

#### Login
```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=securepassword
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### Get Current User
```http
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

#### Update Profile
```http
PUT /api/v1/auth/me
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "full_name": "John Smith"
}
```

#### Change Password
```http
POST /api/v1/auth/change-password
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "current_password": "oldpassword",
  "new_password": "newpassword"
}
```

### Chat Endpoints (Protected)

#### Send Chat Message
```http
POST /api/v1/chat
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "message": "Hello, how can you help me?",
  "conversation_id": "optional-conversation-id"
}
```

### Admin Endpoints

#### Dashboard Statistics
```http
GET /api/v1/admin/dashboard
Authorization: Bearer <admin_access_token>
```

#### Get All Users
```http
GET /api/v1/admin/users?skip=0&limit=100&search=john&is_active=true
Authorization: Bearer <admin_access_token>
```

#### Get User Details
```http
GET /api/v1/admin/users/{user_id}
Authorization: Bearer <admin_access_token>
```

#### Toggle User Status
```http
POST /api/v1/admin/users/{user_id}/toggle-status
Authorization: Bearer <admin_access_token>
```

#### Make User Admin
```http
POST /api/v1/admin/users/{user_id}/make-admin
Authorization: Bearer <admin_access_token>
```

#### Get User Chat History
```http
GET /api/v1/admin/users/{user_id}/chat-history
Authorization: Bearer <admin_access_token>
```

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Database
DATABASE_URL=sqlite+aiosqlite:///./chatbot.db

# Authentication
SECRET_KEY=your-super-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Admin Account
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=admin123

# LLM
OPENAI_API_KEY=your-openai-api-key
```

### Database Setup

The database is automatically initialized on startup with:
- Table creation
- Default admin user creation

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Run the application:
```bash
uvicorn app.main:app --reload
```

## Default Admin Account

A default admin account is created on first startup:
- **Email**: admin@example.com (configurable)
- **Password**: admin123 (configurable)
- **Role**: Administrator

**Important**: Change the default admin credentials in production!

## Security Features

- **Password Hashing**: bcrypt with salt
- **JWT Tokens**: Secure token-based authentication
- **Token Expiration**: Configurable token lifetimes
- **Role-based Access**: Admin and user roles
- **Input Validation**: Pydantic models for request validation
- **SQL Injection Protection**: SQLAlchemy ORM

## Database Schema

### Users Table
- `id`: Primary key
- `email`: Unique email address
- `hashed_password`: bcrypt hashed password
- `full_name`: User's full name
- `is_active`: Account status
- `is_admin`: Admin privileges
- `created_at`: Registration timestamp
- `updated_at`: Last update timestamp
- `last_login`: Last login timestamp

### Chat Sessions Table
- `id`: Primary key
- `user_id`: Foreign key to users
- `title`: Session title
- `created_at`: Session start time
- `updated_at`: Last activity time

### Chat Messages Table
- `id`: Primary key
- `session_id`: Foreign key to chat sessions
- `content`: Message content
- `role`: Message role (user/assistant)
- `created_at`: Message timestamp

## Error Handling

The API returns standard HTTP status codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `500`: Internal Server Error

Error responses include detailed messages:
```json
{
  "detail": "Error description"
}
```

## Testing

Use the interactive API documentation at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Production Deployment

1. **Change Secret Key**: Generate a secure secret key
2. **Database**: Use PostgreSQL or MySQL for production
3. **Environment**: Set `DEBUG=false`
4. **HTTPS**: Use HTTPS in production
5. **Admin Credentials**: Change default admin password
6. **CORS**: Configure appropriate CORS origins

## Troubleshooting

### Common Issues

1. **Database Connection**: Check DATABASE_URL format
2. **Token Errors**: Verify SECRET_KEY configuration
3. **Admin Access**: Ensure user has `is_admin=true`
4. **CORS Issues**: Check BACKEND_CORS_ORIGINS setting

### Logs

Check application logs for detailed error information:
```bash
tail -f logs/app.log
```