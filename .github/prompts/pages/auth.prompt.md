# Auth Pages - Login & Register

## Project Info
- **Tên dự án**: Vi-En Reflex Trainer
- **Loại sản phẩm**: Education App
- **Ngành**: Language Learning
- **Stack**: react + tailwind + lucide-react

## Page/Component
- **Tên page**: Authentication (Login + Register)
- **Mô tả ngắn**: Trang đăng nhập/đăng ký với form validation, JWT token storage, redirect sau khi auth thành công.

## Features
1. Login form: email/username + password
2. Register form: email, username, password, confirm password
3. Toggle giữa Login/Register mode
4. Form validation real-time (email format, password strength)
5. "Remember me" checkbox cho login
6. Link "Forgot password?" (placeholder, chưa implement backend)
7. Social login placeholders (Google, Facebook - future)
8. Guest mode button: "Tiếp tục không đăng ký" → /lessons

## API Endpoints

### POST /api/v1/auth/register
- **Request**:
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "securepass123"
}
```
- **Response**:
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "johndoe",
  "is_active": true,
  "created_at": "2026-01-25T10:00:00Z"
}
```
- **Error 400**:
```json
{
  "detail": "Email already registered"
}
```

### POST /api/v1/auth/login
- **Request**:
```json
{
  "identifier": "user@example.com",
  "password": "securepass123"
}
```
- **Response**:
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 1440
}
```
- **Error 401**:
```json
{
  "detail": "Incorrect email/username or password"
}
```

### POST /api/v1/auth/refresh
- **Request**:
```json
{
  "refresh_token": "eyJhbGc..."
}
```
- **Response**:
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

## UI States
- [x] Loading state: Button spinner "Đang xử lý..."
- [x] Empty state: N/A
- [x] Error state: Toast notification với error message từ API
- [x] Success state: Success toast + redirect to /lessons hoặc /dashboard

## Style Preferences
- **Mood**: clean, professional, trustworthy
- **Dark mode**: both
- **Design flexibility**: Tự do design form layout, có thể split screen, center card, hoặc sáng tạo khác
- **Special effects**: 
  - Card glassmorphism hoặc elevated card
  - Input focus glow effect
  - Button hover lift
  - Password strength indicator (color bars hoặc progress)
  - Smooth transitions

## Images & Illustrations
- **Background**: 
  - Gradient mesh hoặc subtle pattern
  - Split screen với illustration bên trái/phải
  - Image: Education/learning themed
- **Login/Register illustration**: 
  - Security/access themed từ [unDraw](https://undraw.co)
  - Login concept, sign up concept
- **Empty state**: Friendly illustration khi form trống
- **Sources**:
  - Background images: [Unsplash](https://unsplash.com) (abstract, gradient, minimal)
  - Illustrations: unDraw, Storyset
  - Patterns: Hero Patterns, Cool Backgrounds

## Validation Rules
- **Email**: Valid email format, max 100 chars
- **Username**: 3-50 chars, alphanumeric + underscore
- **Password**: Min 6 chars, show strength meter
- **Confirm password**: Must match password

## Component Structure
```
pages/Auth.tsx
├── AuthCard (glassmorphism)
│   ├── TabSwitch (Login/Register)
│   ├── LoginForm
│   │   ├── Input (email/username)
│   │   ├── PasswordInput (with toggle visibility)
│   │   ├── Checkbox (remember me)
│   │   └── SubmitButton
│   └── RegisterForm
│       ├── Input (email)
│       ├── Input (username)
│       ├── PasswordInput (with strength meter)
│       ├── PasswordInput (confirm)
│       └── SubmitButton
├── GuestModeButton
└── SocialLoginButtons (placeholder)
```

## Token Management
- Store `access_token` in localStorage: `vi_en_token`
- Store `refresh_token` in localStorage: `vi_en_refresh`
- Store `user` object in localStorage: `vi_en_user`
- Auto-refresh token 5 minutes before expiry
- Clear all on logout
