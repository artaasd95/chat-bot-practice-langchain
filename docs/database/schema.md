# Database Schema Documentation

This document describes the database schema for the LangGraph Chat Bot System, including table structures, relationships, and data models.

## Overview

The system uses PostgreSQL as the primary database with the following main entities:

- **Users**: User accounts and authentication information
- **Chat Sessions**: Conversation sessions between users and the AI
- **Chat Messages**: Individual messages within chat sessions

## Database Configuration

### Connection Settings

```python
# Environment Variables
DATABASE_URL = "postgresql://username:password@localhost:5432/chatbot_db"
DATABASE_POOL_SIZE = 20
DATABASE_MAX_OVERFLOW = 30
DATABASE_POOL_TIMEOUT = 30
```

### SQLAlchemy Configuration

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_timeout=30,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

## Table Schemas

### Users Table

Stores user account information and authentication data.

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    avatar_url TEXT,
    bio TEXT,
    phone VARCHAR(20)
);

-- Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_uuid ON users(uuid);
CREATE INDEX idx_users_is_active ON users(is_active);
CREATE INDEX idx_users_created_at ON users(created_at);
```

#### Column Descriptions

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| `id` | SERIAL | Primary key, auto-incrementing | PRIMARY KEY |
| `uuid` | UUID | Unique identifier for external references | UNIQUE, NOT NULL |
| `email` | VARCHAR(255) | User's email address | UNIQUE, NOT NULL |
| `hashed_password` | VARCHAR(255) | Bcrypt hashed password | NOT NULL |
| `full_name` | VARCHAR(255) | User's full name | NULLABLE |
| `is_active` | BOOLEAN | Whether the account is active | DEFAULT TRUE |
| `is_admin` | BOOLEAN | Whether the user has admin privileges | DEFAULT FALSE |
| `created_at` | TIMESTAMP WITH TIME ZONE | Account creation timestamp | DEFAULT CURRENT_TIMESTAMP |
| `updated_at` | TIMESTAMP WITH TIME ZONE | Last update timestamp | DEFAULT CURRENT_TIMESTAMP |
| `last_login` | TIMESTAMP WITH TIME ZONE | Last login timestamp | NULLABLE |
| `avatar_url` | TEXT | URL to user's avatar image | NULLABLE |
| `bio` | TEXT | User's biography/description | NULLABLE |
| `phone` | VARCHAR(20) | User's phone number | NULLABLE |

### Chat Sessions Table

Stores chat session information and metadata.

```sql
CREATE TABLE chat_sessions (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB DEFAULT '{}'
);

-- Indexes
CREATE INDEX idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX idx_chat_sessions_uuid ON chat_sessions(uuid);
CREATE INDEX idx_chat_sessions_created_at ON chat_sessions(created_at);
CREATE INDEX idx_chat_sessions_updated_at ON chat_sessions(updated_at);
CREATE INDEX idx_chat_sessions_is_active ON chat_sessions(is_active);
CREATE INDEX idx_chat_sessions_metadata ON chat_sessions USING GIN(metadata);
```

#### Column Descriptions

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| `id` | SERIAL | Primary key, auto-incrementing | PRIMARY KEY |
| `uuid` | UUID | Unique identifier for external references | UNIQUE, NOT NULL |
| `user_id` | INTEGER | Reference to the user who owns this session | FOREIGN KEY, NOT NULL |
| `title` | VARCHAR(500) | Session title/description | NULLABLE |
| `created_at` | TIMESTAMP WITH TIME ZONE | Session creation timestamp | DEFAULT CURRENT_TIMESTAMP |
| `updated_at` | TIMESTAMP WITH TIME ZONE | Last update timestamp | DEFAULT CURRENT_TIMESTAMP |
| `is_active` | BOOLEAN | Whether the session is active | DEFAULT TRUE |
| `metadata` | JSONB | Additional session metadata | DEFAULT '{}' |

### Chat Messages Table

Stores individual messages within chat sessions.

```sql
CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    session_id INTEGER NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    tokens_used INTEGER DEFAULT 0,
    processing_time_ms INTEGER DEFAULT 0
);

