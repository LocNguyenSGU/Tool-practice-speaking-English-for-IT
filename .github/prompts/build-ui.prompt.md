# Build UI - Optimized Prompt Template

> **Mục đích**: Template chuẩn để AI tự động build UI từ mô tả tính năng + API specs

---

## 🎯 PROMPT TEMPLATE

Copy và điền thông tin vào template sau:

```markdown
## Project Info
- **Tên dự án**: [Tên app/website]
- **Loại sản phẩm**: [SaaS | E-commerce | Dashboard | Landing | Portfolio | Mobile App]
- **Ngành**: [Fintech | Healthcare | Education | Beauty | Gaming | ...]
- **Stack**: [html-tailwind | react | nextjs | vue | svelte] (mặc định: html-tailwind)

## Page/Component
- **Tên page**: [Login | Dashboard | Product List | ...]
- **Mô tả ngắn**: [1-2 câu mô tả chức năng chính]

## Features (Liệt kê tính năng)
1. [Feature 1]
2. [Feature 2]
3. [Feature 3]

## API Endpoints
### [Method] /api/endpoint
- **Request**:
```json
{
  "field": "type"
}
```
- **Response**:
```json
{
  "field": "type"
}
```

## UI States
- [ ] Loading state
- [ ] Empty state  
- [ ] Error state
- [ ] Success state

## Style Preferences (optional)
- **Mood**: [minimal | playful | professional | elegant | bold]
- **Dark mode**: [yes | no | both]
- **Special effects**: [glassmorphism | gradients | shadows | animations]
```

---

## 📝 VÍ DỤ HOÀN CHỈNH

```markdown
## Project Info
- **Tên dự án**: Vi-En Reflex Trainer
- **Loại sản phẩm**: Education App
- **Ngành**: Language Learning
- **Stack**: html-tailwind

## Page/Component
- **Tên page**: Practice Session
- **Mô tả ngắn**: Màn hình luyện tập câu tiếng Việt-Anh với audio và tracking progress

## Features
1. Hiển thị câu tiếng Việt, người dùng nói/gõ tiếng Anh
2. Nút play audio cho cả 2 ngôn ngữ
3. Progress bar hiển thị tiến độ trong lesson
4. Nút Next/Previous để chuyển câu
5. Badge hiển thị streak count

## API Endpoints

### GET /api/v1/practice/next
- **Query params**: `lesson_id`, `exclude_recent`
- **Response**:
```json
{
  "sentence": {
    "id": 1,
    "vi_text": "Xin chào",
    "en_text": "Hello",
    "vi_audio_url": "/api/v1/audio/1/vi",
    "en_audio_url": "/api/v1/audio/1/en"
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
  "new_count": 6
}
```

### GET /api/v1/practice/stats
- **Response**:
```json
{
  "total_practiced": 100,
  "total_practice_count": 500,
  "recent_practiced_count": 20
}
```

## UI States
- [x] Loading state: Skeleton loader cho sentence card
- [x] Empty state: "Chưa có câu nào trong lesson này"
- [x] Error state: Toast notification với retry button
- [x] Success state: Confetti animation khi hoàn thành lesson

## Style Preferences
- **Mood**: professional, clean
- **Dark mode**: both (light mặc định)
- **Special effects**: subtle shadows, smooth transitions
```

---

## 🔧 AGENT WORKFLOW (Nội bộ)

Khi nhận prompt theo template trên, AI sẽ tự động:

### Step 1: Generate Design System
```bash
python3 .shared/ui-ux-pro-max/scripts/search.py "<product> <industry> <mood>" --design-system -p "<Project Name>"
```

### Step 2: Get Stack Guidelines
```bash
python3 .shared/ui-ux-pro-max/scripts/search.py "form button card layout" --stack <stack>
```

### Step 3: Build Components
1. Parse API response → Extract data types
2. Map features → UI components
3. Apply design system → Colors, typography, spacing
4. Implement states → Loading, empty, error, success
5. Add interactions → Hover, click, transitions

### Step 4: Output Structure
```
components/
├── PracticeCard.html      # Main component
├── AudioButton.html       # Reusable audio player
├── ProgressBar.html       # Progress indicator
└── StatsWidget.html       # Statistics display
```

---

## ✅ QUALITY CHECKLIST (Auto-verify)

### Visual
- [ ] Không dùng emoji làm icon (dùng Heroicons/Lucide)
- [ ] Icons đồng nhất kích thước (w-5 h-5 hoặc w-6 h-6)
- [ ] Hover states không gây layout shift
- [ ] Text contrast đạt WCAG AA (4.5:1)

### Interaction
- [ ] Tất cả elements clickable có `cursor-pointer`
- [ ] Transitions smooth (150-300ms)
- [ ] Focus states visible cho keyboard nav
- [ ] Loading states cho async operations

### Responsive
- [ ] Mobile first (375px base)
- [ ] Breakpoints: sm(640) md(768) lg(1024) xl(1280)
- [ ] No horizontal scroll on mobile
- [ ] Touch targets ≥ 44px

### Accessibility
- [ ] All images có alt text
- [ ] Form inputs có labels
- [ ] ARIA labels cho interactive elements
- [ ] `prefers-reduced-motion` respected

---

## 🚀 QUICK START

**Minimal prompt** (khi cần nhanh):

```markdown
Build UI cho [Tên page]

Features:
- [Feature 1]
- [Feature 2]

API Response:
```json
{ ... }
```

Stack: html-tailwind
```

**Full prompt** (khi cần chất lượng cao):

Dùng template đầy đủ ở trên với tất cả sections.

---

## 📚 REFERENCE COMMANDS

```bash
# Design system đầy đủ
python3 .shared/ui-ux-pro-max/scripts/search.py "education language learning app" --design-system -p "Vi-En Trainer"

# Lưu design system
python3 .shared/ui-ux-pro-max/scripts/search.py "education app professional" --design-system --persist -p "Vi-En Trainer"

# Stack guidelines
python3 .shared/ui-ux-pro-max/scripts/search.py "card button form audio" --stack html-tailwind

# UX best practices
python3 .shared/ui-ux-pro-max/scripts/search.py "animation loading accessibility" --domain ux

# Chart types (nếu có dashboard)
python3 .shared/ui-ux-pro-max/scripts/search.py "progress streak timeline" --domain chart
```

---

## 💡 TIPS

1. **API-first**: Luôn cung cấp API response structure → AI biết data shape để render
2. **State complete**: Liệt kê đủ 4 states (loading, empty, error, success)
3. **Specific keywords**: "professional SaaS dashboard" > "app"
4. **One page at a time**: Build từng page, không build cả app 1 lúc
5. **Iterate**: Nếu output chưa đúng ý, describe lại cụ thể hơn
