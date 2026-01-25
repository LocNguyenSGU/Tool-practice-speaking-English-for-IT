# User Statistics Dashboard

## Project Info
- **Tên dự án**: Vi-En Reflex Trainer
- **Loại sản phẩm**: Education App
- **Ngành**: Language Learning
- **Stack**: react + tailwind + lucide-react

## Page/Component
- **Tên page**: Statistics Dashboard
- **Mô tả ngắn**: Dashboard cá nhân hiển thị thống kê luyện tập, streak, progress theo lesson, chart xu hướng.

## Features
1. **Overview Cards** (top):
   - Total practiced sentences
   - Total practice sessions
   - Current streak days
   - Recent practice count (7 days)
2. **Progress by Lesson** (table):
   - Lesson title
   - Practiced/Total sentences
   - Progress bar
   - Last practiced date
3. **Practice Chart** (optional):
   - Line chart: Practice count theo ngày (7-30 days)
   - Bar chart: Practice count theo lesson
4. **Achievements/Badges** (optional):
   - First practice
   - 7-day streak
   - 100 sentences mastered

## API Endpoints

### GET /api/v1/practice/stats
- **Query params**: `lesson_id={id}` (optional, filter by lesson)
- **Response**:
```json
{
  "total_practiced": 100,
  "total_practice_count": 500,
  "recent_practiced_count": 20
}
```

### GET /api/v1/auth/me (user info + streak)
- **Response**:
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "johndoe",
  "is_active": true,
  "is_admin": false,
  "created_at": "2026-01-20T10:00:00Z",
  "updated_at": "2026-01-25T10:00:00Z"
}
```

### GET /api/v1/lessons (to calculate progress by lesson)
- **Response**:
```json
{
  "items": [
    {
      "id": 1,
      "title": "Basic Greetings",
      "description": "..."
    }
  ]
}
```

### GET /api/v1/practice/stats?lesson_id={id} (foreach lesson)
- Calculate practiced/total for each lesson

## UI States
- [x] Loading state: Skeleton cards + skeleton chart
- [x] Empty state: "Bạn chưa luyện tập câu nào" với CTA "Bắt đầu ngay"
- [x] Error state: Error card với retry
- [x] Success state: Animated numbers count-up, smooth charts

## Style Preferences
- **Mood**: motivating, achievement-focused, colorful
- **Dark mode**: both
- **Design flexibility**: Bạn được khuyến khích sáng tạo và điều chỉnh layout/spacing/colors để UI đẹp và hợp lý, không cần tuân thủ 100% các guideline cứng nhắc
- **Special effects**:
  - Number count-up animation (0 → actual value)
  - Progress bar animated fill
  - Chart smooth transitions
  - Badge glow effect
  - Confetti on new achievement

## Images & Illustrations
- **Achievement badges**: Sử dụng SVG icons với gradient fills
- **Empty state**: Thêm illustration vui nhộn (có thể dùng undraw.co, illustrations.co, hoặc design custom)
- **Background decorations**: Subtle geometric patterns hoặc gradient orbs
- **Chart placeholders**: Skeleton với shimmer effect
- **Sources**:
  - Icons: Lucide React (đã có sẵn)
  - Illustrations: [unDraw](https://undraw.co), [Illustrations.co](https://illustrations.co), [Storyset](https://storyset.com)
  - Patterns: [Hero Patterns](https://heropatterns.com)
  - Images: [Unsplash](https://unsplash.com) (education, learning themes)

## Component Structure
```
pages/Stats.tsx
├── Header "Thống kê của bạn"
├── OverviewCards (grid - responsive, tự do điều chỉnh layout)
│   ├── StatCard (Total practiced)
│   ├── StatCard (Practice sessions)
│   ├── StatCard (Streak days) 🔥
│   └── StatCard (Recent count)
├── LessonProgressSection
│   ├── SectionTitle "Tiến độ theo bài học"
│   └── LessonProgressTable (custom table, không cần dùng component library)
│       └── LessonProgressRow (map lessons)
│           ├── LessonTitle
│           ├── ProgressText "20/50"
│           ├── ProgressBar (custom with gradient)
│           └── LastPracticed
└── PracticeChartSection (optional)
    ├── SectionTitle "Lịch sử luyện tập"
    └── Chart (có thể dùng recharts, chart.js, hoặc custom SVG)
```

## Design Flexibility Note
- **Layout**: Tự do sắp xếp lại cards, spacing, grid columns để đạt visual balance tốt nhất
- **Colors**: Có thể điều chỉnh màu sắc, gradients để phù hợp với tổng thể
- **Typography**: Tự do chọn font sizes, weights phù hợp, không bị giới hạn
- **Animations**: Thêm micro-interactions để tăng engagement
- **Spacing**: Sử dụng spacing hợp lý (không quá chật, không quá rộng)

## Data Calculation
1. Load user info: GET /auth/me
2. Load all lessons: GET /lessons
3. Foreach lesson:
   - GET /practice/stats?lesson_id={id}
   - Calculate practiced/total ratio
4. Aggregate global stats:
   - Sum total_practiced across all lessons
   - Calculate average progress
   - Recent practice trend

## Achievements Logic (Frontend)
- **First Practice**: total_practiced >= 1
- **7-Day Streak**: streak_days >= 7
- **30-Day Streak**: streak_days >= 30
- **100 Sentences**: total_practiced >= 100
- **All Lessons**: All lessons have 100% progress

## Chart Data (optional, if backend supports)
- Backend can add new endpoint: GET /practice/history?days=7
- Returns array of {date, count} for line chart