-- Indexes
CREATE INDEX idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX idx_chat_messages_uuid ON chat_messages(uuid);
CREATE INDEX idx_chat_messages_created_at ON chat_messages(created_at);
CREATE INDEX idx_chat_messages_role ON chat_messages(role);
CREATE INDEX idx_chat_messages_metadata ON chat_messages USING GIN(metadata);
```

#### Column Descriptions

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| `id` | SERIAL | Primary key, auto-incrementing | PRIMARY KEY |
| `uuid` | UUID | Unique identifier for external references | UNIQUE, NOT NULL |
| `session_id` | INTEGER | Reference to the chat session | FOREIGN KEY, NOT NULL |
| `content` | TEXT | Message content | NOT NULL |
| `role` | VARCHAR(20) | Message role (user, assistant, system) | CHECK constraint |
| `created_at` | TIMESTAMP WITH TIME ZONE | Message creation timestamp | DEFAULT CURRENT_TIMESTAMP |
| `metadata` | JSONB | Additional message metadata | DEFAULT '{}' |
| `tokens_used` | INTEGER | Number of tokens used for this message | DEFAULT 0 |
| `processing_time_ms` | INTEGER | Processing time in milliseconds | DEFAULT 0 |

## Relationships

### Entity Relationship Diagram

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│     Users       │       │  Chat Sessions  │       │  Chat Messages  │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK)         │◄─────┐│ id (PK)         │◄─────┐│ id (PK)         │
│ uuid            │      ││ uuid            │      ││ uuid            │
│ email           │      ││ user_id (FK)    │      ││ session_id (FK) │
│ hashed_password │      ││ title           │      ││ content         │
│ full_name       │      ││ created_at      │      ││ role            │
│ is_active       │      ││ updated_at      │      ││ created_at      │
│ is_admin        │      ││ is_active       │      ││ metadata        │
│ created_at      │      ││ metadata        │      ││ tokens_used     │
│ updated_at      │      │└─────────────────┘      ││ processing_time │
│ last_login      │      │                         │└─────────────────┘
│ avatar_url      │      │                         │
│ bio             │      │                         │
│ phone           │      └─────────────────────────┘
└─────────────────┘
```

### Relationship Details

1. **Users → Chat Sessions**: One-to-Many
   - One user can have multiple chat sessions
   - Foreign key: `chat_sessions.user_id` → `users.id`
   - Cascade delete: When a user is deleted, all their sessions are deleted

2. **Chat Sessions → Chat Messages**: One-to-Many
   - One session can have multiple messages
   - Foreign key: `chat_messages.session_id` → `chat_sessions.id`
   - Cascade delete: When a session is deleted, all its messages are deleted

## SQLAlchemy Models

### User Model

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid as uuid_lib

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid_lib.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True, index=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    avatar_url = Column(Text)
    bio = Column(Text)
    phone = Column(String(20))
    
    # Relationships
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
```

### Chat Session Model

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid as uuid_lib

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid_lib.uuid4)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), index=True)
    is_active = Column(Boolean, default=True, index=True)
    metadata = Column(JSONB, default={})
    
    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
```

### Chat Message Model

```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid as uuid_lib

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid_lib.uuid4)
    session_id = Column(Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    role = Column(String(20), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    metadata = Column(JSONB, default={})
    tokens_used = Column(Integer, default=0)
    processing_time_ms = Column(Integer, default=0)
    
    # Constraints
    __table_args__ = (
        CheckConstraint("role IN ('user', 'assistant', 'system')", name="check_message_role"),
    )
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")
```

## Database Migrations

### Alembic Configuration

The project uses Alembic for database migrations:

```python
# alembic.ini
[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os
sqlalchemy.url = postgresql://username:password@localhost:5432/chatbot_db

[post_write_hooks]
hooks = black
black.type = console_scripts
black.entrypoint = black
black.options = -l 79 REVISION_SCRIPT_FILENAME
```

### Migration Commands

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Downgrade to previous version
alembic downgrade -1

# Show current revision
alembic current

