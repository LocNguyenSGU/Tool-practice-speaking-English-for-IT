# Admin - Sentences Management

## Project Info
- **Tên dự án**: Vi-En Reflex Trainer
- **Loại sản phẩm**: Education App / Admin Panel
- **Ngành**: Language Learning
- **Stack**: react + tailwind + lucide-react

## Page/Component
- **Tên page**: Admin Sentences Management
- **Mô tả ngắn**: Quản lý câu - CRUD + Bulk Create cho sentences trong từng lesson.

## Features
1. **Sentences Table** (filter by lesson):
   - Columns: ID, Lesson, Vietnamese, English, Order, Created, Actions
   - Filter: Select lesson dropdown
   - Sort: Order index, Created date
2. **Create Sentence**:
   - Form: Lesson ID (dropdown), Vi text, En text, Order
3. **Bulk Create** (main feature):
   - CSV/JSON upload hoặc textarea paste
   - Format: `{"vi": "Xin chào", "en": "Hello"}`
   - Preview before submit
   - Batch create API call
4. **Edit Sentence**:
   - Pre-filled form
   - Audio cache invalidation note
5. **Delete Sentence**:
   - Confirmation dialog

## API Endpoints

### GET /api/v1/sentences
- **Query params**: `lesson_id={id}&page=1&limit=50&search=`
- **Response**: Same as lesson-detail.prompt.md

### POST /api/v1/sentences
- **Headers**: `Authorization: Bearer {admin_token}`
- **Request**:
```json
{
  "lesson_id": 1,
  "vi_text": "Chào buổi sáng",
  "en_text": "Good morning",
  "order_index": 5
}
```
- **Response**:
```json
{
  "id": 100,
  "lesson_id": 1,
  "vi_text": "Chào buổi sáng",
  "en_text": "Good morning",
  "order_index": 5,
  "created_at": "2026-01-25T10:00:00Z",
  "updated_at": "2026-01-25T10:00:00Z"
}
```

### POST /api/v1/sentences/bulk
- **Headers**: `Authorization: Bearer {admin_token}`
- **Request**:
```json
{
  "lesson_id": 1,
  "sentences": [
    {"vi": "Xin chào", "en": "Hello"},
    {"vi": "Tạm biệt", "en": "Goodbye"},
    {"vi": "Cảm ơn", "en": "Thank you"}
  ]
}
```
- **Response**: Array of created sentences
```json
[
  {
    "id": 101,
    "lesson_id": 1,
    "vi_text": "Xin chào",
    "en_text": "Hello",
    "order_index": 1,
    "created_at": "2026-01-25T10:00:00Z"
  }
]
```
- **Error 400**: Empty list or invalid format

### PUT /api/v1/sentences/{sentence_id}
- **Headers**: `Authorization: Bearer {admin_token}`
- **Request**:
```json
{
  "vi_text": "Updated Vietnamese",
  "en_text": "Updated English"
}
```
- **Response**: Updated sentence object
- **Note**: Audio cache auto-invalidated on text change

### DELETE /api/v1/sentences/{sentence_id}
- **Headers**: `Authorization: Bearer {admin_token}`
- **Response**: 204 No Content

## UI States
- [x] Loading state: Skeleton table + spinner on bulk upload
- [x] Empty state: "Chọn bài học để xem câu" hoặc "Bài học chưa có câu nào"
- [x] Error state: Error toast với details (bulk upload: show failed rows)
- [x] Success state: Success toast "Đã tạo 10 câu thành công"

## Style Preferences
- **Mood**: efficient, data-heavy, productive
- **Dark mode**: both
- **Design flexibility**: Admin panel có thể sáng tạo với layout hiện đại, data visualization đẹp
- **Special effects**:
  - Bulk upload: Progress bar animated during upload
  - Table row highlight on hover
  - Preview modal với smooth transition
  - Success animation (checkmark hoặc celebration)
  - Drag & drop zone với visual feedback

## Images & Illustrations
- **Empty state**: 
  - "Select a lesson" illustration
  - "No sentences yet" với admin adding content illustration
- **Bulk upload zone**: 
  - Upload icon với dashed border
  - Drag & drop visual cue
  - File preview thumbnails
- **Success state**: 
  - Checkmark animation
  - Created sentences count visualization
- **Sources**:
  - Illustrations: unDraw (upload, data entry, admin themes)
  - Icons: Lucide React

## Component Structure
```
pages/AdminSentences.tsx
├── Header
│   ├── Title "Quản lý câu"
│   ├── CreateSentenceButton
│   └── BulkCreateButton (opens modal)
├── FiltersBar
│   ├── LessonSelect (dropdown)
│   ├── SearchInput
│   └── SortDropdown
├── SentencesTable (custom table với Tailwind)
│   ├── TableHeader
│   └── TableRow (map sentences)
│       ├── IdCell
│       ├── LessonCell
│       ├── ViTextCell (truncated)
│       ├── EnTextCell (truncated)
│       ├── OrderCell
│       ├── CreatedCell
│       └── ActionsCell
│           ├── EditButton
│           └── DeleteButton
└── Pagination

Dialogs/Modals:
├── CreateSentenceDialog
│   └── SentenceForm
├── BulkCreateDialog
│   ├── LessonSelect
│   ├── JsonTextarea (or CSV upload with drag & drop)
│   ├── PreviewButton → PreviewTable
│   └── SubmitButton
├── EditSentenceDialog
│   └── SentenceForm (pre-filled)
└── DeleteConfirmDialog
```

## Bulk Upload Format
**JSON Array**:
```json
[
  {"vi": "Xin chào", "en": "Hello"},
  {"vi": "Tạm biệt", "en": "Goodbye"}
]
```

**CSV** (optional):
```csv
vi,en
Xin chào,Hello
Tạm biệt,Goodbye
```

## Form Validation
- **Lesson ID**: Required, dropdown select
- **Vi Text**: Required, max 500 chars
- **En Text**: Required, max 500 chars
- **Order Index**: Integer, auto = max + 1 in lesson

## Bulk Upload Logic
1. Parse JSON/CSV input
2. Validate format
3. Show preview table (vi, en, order)
4. Confirm & POST /sentences/bulk
5. Show success: "Created 50 sentences"
6. Show errors: "3 failed: [row indices]"
