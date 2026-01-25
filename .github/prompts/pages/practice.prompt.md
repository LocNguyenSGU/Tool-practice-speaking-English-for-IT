# Practice Session Page (MAIN FEATURE)

## Project Info
- **Tên dự án**: Vi-En Reflex Trainer
- **Loại sản phẩm**: Education App
- **Ngành**: Language Learning
- **Stack**: react + tailwind + lucide-react

## Page/Component
- **Tên page**: Practice Session
- **Mô tả ngắn**: Màn hình luyện tập chính - hiển thị câu tiếng Việt, user đọc/nói tiếng Anh, play audio để check, record practice, next sentence với smart algorithm.

## Features
1. **Sentence Card** (center focus):
   - Hiển thị câu tiếng Việt (font size lớn)
   - Câu tiếng Anh ẩn (click "Show Answer" để reveal)
   - Audio buttons: 🔊 Vi, 🔊 En
2. **Progress Bar** (top): "5/50 câu trong bài học này"
3. **Action Buttons**:
   - "Hiện đáp án" (toggle show/hide English)
   - "Đã thuộc" → Record practice + Next sentence
   - "Bỏ qua" → Next sentence (không record)
4. **Navigation**: 
   - Previous button (nếu có history)
   - Exit button → Back to lesson detail
5. **Streak Badge** (corner): "🔥 Streak: 7 ngày" (authenticated)
6. **Keyboard shortcuts**: 
   - Space: Play audio
   - Enter: Show answer
   - 1: Đã thuộc
   - 2: Bỏ qua

## API Endpoints

### GET /api/v1/practice/next
- **Query params**: `lesson_id={id}&exclude_recent=true`
- **Response**:
```json
{
  "sentence": {
    "id": 1,
    "lesson_id": 1,
    "vi_text": "Xin chào",
    "en_text": "Hello",
    "vi_audio_url": "/api/v1/audio/1/vi",
    "en_audio_url": "/api/v1/audio/1/en",
    "order_index": 1,
    "created_at": "2026-01-20T10:00:00Z",
    "updated_at": "2026-01-20T10:00:00Z"
  },
  "progress": {
    "practiced_count": 5,
    "total_in_lesson": 50,
    "percentage": 10
  }
}
```

### POST /api/v1/practice/record
- **Request**:
```json
{
  "sentence_id": 1
}
```
- **Response**:
```json
{
  "success": true,
  "practiced_count": 6,
  "total_practice_count": 101,
  "streak_days": 7
}
```

### GET /api/v1/audio/{sentence_id}/{lang}
- **Response**: MP3 audio file

### GET /api/v1/practice/stats (authenticated)
- **Response**:
```json
{
  "total_practiced": 100,
  "total_practice_count": 500,
  "recent_practiced_count": 20
}
```

## UI States
- [x] Loading state: Skeleton card cho sentence
- [x] Empty state: "Bài học chưa có câu nào" hoặc "Bạn đã hoàn thành tất cả câu!" với confetti
- [x] Error state: Error card với retry button
- [x] Success state: Confetti animation khi hoàn thành lesson

## Style Preferences
- **Mood**: focused, calm, minimal (avoid distractions)
- **Dark mode**: both (prefer dark for focus)
- **Design flexibility**: Tự do thiết kế card layout để tạo trải nghiệm học tập tốt nhất, có thể thử card 3D, animated transitions
- **Special effects**:
  - Card flip animation khi show answer (hoặc slide/fade)
  - Audio button pulse khi playing
  - Progress bar smooth animation
  - Confetti khi complete lesson
  - Subtle background gradient hoặc ambient animation
  - Floating elements (optional)

## Images & Illustrations
- **Background**: 
  - Subtle gradient mesh
  - Abstract learning-themed patterns
  - Ambient animated shapes (very subtle, không distract)
- **Sentence card**: 
  - Language flags (🇻🇳 🇺🇸) decorative
  - Audio waveform visualization (optional)
- **Completion state**: 
  - Success illustration (celebration, trophy, medal)
  - Confetti animation + achievement badge
- **Empty state**: "No more sentences" với friendly illustration
- **Sources**:
  - Illustrations: unDraw (learning, achievement themes)
  - Patterns: Subtle gradients, geometric patterns
  - Confetti: canvas-confetti library

## Component Structure
```
pages/Practice.tsx
├── Header
│   ├── ProgressBar (5/50)
│   ├── StreakBadge (🔥 7 ngày)
│   └── ExitButton
├── SentenceCard (center focus)
│   ├── VietnameseText (large font)
│   ├── EnglishText (collapsible)
│   └── AudioButtons
│       ├── PlayViButton
│       └── PlayEnButton
├── ActionButtons
│   ├── ShowAnswerButton (toggle)
│   ├── MasteredButton (primary)
│   └── SkipButton (secondary)
└── NavigationButtons
    ├── PreviousButton
    └── Hints/Tips (optional)
```

## Practice Logic
1. **Load sentence**: GET /practice/next
2. **Show Vietnamese**: User attempts to translate mentally
3. **Play audio**: Listen to pronunciation
4. **Show answer**: Reveal English text
5. **Record practice**: POST /practice/record (if mastered)
6. **Next sentence**: Load next via smart algorithm

## Smart Algorithm (Backend)
- Authenticated: Filter recently practiced (<5 min), prioritize least practiced
- Guest: Random selection from lesson

## Completion Flow
- When `practiced_count >= total_in_lesson`:
  - Show confetti animation
  - Display completion modal
  - Options: "Ôn lại từ đầu" | "Về danh sách bài"

## Keyboard Shortcuts
- `Space`: Play audio
- `Enter`: Toggle show answer
- `1` or `Y`: Mastered
- `2` or `N`: Skip
- `Esc`: Exit to lesson detail
