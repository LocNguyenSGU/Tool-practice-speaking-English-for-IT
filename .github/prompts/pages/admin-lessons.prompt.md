# Admin - Lessons Management

## Project Info
- **Tên dự án**: Vi-En Reflex Trainer
- **Loại sản phẩm**: Education App / Admin Panel
- **Ngành**: Language Learning
- **Stack**: react + tailwind + lucide-react

## Page/Component
- **Tên page**: Admin Lessons Management
- **Mô tả ngắn**: Quản lý bài học - CRUD operations (Create, Read, Update, Delete) cho admin.

## Features
1. **Lessons Table**:
   - Columns: ID, Title, Description, Order, Active, Created, Actions
   - Sort by: Created date, Order index
   - Filter: Active/Inactive/All
2. **Create Lesson**:
   - Modal/Dialog với form: Title, Description, Order, Active toggle
   - Validation: Title required, Order integer
3. **Edit Lesson**:
   - Pre-filled form với lesson data
   - Update API call
4. **Delete Lesson**:
   - Confirmation dialog: "Xóa bài học sẽ xóa tất cả câu liên quan. Chắc chắn?"
   - Cascade delete sentences
5. **Bulk Actions** (optional):
   - Select multiple lessons
   - Bulk activate/deactivate

## API Endpoints

### GET /api/v1/lessons
- **Query params**: `page=1&limit=20&search=&sort_by=created_at&order=desc`
- **Response**: Same as lessons.prompt.md

### POST /api/v1/lessons
- **Headers**: `Authorization: Bearer {admin_token}`
- **Request**:
```json
{
  "title": "Advanced Conversations",
  "description": "Complex Vietnamese conversations",
  "order_index": 10,
  "is_active": true
}
```
- **Response**:
```json
{
  "id": 10,
  "title": "Advanced Conversations",
  "description": "Complex Vietnamese conversations",
  "order_index": 10,
  "is_active": true,
  "created_at": "2026-01-25T10:00:00Z",
  "updated_at": "2026-01-25T10:00:00Z"
}
```
- **Error 401**: Unauthorized
- **Error 403**: Forbidden (not admin)

### PUT /api/v1/lessons/{lesson_id}
- **Headers**: `Authorization: Bearer {admin_token}`
- **Request**:
```json
{
  "title": "Updated Title",
  "description": "Updated description",
  "is_active": false
}
```
- **Response**: Updated lesson object

### DELETE /api/v1/lessons/{lesson_id}
- **Headers**: `Authorization: Bearer {admin_token}`
- **Response**: 204 No Content
- **Error 404**: Lesson not found

## UI States
- [x] Loading state: Skeleton table rows
- [x] Empty state: "Chưa có bài học nào. Tạo bài học đầu tiên!"
- [x] Error state: Error toast với retry
- [x] Success state: Success toast "Đã tạo/cập nhật/xóa bài học"

## Style Preferences
- **Mood**: professional, data-focused, efficient
- **Dark mode**: both
- **Design flexibility**: Tự do thiết kế admin interface hiện đại, có thể tham khảo các admin dashboard đẹp
- **Special effects**:
  - Table row hover highlight
  - Modal/dialog fade-in animation
  - Button loading spinners
  - Toast notifications với slide-in animation
  - Smooth transitions

## Images & Illustrations
- **Empty state**: 
  - "No lessons yet" illustration (admin creating content)
  - Friendly illustration khuyến khích admin tạo lesson đầu tiên
- **Dashboard header**: 
  - Admin panel icon/illustration
  - Stats visualization (optional charts)
- **Success states**: 
  - Success icons với checkmarks
  - Celebration micro-animations
- **Sources**:
  - Illustrations: unDraw (admin, dashboard, management themes)
  - Icons: Lucide React

## Component Structure
```
pages/AdminLessons.tsx
├── Header
│   ├── Title "Quản lý bài học"
│   └── CreateLessonButton (opens dialog)
├── FiltersBar
│   ├── SearchInput
│   ├── FilterDropdown (Active/All)
│   └── SortDropdown
├── LessonsTable (custom table với Tailwind)
│   ├── TableHeader
│   └── TableRow (map lessons)
│       ├── IdCell
│       ├── TitleCell
│       ├── DescriptionCell (truncated)
│       ├── OrderCell
│       ├── ActiveBadge
│       ├── CreatedCell
│       └── ActionsCell
│           ├── EditButton
│           └── DeleteButton
└── Pagination

Dialogs/Modals:
├── CreateLessonDialog (custom modal)
│   └── LessonForm
├── EditLessonDialog
│   └── LessonForm (pre-filled)
└── DeleteConfirmDialog
```

## Form Validation
- **Title**: Required, max 200 chars
- **Description**: Optional, max 1000 chars
- **Order Index**: Integer, default = max + 1
- **Is Active**: Boolean, default = true

## Admin Auth Guard
- Check user.is_admin before rendering
- Redirect to /lessons if not admin
- Show 403 error if API returns forbidden
