# Lessons List Page

## Project Info
- **Tên dự án**: Vi-En Reflex Trainer
- **Loại sản phẩm**: Education App
- **Ngành**: Language Learning
- **Stack**: react + tailwind + lucide-react

## Page/Component
- **Tên page**: Lessons List
- **Mô tả ngắn**: Danh sách các bài học với search, pagination, filter. Mỗi lesson card hiển thị title, description, số câu, progress (nếu user đã login).

## Features
1. Search bar: Tìm kiếm theo title
2. Lesson cards grid (responsive: 1 col mobile, 2-3 cols desktop)
3. Mỗi card hiển thị:
   - Title, description
   - Số lượng sentences
   - Progress bar (nếu authenticated user)
   - Button "Bắt đầu luyện tập" → /practice?lesson_id={id}
4. Pagination: Previous/Next + page numbers
5. Filter: Active/All lessons (admin view)
6. Sort: By created_at, order_index

## API Endpoints

### GET /api/v1/lessons
- **Query params**: `page=1&limit=20&search=greetings&sort_by=created_at&order=asc`
- **Response**:
```json
{
  "items": [
    {
      "id": 1,
      "title": "Basic Greetings",
      "description": "Learn common Vietnamese greetings",
      "order_index": 1,
      "is_active": true,
      "created_at": "2026-01-20T10:00:00Z",
      "updated_at": "2026-01-20T10:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total_items": 100,
    "total_pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```

### GET /api/v1/lessons/{lesson_id}/sentences-count (custom endpoint)
- **Response**:
```json
{
  "lesson_id": 1,
  "total_sentences": 50
}
```

### GET /api/v1/practice/stats?lesson_id={id} (if authenticated)
- **Response**:
```json
{
  "total_practiced": 20,
  "total_practice_count": 100,
  "recent_practiced_count": 5
}
```

## UI States
- [x] Loading state: Skeleton cards (6 cards)
- [x] Empty state: "Chưa có bài học nào" với illustration + CTA (admin: thêm lesson)
- [x] Error state: Error card với retry button
- [x] Success state: Cards render với smooth fade-in animation

## Style Preferences
- **Mood**: clean, organized, inviting
- **Dark mode**: both
- **Design flexibility**: Tự do chọn card style, grid layout, spacing để UI thật sự hấp dẫn
- **Special effects**:
  - Card hover: lift + glow hoặc scale
  - Progress bar: animated fill với gradient
  - Search input: focus border animation hoặc shadow glow
  - Skeleton loading với shimmer
  - Staggered card animations on load

## Images & Illustrations
- **Lesson cards**: 
  - Thumbnail images cho mỗi lesson (education icons hoặc themed images)
  - Gradient backgrounds với patterns
  - Icon overlay (book, chat, graduation cap, etc.)
- **Empty state**: "No lessons found" illustration
- **Search illustration**: Magnifying glass với books
- **Sources**:
  - Lesson thumbnails: Unsplash (education, books, learning)
  - Icons: Lucide React
  - Illustrations: unDraw, Illustrations.co
  - Patterns: Subtle geometric patterns

## Component Structure
```
pages/Lessons.tsx
├── Header
│   ├── Title "Danh sách bài học"
│   └── SearchBar
├── FilterSort
│   ├── FilterDropdown (Active/All)
│   └── SortDropdown (Created date, Order)
├── LessonGrid
│   └── LessonCard (map items)
│       ├── CardHeader (title, description)
│       ├── CardContent
│       │   ├── SentenceCount
│       │   └── ProgressBar (conditional)
│       └── CardFooter
│           └── StartButton
└── Pagination
    ├── PreviousButton
    ├── PageNumbers
    └── NextButton
```

## User Experience
- Guest: Xem tất cả lessons, không có progress
- Authenticated: Hiển thị progress bar, highlight lessons đã bắt đầu
- Admin: Thêm button "Tạo bài học mới" (top right)
