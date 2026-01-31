# Admin Dashboard - Vi-En Reflex Trainer

## Overview

Admin dashboard hiện đại, clean và professional cho việc quản lý bài học và câu trong hệ thống Vi-En Reflex Trainer.

## Features

### ✅ Dashboard
- Tổng quan thống kê (Lessons, Sentences, Users, Progress)
- Quick actions để truy cập nhanh các chức năng
- Stats cards với loading skeleton states

### ✅ Quản lý Bài học (Lessons Management)
- **CRUD Operations**: Create, Read, Update, Delete
- **Search**: Tìm kiếm theo title hoặc description
- **Pagination**: Phân trang với navigation
- **Table View**: Hiển thị ID, Title, Description, Order, Status, Created Date
- **Status Badge**: Active/Inactive với màu sắc phân biệt
- **Modal Forms**: Create/Edit với validation
- **Delete Confirmation**: Warning về việc xóa cascade

### ✅ Quản lý Câu (Sentences Management)
- **CRUD Operations**: Create, Read, Update, Delete cho sentences
- **Bulk Upload**: Import nhiều câu cùng lúc qua JSON
  - JSON format validation
  - Preview table trước khi submit
  - Example format hiển thị
- **Lesson Filter**: Lọc câu theo bài học
- **Search**: Tìm kiếm trong Vietnamese hoặc English text
- **Pagination**: 50 items per page
- **Table View**: ID, Lesson, Vietnamese, English, Order, Created Date

## File Structure

```
frontend/src/
├── pages/
│   ├── admin/
│   │   ├── AdminLayout.tsx          # Layout với sidebar
│   │   ├── Dashboard.tsx            # Trang tổng quan
│   │   ├── AdminLessons.tsx         # Quản lý bài học
│   │   └── AdminSentences.tsx       # Quản lý câu
│
├── components/
│   └── admin/
│       ├── Sidebar.tsx              # Sidebar navigation
│       ├── StatsCard.tsx            # Dashboard stat cards
│       ├── LessonForm.tsx           # Create/Edit lesson modal
│       ├── SentenceForm.tsx         # Create/Edit sentence modal
│       ├── BulkUploadModal.tsx      # Bulk upload JSON
│       ├── ConfirmDialog.tsx        # Delete confirmation
│       └── Toast.tsx                # Toast notifications
│
└── utils/
    ├── api.ts                       # API call helper với auto token refresh
    └── adminAuth.ts                 # Admin auth guards
```

## Routes

```
/admin                  → Dashboard (tổng quan)
/admin/dashboard        → Dashboard
/admin/lessons          → Quản lý bài học
/admin/sentences        → Quản lý câu
```

## Design System

Theo đúng design system hiện đại, clean đã implement ở client pages:

### Colors
- **Primary**: `indigo-600` / `indigo-700`
- **Background**: `gray-50` (page), `white` (cards)
- **Text**: `gray-900` (headings), `gray-700` (body), `gray-600` (secondary)
- **Borders**: `gray-200` / `gray-300`
- **Success**: `green-600`
- **Error**: `red-600`
- **Info**: `blue-600`

### Typography
- **Font**: Inter (sans-serif)
- **Headings**: font-bold
- **Body**: font-medium / regular

### Spacing & Layout
- **Rounded**: `rounded-lg` (consistent)
- **Shadows**: `shadow-sm`, `shadow-md`, `shadow-lg`
- **Padding**: `p-4`, `p-6`, `p-8`
- **Gaps**: `gap-2`, `gap-3`, `gap-4`, `gap-6`

### Animations
- **Transitions**: `transition-colors duration-200`
- **Hover**: `hover:bg-gray-50`, `hover:shadow-md`, `hover:-translate-y-1`
- **Modal**: Fade in background, scale in content
- **Toast**: Slide in from right (`animate-slide-in-right`)

## API Integration

### Authentication
- All admin endpoints require admin authentication
- Auto token refresh on 401
- Redirect to `/lessons` if not admin

### Endpoints Used

**Lessons:**
- `GET /api/v1/lessons?page={page}&limit=20&search={query}`
- `POST /api/v1/lessons` (body: LessonCreate)
- `PUT /api/v1/lessons/{id}` (body: LessonUpdate)
- `DELETE /api/v1/lessons/{id}`

**Sentences:**
- `GET /api/v1/sentences?lesson_id={id}&page={page}&limit=50&search={query}`
- `POST /api/v1/sentences` (body: SentenceCreate)
- `POST /api/v1/sentences/bulk` (body: BulkSentenceCreate)
- `PUT /api/v1/sentences/{id}` (body: SentenceUpdate)
- `DELETE /api/v1/sentences/{id}`

## Admin Auth Guard

```typescript
// utils/adminAuth.ts
export const requireAdmin = (): boolean => {
  if (!isAuthenticated()) {
    window.location.href = '/auth';
    return false;
  }

  if (!isAdmin()) {
    window.location.href = '/lessons';
    return false;
  }

  return true;
};
```

Được sử dụng trong `AdminLayout` để protect tất cả admin routes.

## Toast Notifications

Toast system với 3 types:
- **Success**: Green, CheckCircle icon
- **Error**: Red, XCircle icon
- **Info**: Blue, Info icon

Auto-dismiss sau 5 giây, slide in from right.

```typescript
// Usage
const { showToast } = useToast();
showToast('success', 'Đã tạo bài học thành công!');
```

## Bulk Upload Format

JSON Array format cho bulk upload sentences:

```json
[
  {"vi": "Xin chào", "en": "Hello"},
  {"vi": "Tạm biệt", "en": "Goodbye"},
  {"vi": "Cảm ơn", "en": "Thank you"}
]
```

**Features:**
- JSON validation
- Preview table với auto order_index
- Error handling cho invalid format
- Success message với count

## UI States

### Loading States
- Skeleton rows (3-5 animated pulse)
- Stats cards với pulsing numbers

### Empty States
- "Chưa có bài học nào. Tạo bài học đầu tiên!"
- "Bài học chưa có câu nào"

### Error States
- Toast notification (red, auto-dismiss)
- Form validation errors inline

### Success States
- Toast "Đã tạo/cập nhật/xóa thành công!"
- Bulk upload: "Đã tạo X câu thành công!"

## Testing Admin Access

1. Login với admin user
2. Navigate to `/admin` hoặc `/admin/dashboard`
3. Sidebar navigation:
   - Dashboard
   - Quản lý Bài học
   - Quản lý Câu
   - Logout

## Future Enhancements

Architecture đã được thiết kế để dễ dàng mở rộng:

1. **AI Auto-generation**: `/admin/ai-generator`
2. **IELTS Practice Management**: `/admin/ielts`
3. **User Management**: `/admin/users`
4. **Analytics Dashboard**: Charts, graphs cho practice data
5. **CSV Upload**: Thêm CSV parser vào BulkUploadModal

## Notes

- **No Dark Mode**: Simplified, consistent với client pages
- **No External Libraries**: Pure Tailwind + Lucide icons
- **Responsive**: Sidebar collapses on mobile (future enhancement)
- **Professional**: Clean, modern, minimal animations
- **Consistent**: Matches client pages design exactly

## Troubleshooting

### Admin access denied
- Check user `is_admin` field in database
- Verify token is valid
- Check browser console for auth errors

### API errors
- Check backend is running on `http://localhost:8000`
- Verify admin endpoints in backend
- Check network tab for request/response

### Toast not showing
- Check `ToastContainer` is rendered
- Verify `useToast` hook is called
- Check z-index conflicts