# Show migration history
alembic history
```

### Initial Migration

```python
# alembic/versions/001_initial_schema.py
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_admin', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('avatar_url', sa.Text(), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('uuid')
    )
    
    # Create indexes for users table
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_uuid', 'users', ['uuid'])
    op.create_index('idx_users_is_active', 'users', ['is_active'])
    op.create_index('idx_users_created_at', 'users', ['created_at'])
    
    # Create chat_sessions table
    op.create_table(
        'chat_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid')
    )
    
    # Create indexes for chat_sessions table
    op.create_index('idx_chat_sessions_user_id', 'chat_sessions', ['user_id'])
    op.create_index('idx_chat_sessions_uuid', 'chat_sessions', ['uuid'])
    op.create_index('idx_chat_sessions_created_at', 'chat_sessions', ['created_at'])
    op.create_index('idx_chat_sessions_updated_at', 'chat_sessions', ['updated_at'])
    op.create_index('idx_chat_sessions_is_active', 'chat_sessions', ['is_active'])
    op.create_index('idx_chat_sessions_metadata', 'chat_sessions', ['metadata'], postgresql_using='gin')
    
    # Create chat_messages table
    op.create_table(
        'chat_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('processing_time_ms', sa.Integer(), nullable=True),
        sa.CheckConstraint("role IN ('user', 'assistant', 'system')", name='check_message_role'),
        sa.ForeignKeyConstraint(['session_id'], ['chat_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid')
    )
    
    # Create indexes for chat_messages table
    op.create_index('idx_chat_messages_session_id', 'chat_messages', ['session_id'])
    op.create_index('idx_chat_messages_uuid', 'chat_messages', ['uuid'])
    op.create_index('idx_chat_messages_created_at', 'chat_messages', ['created_at'])
    op.create_index('idx_chat_messages_role', 'chat_messages', ['role'])
    op.create_index('idx_chat_messages_metadata', 'chat_messages', ['metadata'], postgresql_using='gin')

def downgrade():
    op.drop_table('chat_messages')
    op.drop_table('chat_sessions')
    op.drop_table('users')
```

## Data Access Patterns

### Common Queries

#### Get User with Sessions

```python
from sqlalchemy.orm import joinedload

def get_user_with_sessions(db: Session, user_id: int):
    return db.query(User).options(
        joinedload(User.chat_sessions).joinedload(ChatSession.messages)
    ).filter(User.id == user_id).first()
```

#### Get Recent Sessions for User

```python
def get_recent_sessions(db: Session, user_id: int, limit: int = 10):
    return db.query(ChatSession).filter(
        ChatSession.user_id == user_id,
        ChatSession.is_active == True
    ).order_by(ChatSession.updated_at.desc()).limit(limit).all()
```

#### Get Messages for Session

```python
def get_session_messages(db: Session, session_id: int, limit: int = 50, offset: int = 0):
    return db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at.asc()).offset(offset).limit(limit).all()
```

#### Search Sessions by Title

```python
from sqlalchemy import func

def search_sessions(db: Session, user_id: int, search_term: str):
    return db.query(ChatSession).filter(
        ChatSession.user_id == user_id,
        ChatSession.is_active == True,
        func.lower(ChatSession.title).contains(search_term.lower())
    ).order_by(ChatSession.updated_at.desc()).all()
```

### Performance Optimizations

#### Pagination Helper

```python
from typing import List, Optional
from sqlalchemy import func

def paginate_query(query, page: int = 1, per_page: int = 20):
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    
    return {
        'items': items,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page,
        'has_next': page * per_page < total,
        'has_prev': page > 1
    }
```

#### Bulk Operations

```python
def bulk_create_messages(db: Session, messages_data: List[dict]):
    """Efficiently create multiple messages"""
    db.bulk_insert_mappings(ChatMessage, messages_data)
    db.commit()

def bulk_update_sessions(db: Session, session_updates: List[dict]):
    """Efficiently update multiple sessions"""
    db.bulk_update_mappings(ChatSession, session_updates)
    db.commit()
```

## Database Maintenance

### Backup and Restore

```bash
# Create backup
pg_dump -h localhost -U username -d chatbot_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
psql -h localhost -U username -d chatbot_db < backup_20240101_120000.sql
```

### Performance Monitoring

```sql
-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- Check slow queries
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

### Data Cleanup

```sql
-- Clean up old inactive sessions (older than 6 months)
DELETE FROM chat_sessions 
WHERE is_active = false 
  AND updated_at < NOW() - INTERVAL '6 months';

-- Clean up orphaned messages (should not happen with FK constraints)
DELETE FROM chat_messages 
WHERE session_id NOT IN (SELECT id FROM chat_sessions);

-- Update statistics
ANALYZE;
```

## Security Considerations

1. **Password Storage**: Passwords are hashed using bcrypt with salt
2. **Data Encryption**: Sensitive data encrypted at rest
3. **Access Control**: Row-level security for multi-tenant scenarios
4. **Audit Logging**: Database changes are logged
5. **Connection Security**: SSL/TLS for database connections
6. **Backup Encryption**: Database backups are encrypted

## Monitoring and Alerts

### Key Metrics to Monitor

1. **Connection Pool**: Active/idle connections
2. **Query Performance**: Slow query detection
3. **Table Growth**: Monitor table sizes
4. **Index Usage**: Unused index detection
5. **Lock Contention**: Blocking queries
6. **Replication Lag**: If using read replicas

### Recommended Alerts

1. Connection pool exhaustion (>90% utilization)
2. Slow queries (>5 seconds)
3. High CPU usage (>80%)
4. Disk space usage (>85%)
5. Failed backup jobs
6. Replication lag (>1 minute)