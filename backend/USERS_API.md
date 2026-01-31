# Users Management API

## Overview

API endpoints for managing users in the Vi-En Reflex Trainer system.

**Base URL**: `/api/v1`

**Authentication**: All endpoints require Admin authentication

## Endpoints

### 1. List Users

Get all users with pagination, search, and filtering.

```
GET /users
```

**Query Parameters:**
- `page` (integer, default: 1) - Page number
- `limit` (integer, default: 10, max: 100) - Items per page
- `search` (string, optional) - Search in email or username
- `is_admin` (boolean, optional) - Filter by admin status
- `is_active` (boolean, optional) - Filter by active status

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "email": "user@example.com",
      "username": "username",
      "is_active": true,
      "is_admin": false,
      "created_at": "2026-01-31T10:00:00Z",
      "updated_at": "2026-01-31T10:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total_items": 50,
    "total_pages": 3,
    "has_next": true,
    "has_prev": false
  }
}
```

### 2. Get User by ID

Get a specific user by their UUID.

```
GET /users/{user_id}
```

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "username",
  "is_active": true,
  "is_admin": false,
  "created_at": "2026-01-31T10:00:00Z",
  "updated_at": "2026-01-31T10:00:00Z"
}
```

### 3. Create User

Create a new user.

```
POST /users
```

**Request Body:**
```json
{
  "email": "newuser@example.com",
  "username": "newuser",
  "password": "securepassword123"
}
```

**Response:** (201 Created)
```json
{
  "id": "uuid",
  "email": "newuser@example.com",
  "username": "newuser",
  "is_active": true,
  "is_admin": false,
  "created_at": "2026-01-31T10:00:00Z",
  "updated_at": "2026-01-31T10:00:00Z"
}
```

**Errors:**
- `400 Bad Request` - Email or username already exists
- `422 Unprocessable Entity` - Validation error

### 4. Update User

Update user information (status, admin rights, password).

```
PUT /users/{user_id}
```

**Request Body:** (all fields optional)
```json
{
  "is_active": true,
  "is_admin": false,
  "password": "newpassword123"
}
```

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "username",
  "is_active": true,
  "is_admin": false,
  "created_at": "2026-01-31T10:00:00Z",
  "updated_at": "2026-01-31T10:00:00Z"
}
```

**Notes:**
- Email and username cannot be changed
- Admin cannot deactivate their own account
- Admin cannot remove their own admin rights
- Password is optional (leave empty to keep current password)

**Errors:**
- `400 Bad Request` - Attempting to deactivate own account or remove own admin rights
- `404 Not Found` - User not found

### 5. Delete User

Delete a user.

```
DELETE /users/{user_id}
```

**Response:** (204 No Content)

**Notes:**
- Admin cannot delete their own account
- This is a permanent action

**Errors:**
- `400 Bad Request` - Attempting to delete own account
- `404 Not Found` - User not found

### 6. Update User Password

Update user password (alternative endpoint).

```
PATCH /users/{user_id}/password?password=newpassword123
```

**Query Parameters:**
- `password` (string, required, min 6 chars) - New password

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "username",
  "is_active": true,
  "is_admin": false,
  "created_at": "2026-01-31T10:00:00Z",
  "updated_at": "2026-01-31T10:00:00Z"
}
```

### 7. Get Users Statistics

Get summary statistics about users.

```
GET /users/stats/summary
```

**Response:**
```json
{
  "total_users": 150,
  "active_users": 142,
  "inactive_users": 8,
  "admin_users": 3
}
```

## Authorization

All endpoints require:
- Valid JWT token in Authorization header: `Bearer <token>`
- User must have `is_admin: true`

**Example:**
```bash
curl -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  http://localhost:8000/api/v1/users
```

## Error Responses

### 401 Unauthorized
```json
{
  "error": "Unauthorized",
  "message": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "error": "Forbidden",
  "message": "Not enough permissions"
}
```

### 404 Not Found
```json
{
  "error": "Not Found",
  "message": "User with id {uuid} not found"
}
```

### 400 Bad Request
```json
{
  "error": "Bad Request",
  "message": "Email user@example.com already registered"
}
```

## Testing with Postman/Curl

### Create User
```bash
curl -X POST http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "username": "testuser",
    "password": "password123"
  }'
```

### List Users
```bash
curl -X GET "http://localhost:8000/api/v1/users?page=1&limit=20&search=test" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### Update User (Toggle Admin)
```bash
curl -X PUT http://localhost:8000/api/v1/users/{user_id} \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "is_admin": true,
    "is_active": true
  }'
```

### Delete User
```bash
curl -X DELETE http://localhost:8000/api/v1/users/{user_id} \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```
