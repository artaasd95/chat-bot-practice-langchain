# Admin API Documentation

The Admin Service provides administrative functionality for managing users, chat sessions, system settings, and monitoring the Chat Bot System.

## Base URL

```
http://localhost:8003/api/v1/admin
```

## Authentication

All endpoints require JWT authentication with admin privileges. Include the token in the Authorization header:

```
Authorization: Bearer <admin-jwt-token>
```

**Note**: The user must have `is_admin: true` in their profile to access these endpoints.

## Endpoints

### Health Check

**GET** `/health`

Check the health status of the admin service.

#### Response

**Status: 200 OK**

```json
{
  "status": "healthy",
  "service": "admin-service",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.0"
}
```

## User Management

### Get All Users

**GET** `/users`

Retrieve a paginated list of all users in the system.

#### Headers

```
Authorization: Bearer <admin-access-token>
```

#### Query Parameters

- `page` (optional): Page number (default: 1)
- `size` (optional): Page size (default: 20, max: 100)
- `search` (optional): Search term for email, name, or UUID
- `is_active` (optional): Filter by active status (`true`, `false`)
- `is_admin` (optional): Filter by admin status (`true`, `false`)
- `sort_by` (optional): Sort field (`created_at`, `updated_at`, `last_login`, `email`, `full_name`)
- `sort_order` (optional): Sort order (`asc`, `desc`, default: `desc`)
- `created_after` (optional): Filter users created after date (ISO format)
- `created_before` (optional): Filter users created before date (ISO format)

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
      "last_login": "2024-01-01T12:30:00Z",
      "avatar_url": "https://example.com/avatar.jpg",
      "bio": "Software developer",
      "phone": "+1234567890",
      "chat_sessions_count": 5,
      "total_messages_count": 150
    }
  ],
  "pagination": {
    "total": 1,
    "page": 1,
    "size": 20,
    "pages": 1,
    "has_next": false,
    "has_prev": false
  },
  "summary": {
    "total_users": 1,
    "active_users": 1,
    "admin_users": 0,
    "new_users_today": 0,
    "new_users_this_week": 1
  }
}
```

### Get User Details

**GET** `/users/{user_id}`

Retrieve detailed information about a specific user.

#### Headers

```
Authorization: Bearer <admin-access-token>
```

#### Response

**Status: 200 OK**

```json
{
  "user": {
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
  },
  "statistics": {
    "chat_sessions_count": 5,
    "total_messages_count": 150,
    "avg_messages_per_session": 30,
    "last_activity": "2024-01-01T12:30:00Z",
    "account_age_days": 30,
    "login_frequency": {
      "total_logins": 25,
      "logins_this_week": 5,
      "logins_this_month": 20
    }
  },
  "recent_sessions": [
    {
      "session_id": "sess_123e4567-e89b-12d3-a456-426614174000",
      "title": "Project Planning Discussion",
      "created_at": "2024-01-01T12:00:00Z",
      "message_count": 15,
      "last_activity": "2024-01-01T12:30:00Z"
    }
  ]
}
```

### Update User

**PUT** `/users/{user_id}`

Update user information and permissions.

#### Headers

```
Authorization: Bearer <admin-access-token>
Content-Type: application/json
```

#### Request Body

```json
{
  "full_name": "John Smith",
  "is_active": true,
  "is_admin": false,
  "bio": "Senior Software Developer",
  "phone": "+1234567890"
}
```

#### Response

**Status: 200 OK**

```json
{
  "user": {
    "id": 1,
    "uuid": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "full_name": "John Smith",
    "is_active": true,
    "is_admin": false,
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T13:00:00Z",
    "last_login": "2024-01-01T12:30:00Z",
    "bio": "Senior Software Developer",
    "phone": "+1234567890"
  },
  "changes": [
    "full_name updated",
    "bio updated",
    "phone updated"
  ]
}
```

### Delete User

**DELETE** `/users/{user_id}`

Permanently delete a user and all associated data.

#### Headers

```
Authorization: Bearer <admin-access-token>
```

#### Query Parameters

- `force` (optional): Force deletion even if user has active sessions (`true`, `false`, default: `false`)

#### Response

**Status: 200 OK**

```json
{
  "message": "User deleted successfully",
  "user_id": 1,
  "deleted_data": {
    "chat_sessions": 5,
    "messages": 150,
    "files": 0
  },
  "deleted_at": "2024-01-01T13:00:00Z"
}
```

## Chat Session Management

### Get All Chat Sessions

**GET** `/chat-sessions`

Retrieve a paginated list of all chat sessions in the system.

#### Headers

```
Authorization: Bearer <admin-access-token>
```

#### Query Parameters

- `page` (optional): Page number (default: 1)
- `size` (optional): Page size (default: 20, max: 100)
- `user_id` (optional): Filter by user ID
- `search` (optional): Search in session titles
- `created_after` (optional): Filter sessions created after date
- `created_before` (optional): Filter sessions created before date
- `min_messages` (optional): Filter sessions with minimum message count
- `max_messages` (optional): Filter sessions with maximum message count
- `sort_by` (optional): Sort field (`created_at`, `updated_at`, `message_count`, `title`)
- `sort_order` (optional): Sort order (`asc`, `desc`, default: `desc`)

#### Response

**Status: 200 OK**

```json
{
  "sessions": [
    {
      "session_id": "sess_123e4567-e89b-12d3-a456-426614174000",
      "title": "Project Planning Discussion",
      "user": {
        "id": 1,
        "email": "user@example.com",
        "full_name": "John Doe"
      },
      "created_at": "2024-01-01T12:00:00Z",
      "updated_at": "2024-01-01T12:30:00Z",
      "message_count": 15,
      "last_message_preview": "That sounds like a great approach for the database design...",
      "last_activity": "2024-01-01T12:30:00Z",
      "total_tokens_used": 2500
    }
  ],
  "pagination": {
    "total": 1,
    "page": 1,
    "size": 20,
    "pages": 1,
    "has_next": false,
    "has_prev": false
  },
  "summary": {
    "total_sessions": 1,
    "active_sessions_today": 1,
    "total_messages": 15,
    "total_tokens_used": 2500,
    "avg_messages_per_session": 15
  }
}
```

### Get Chat Session Details

**GET** `/chat-sessions/{session_id}`

Retrieve detailed information about a specific chat session.

#### Headers

```
Authorization: Bearer <admin-access-token>
```

#### Query Parameters

- `include_messages` (optional): Include all messages (default: true)
- `message_limit` (optional): Limit number of messages (default: 100)

#### Response

**Status: 200 OK**

```json
{
  "session": {
    "session_id": "sess_123e4567-e89b-12d3-a456-426614174000",
    "title": "Project Planning Discussion",
    "user": {
      "id": 1,
      "email": "user@example.com",
      "full_name": "John Doe"
    },
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:30:00Z",
    "message_count": 15
  },
  "messages": [
    {
      "id": "msg_123e4567-e89b-12d3-a456-426614174001",
      "content": "I need help planning a new software project",
      "role": "user",
      "timestamp": "2024-01-01T12:00:00Z",
      "metadata": {}
    },
    {
      "id": "msg_123e4567-e89b-12d3-a456-426614174002",
      "content": "I'd be happy to help you plan your new software project!",
      "role": "assistant",
      "timestamp": "2024-01-01T12:00:01Z",
      "metadata": {
        "model_used": "gpt-4",
        "tokens_used": {
          "input": 35,
          "output": 55,
          "total": 90
        }
      }
    }
  ],
  "analytics": {
    "total_tokens_used": 2500,
    "avg_response_time_ms": 1500,
    "user_message_count": 8,
    "assistant_message_count": 7,
    "session_duration_minutes": 30,
    "models_used": {
      "gpt-4": 7,
      "gpt-3.5-turbo": 0
    }
  }
}
```

### Delete Chat Session

**DELETE** `/chat-sessions/{session_id}`

Delete a chat session and all its messages.

#### Headers

```
Authorization: Bearer <admin-access-token>
```

#### Response

**Status: 200 OK**

```json
{
  "message": "Chat session deleted successfully",
  "session_id": "sess_123e4567-e89b-12d3-a456-426614174000",
  "deleted_messages": 15,
  "deleted_at": "2024-01-01T13:00:00Z"
}
```

## System Analytics

### Get System Statistics

**GET** `/analytics/overview`

Retrieve comprehensive system statistics and metrics.

#### Headers

```
Authorization: Bearer <admin-access-token>
```

#### Query Parameters

- `period` (optional): Time period (`day`, `week`, `month`, `year`, default: `week`)
- `timezone` (optional): Timezone for date calculations (default: UTC)

#### Response

**Status: 200 OK**

```json
{
  "overview": {
    "total_users": 150,
    "active_users": 120,
    "admin_users": 5,
    "total_sessions": 500,
    "total_messages": 15000,
    "total_tokens_used": 2500000,
    "avg_session_length": 25.5,
    "avg_response_time_ms": 1200
  },
  "period_stats": {
    "new_users": 10,
    "new_sessions": 50,
    "new_messages": 1500,
    "tokens_used": 250000,
    "active_users": 80,
    "peak_concurrent_users": 25
  },
  "usage_trends": {
    "daily_active_users": [
      {"date": "2024-01-01", "count": 45},
      {"date": "2024-01-02", "count": 52},
      {"date": "2024-01-03", "count": 48}
    ],
    "daily_messages": [
      {"date": "2024-01-01", "count": 200},
      {"date": "2024-01-02", "count": 250},
      {"date": "2024-01-03", "count": 180}
    ]
  },
  "model_usage": {
    "gpt-4": {
      "requests": 1200,
      "tokens": 1800000,
      "avg_response_time_ms": 1500
    },
    "gpt-3.5-turbo": {
      "requests": 300,
      "tokens": 700000,
      "avg_response_time_ms": 800
    }
  },
  "error_rates": {
    "total_errors": 25,
    "error_rate_percent": 1.67,
    "common_errors": [
      {"type": "rate_limit_exceeded", "count": 15},
      {"type": "model_timeout", "count": 8},
      {"type": "invalid_request", "count": 2}
    ]
  }
}
```

### Get User Analytics

**GET** `/analytics/users`

Retrieve detailed user analytics and behavior patterns.

#### Headers

```
Authorization: Bearer <admin-access-token>
```

#### Query Parameters

- `period` (optional): Time period (`day`, `week`, `month`, `year`, default: `month`)
- `user_id` (optional): Filter by specific user ID
- `include_inactive` (optional): Include inactive users (default: false)

#### Response

**Status: 200 OK**

```json
{
  "user_metrics": {
    "total_users": 150,
    "new_users": 10,
    "active_users": 120,
    "churned_users": 5,
    "retention_rate_percent": 80.0
  },
  "engagement_metrics": {
    "avg_sessions_per_user": 3.33,
    "avg_messages_per_user": 100,
    "avg_session_duration_minutes": 25.5,
    "most_active_users": [
      {
        "user_id": 1,
        "email": "user@example.com",
        "sessions": 15,
        "messages": 450,
        "total_time_minutes": 380
      }
    ]
  },
  "usage_patterns": {
    "peak_hours": [
      {"hour": 9, "active_users": 45},
      {"hour": 14, "active_users": 52},
      {"hour": 20, "active_users": 38}
    ],
    "peak_days": [
      {"day": "Monday", "active_users": 85},
      {"day": "Tuesday", "active_users": 92},
      {"day": "Wednesday", "active_users": 88}
    ]
  },
  "geographic_distribution": [
    {"country": "United States", "users": 75},
    {"country": "Canada", "users": 25},
    {"country": "United Kingdom", "users": 20}
  ]
}
```

## System Settings

### Get System Configuration

**GET** `/settings`

Retrieve current system configuration and settings.

#### Headers

```
Authorization: Bearer <admin-access-token>
```

#### Response

**Status: 200 OK**

```json
{
  "api_settings": {
    "rate_limits": {
      "chat_requests_per_minute": 30,
      "session_creation_per_minute": 10,
      "admin_requests_per_minute": 100
    },
    "message_limits": {
      "max_message_length": 4000,
      "max_messages_per_session": 1000,
      "max_sessions_per_user": 50
    }
  },
  "llm_settings": {
    "default_model": "gpt-4",
    "fallback_model": "gpt-3.5-turbo",
    "max_tokens": 2048,
    "temperature": 0.7,
    "timeout_seconds": 30
  },
  "security_settings": {
    "jwt_expiry_minutes": 30,
    "refresh_token_expiry_days": 7,
    "password_min_length": 8,
    "require_email_verification": false,
    "enable_2fa": false
  },
  "feature_flags": {
    "enable_streaming": true,
    "enable_file_uploads": false,
    "enable_voice_chat": false,
    "enable_analytics": true
  }
}
```

### Update System Configuration

**PUT** `/settings`

Update system configuration and settings.

#### Headers

```
Authorization: Bearer <admin-access-token>
Content-Type: application/json
```

#### Request Body

```json
{
  "api_settings": {
    "rate_limits": {
      "chat_requests_per_minute": 40
    }
  },
  "llm_settings": {
    "temperature": 0.8,
    "max_tokens": 3000
  },
  "feature_flags": {
    "enable_streaming": true,
    "enable_file_uploads": true
  }
}
```

#### Response

**Status: 200 OK**

```json
{
  "message": "Settings updated successfully",
  "updated_settings": {
    "api_settings.rate_limits.chat_requests_per_minute": 40,
    "llm_settings.temperature": 0.8,
    "llm_settings.max_tokens": 3000,
    "feature_flags.enable_file_uploads": true
  },
  "updated_at": "2024-01-01T13:00:00Z"
}
```

## System Monitoring

### Get System Health

**GET** `/monitoring/health`

Retrieve comprehensive system health information.

#### Headers

```
Authorization: Bearer <admin-access-token>
```

#### Response

**Status: 200 OK**

```json
{
  "overall_status": "healthy",
  "services": {
    "auth_service": {
      "status": "healthy",
      "response_time_ms": 45,
      "last_check": "2024-01-01T12:00:00Z"
    },
    "chat_service": {
      "status": "healthy",
      "response_time_ms": 120,
      "last_check": "2024-01-01T12:00:00Z"
    },
    "admin_service": {
      "status": "healthy",
      "response_time_ms": 35,
      "last_check": "2024-01-01T12:00:00Z"
    }
  },
  "database": {
    "status": "healthy",
    "connection_pool": {
      "active_connections": 5,
      "idle_connections": 15,
      "max_connections": 20
    },
    "query_performance": {
      "avg_query_time_ms": 25,
      "slow_queries": 0
    }
  },
  "redis": {
    "status": "healthy",
    "memory_usage_mb": 128,
    "connected_clients": 10,
    "operations_per_second": 150
  },
  "llm_service": {
    "status": "healthy",
    "avg_response_time_ms": 1200,
    "success_rate_percent": 98.5,
    "queue_length": 2
  }
}
```

### Get System Logs

**GET** `/monitoring/logs`

Retrieve system logs with filtering options.

#### Headers

```
Authorization: Bearer <admin-access-token>
```

#### Query Parameters

- `level` (optional): Log level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`)
- `service` (optional): Service name (`auth`, `chat`, `admin`)
- `start_time` (optional): Start time for log filtering (ISO format)
- `end_time` (optional): End time for log filtering (ISO format)
- `limit` (optional): Number of log entries to return (default: 100, max: 1000)
- `search` (optional): Search term in log messages

