# Authentication API Documentation

The Authentication Service provides user management, authentication, and authorization functionality for the Chat Bot System.

## Base URL

```
http://localhost:8001/api/v1/auth
```

## Authentication

Most endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Endpoints

### User Registration

**POST** `/register`

Register a new user account.

#### Request Body

```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

#### Response

**Status: 201 Created**

```json
{
  "id": 1,
  "uuid": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_admin": false,
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z",
  "last_login": null,
  "avatar_url": null,
  "bio": null,
  "phone": null
}
```

#### Error Responses

**Status: 400 Bad Request**
```json
{
  "detail": "Email already registered"
}
```

**Status: 422 Unprocessable Entity**
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### User Login

**POST** `/login`

Authenticate user and receive access tokens.

#### Request Body

```json
{
  "username": "user@example.com",
  "password": "securepassword123"
}
```

#### Response

**Status: 200 OK**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### Error Responses

**Status: 401 Unauthorized**
```json
{
  "detail": "Incorrect email or password"
}
```

### Token Refresh

**POST** `/refresh`

Refresh access token using refresh token.

#### Request Body

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Response

**Status: 200 OK**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Get Current User

**GET** `/me`

Get current authenticated user information.

#### Headers

```
Authorization: Bearer <access-token>
```

#### Response

**Status: 200 OK**

```json
{
  "id": 1,
  "uuid": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_admin": false,
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z",
  "last_login": "2024-01-01T12:30:00Z",
  "avatar_url": "https://example.com/avatar.jpg",
  "bio": "Software developer",
  "phone": "+1234567890"
}
```

### Update User Profile

**PUT** `/profile`

Update current user's profile information.

#### Headers

```
Authorization: Bearer <access-token>
```

#### Request Body

```json
{
  "full_name": "John Smith",
  "bio": "Senior Software Developer",
  "phone": "+1234567890",
  "avatar_url": "https://example.com/new-avatar.jpg"
}
```

#### Response

**Status: 200 OK**

```json
{
  "id": 1,
  "uuid": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "full_name": "John Smith",
  "is_active": true,
  "is_admin": false,
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T13:00:00Z",
  "last_login": "2024-01-01T12:30:00Z",
  "avatar_url": "https://example.com/new-avatar.jpg",
  "bio": "Senior Software Developer",
  "phone": "+1234567890"
}
```

### Change Password

**PUT** `/password`

Change current user's password.

#### Headers

```
Authorization: Bearer <access-token>
```

#### Request Body

```json
{
  "current_password": "oldpassword123",
  "new_password": "newpassword456"
}
```

#### Response

**Status: 200 OK**

```json
{
  "message": "Password updated successfully"
}
```

#### Error Responses

**Status: 400 Bad Request**
```json
{
  "detail": "Current password is incorrect"
}
```

### Logout

**POST** `/logout`

Logout user and invalidate tokens.

#### Headers

```
Authorization: Bearer <access-token>
```

#### Response

**Status: 200 OK**

```json
{
  "message": "Successfully logged out"
}
```

## Admin Endpoints

The following endpoints require admin privileges (`is_admin: true`).

### List All Users

**GET** `/admin/users`

Get paginated list of all users.

#### Headers

```
Authorization: Bearer <admin-access-token>
```

#### Query Parameters

- `page` (optional): Page number (default: 1)
- `size` (optional): Page size (default: 20)
- `search` (optional): Search term for email or name
- `is_active` (optional): Filter by active status

#### Response

**Status: 200 OK**

```json
{
  "users": [
    {
      "id": 1,
      "uuid": "123e4567-e89b-12d3-a456-426614174000",
      "email": "user@example.com",
      "full_name": "John Doe",
      "is_active": true,
      "is_admin": false,
      "created_at": "2024-01-01T12:00:00Z",
      "updated_at": "2024-01-01T12:00:00Z",
      "last_login": "2024-01-01T12:30:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "size": 20,
  "pages": 1
}
```

### Get User by ID

**GET** `/admin/users/{user_id}`

Get specific user information.

#### Headers

```
Authorization: Bearer <admin-access-token>
```

#### Response

**Status: 200 OK**

```json
{
  "id": 1,
  "uuid": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_admin": false,
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z",
  "last_login": "2024-01-01T12:30:00Z",
  "avatar_url": null,
  "bio": null,
  "phone": null
}
```

### Update User

**PUT** `/admin/users/{user_id}`

Update user information (admin only).

#### Headers

```
Authorization: Bearer <admin-access-token>
```

#### Request Body

```json
{
  "full_name": "Updated Name",
  "is_active": true,
  "is_admin": false
}
```

#### Response

**Status: 200 OK**

```json
{
  "id": 1,
  "uuid": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "full_name": "Updated Name",
  "is_active": true,
  "is_admin": false,
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T13:00:00Z",
  "last_login": "2024-01-01T12:30:00Z"
}
```

### Deactivate User

**PUT** `/admin/users/{user_id}/deactivate`

Deactivate a user account.

#### Headers

```
Authorization: Bearer <admin-access-token>
```

#### Response

**Status: 200 OK**

```json
{
  "message": "User deactivated successfully"
}
```

### Activate User

**PUT** `/admin/users/{user_id}/activate`

Activate a user account.

#### Headers

```
Authorization: Bearer <admin-access-token>
```

#### Response

**Status: 200 OK**

```json
{
  "message": "User activated successfully"
}
```

## Data Models

### UserCreate

```json
{
  "email": "string (required)",
  "password": "string (required, min 8 chars)",
  "full_name": "string (optional)"
}
```

### UserResponse

```json
{
  "id": "integer",
  "uuid": "string (UUID)",
  "email": "string",
  "full_name": "string",
  "is_active": "boolean",
  "is_admin": "boolean",
  "created_at": "string (ISO datetime)",
  "updated_at": "string (ISO datetime)",
  "last_login": "string (ISO datetime, nullable)",
  "avatar_url": "string (nullable)",
  "bio": "string (nullable)",
  "phone": "string (nullable)"
}
```

### Token

```json
{
  "access_token": "string (JWT)",
  "refresh_token": "string (JWT)",
  "token_type": "string (bearer)",
  "expires_in": "integer (seconds)"
}
```

## Error Handling

### Common Error Responses

#### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

#### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

#### 404 Not Found
```json
{
  "detail": "User not found"
}
```

#### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "error message",
      "type": "error_type"
    }
  ]
}
```

## Rate Limiting

Authentication endpoints are rate limited:

- Login: 10 requests per minute per IP
- Registration: 5 requests per minute per IP
- Password reset: 3 requests per minute per IP

## Security Considerations

1. **JWT Tokens**: Access tokens expire in 30 minutes, refresh tokens in 7 days
2. **Password Requirements**: Minimum 8 characters
3. **HTTPS**: All production traffic should use HTTPS
4. **CORS**: Configured for specific origins in production
5. **Rate Limiting**: Implemented to prevent abuse
6. **Input Validation**: All inputs are validated using Pydantic models