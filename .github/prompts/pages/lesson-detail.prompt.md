# Lesson Detail Page

## Project Info
- **Tên dự án**: Vi-En Reflex Trainer
- **Loại sản phẩm**: Education App
- **Ngành**: Language Learning
- **Stack**: react + tailwind + lucide-react

## Page/Component
- **Tên page**: Lesson Detail
- **Mô tả ngắn**: Chi tiết bài học với danh sách sentences, có thể play audio, preview trước khi bắt đầu practice.

## Features
1. Lesson header: Title, description, metadata (created date, total sentences)
2. Action buttons: "Bắt đầu luyện tập" → /practice?lesson_id={id}
3. Sentences list (expandable table/cards):
   - Vietnamese text
   - English text
   - Audio buttons (play vi/en)
   - Order index
4. Progress indicator: "Bạn đã luyện 20/50 câu" (nếu authenticated)
5. Back button: ← Quay lại danh sách

## API Endpoints

### GET /api/v1/lessons/{lesson_id}
- **Response**:
```json
{
  "id": 1,
  "title": "Basic Greetings",
  "description": "Learn common Vietnamese greetings",
  "order_index": 1,
  "is_active": true,
  "created_at": "2026-01-20T10:00:00Z",
  "updated_at": "2026-01-20T10:00:00Z"
}
```

### GET /api/v1/sentences?lesson_id={id}&page=1&limit=50
- **Response**:
```json
{
  "items": [
    {
      "id": 1,
      "lesson_id": 1,
      "vi_text": "Xin chào",
      "en_text": "Hello",
      "vi_audio_url": "/api/v1/audio/1/vi",
      "en_audio_url": "/api/v1/audio/1/en",
      "order_index": 1,
      "created_at": "2026-01-20T10:00:00Z",
      "updated_at": "2026-01-20T10:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total_items": 50,
    "total_pages": 1,
    "has_next": false,
    "has_prev": false
  }
}
```

### GET /api/v1/audio/{sentence_id}/{lang} (vi/en)
- **Response**: Audio file (MP3)
- **Headers**: `Content-Type: audio/mpeg`

### GET /api/v1/practice/stats?lesson_id={id} (authenticated)
- **Response**:
```json
{
  "total_practiced": 20,
  "total_practice_count": 100,
  "recent_practiced_count": 5
}
```

## UI States
- [x] Loading state: Skeleton cho header + sentences table
- [x] Empty state: "Bài học chưa có câu nào" (admin: add sentences)
- [x] Error state: Error card với retry button
- [x] Success state: Smooth render với fade-in

## Style Preferences
- **Mood**: organized, educational, clear
- **Dark mode**: both
- **Design flexibility**: Tự do thiết kế table/list layout, có thể dùng cards thay vì table nếu đẹp hơn
- **Special effects**:
  - Audio button: pulse animation khi playing
  - Sentence hover: highlight với smooth transition
  - Progress bar: animated fill
  - Collapsible/expandable sections

## Images & Illustrations
- **Lesson header**: 
  - Hero image cho lesson (themed theo topic)
  - Icon badge lớn đại diện cho lesson
- **Sentences section**: 
  - Audio wave visualization (optional)
  - Language flags (VN 🇻🇳 / US 🇺🇸) nhỏ bên cạnh text
- **Empty state**: "No sentences yet" illustration
- **Sources**:
  - Header images: Unsplash (theo topic của lesson)
  - Icons: Lucide React
  - Illustrations: unDraw, Storyset

## Component Structure
```
pages/LessonDetail.tsx
├── BackButton
├── LessonHeader
│   ├── Title + Description
│   ├── Metadata (date, sentences count)
│   └── ProgressBadge (authenticated)
├── ActionButtons
│   └── StartPracticeButton (primary)
├── SentencesSection
│   ├── SectionHeader "Danh sách câu"
│   └── SentencesTable
│       └── SentenceRow (map items)
│           ├── OrderIndex
│           ├── ViText
│           ├── EnText
│           ├── AudioButton (vi)
│           └── AudioButton (en)
└── Pagination (if > 50 sentences)
```

## Audio Player Logic
- Play audio inline: `<audio>` element với controls hidden
- Loading state: Spinner on button
- Error state: Show error toast
- Cache: Browser cache audio files
- Play icon: ▶️ → ⏸ (playing state)