#### Response

**Status: 200 OK**

```json
{
  "logs": [
    {
      "timestamp": "2024-01-01T12:00:00Z",
      "level": "INFO",
      "service": "chat",
      "message": "Chat session created successfully",
      "metadata": {
        "user_id": 1,
        "session_id": "sess_123456",
        "request_id": "req_789012"
      }
    },
    {
      "timestamp": "2024-01-01T12:01:00Z",
      "level": "ERROR",
      "service": "chat",
      "message": "LLM service timeout",
      "metadata": {
        "error_code": "TIMEOUT",
        "request_id": "req_789013",
        "duration_ms": 30000
      }
    }
  ],
  "pagination": {
    "total": 2,
    "limit": 100,
    "has_more": false
  },
  "summary": {
    "total_logs": 2,
    "error_count": 1,
    "warning_count": 0,
    "info_count": 1
  }
}
```

## Data Models

### UserUpdate

```json
{
  "full_name": "string (optional)",
  "is_active": "boolean (optional)",
  "is_admin": "boolean (optional)",
  "bio": "string (optional)",
  "phone": "string (optional)"
}
```

### SystemSettings

```json
{
  "api_settings": {
    "rate_limits": "object (optional)",
    "message_limits": "object (optional)"
  },
  "llm_settings": {
    "default_model": "string (optional)",
    "temperature": "number (optional)",
    "max_tokens": "integer (optional)"
  },
  "feature_flags": "object (optional)"
}
```

### AnalyticsFilter

```json
{
  "period": "string (day|week|month|year)",
  "start_date": "string (ISO date, optional)",
  "end_date": "string (ISO date, optional)",
  "user_id": "integer (optional)",
  "timezone": "string (optional)"
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
  "detail": "Admin privileges required"
}
```

#### 404 Not Found
```json
{
  "detail": "User not found"
}
```

#### 409 Conflict
```json
{
  "detail": "Cannot delete user with active sessions"
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

Admin endpoints have the following rate limits:

- User management: 100 requests per minute
- Analytics: 50 requests per minute
- System settings: 20 requests per minute
- Monitoring: 200 requests per minute

## Security Considerations

1. **Admin Authentication**: All endpoints require valid admin JWT tokens
2. **Audit Logging**: All admin actions are logged with user identification
3. **Data Privacy**: Sensitive user data is masked in logs
4. **Access Control**: Fine-grained permissions for different admin operations
5. **Rate Limiting**: Prevents abuse of admin endpoints
6. **Input Validation**: All inputs are validated and sanitized

## Best Practices

1. **Regular Monitoring**: Check system health and analytics regularly
2. **User Management**: Review user accounts and permissions periodically
3. **Performance Optimization**: Monitor response times and optimize as needed
4. **Security Updates**: Keep system settings updated for security
5. **Data Backup**: Regular backups of user data and chat sessions
6. **Error Monitoring**: Set up alerts for critical errors and system issues