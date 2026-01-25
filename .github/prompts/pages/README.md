# Vi-En Reflex Trainer - UI Prompts Collection

Bộ prompts hoàn chỉnh để build toàn bộ app Vi-En Reflex Trainer với React + shadcn/ui.

## 📋 Danh sách Pages

### Public Pages (Guest + User)
1. **[landing.prompt.md](landing.prompt.md)** - Landing Page
   - Hero section với CTA
   - Feature showcase
   - How it works
   - Social proof + footer

2. **[auth.prompt.md](auth.prompt.md)** - Login/Register
   - Login form
   - Register form
   - Guest mode button
   - Token management

3. **[lessons.prompt.md](lessons.prompt.md)** - Lessons List
   - Search + filter
   - Lesson cards với progress
   - Pagination

4. **[lesson-detail.prompt.md](lesson-detail.prompt.md)** - Lesson Detail
   - Lesson info
   - Sentences table
   - Audio players
   - Start practice CTA

5. **[practice.prompt.md](practice.prompt.md)** - Practice Session ⭐
   - Main feature
   - Sentence card flip
   - Audio playback
   - Smart algorithm
   - Progress tracking

6. **[stats.prompt.md](stats.prompt.md)** - User Statistics (Auth required)
   - Overview cards
   - Progress by lesson
   - Practice charts
   - Achievements

### Admin Pages (Admin only)
7. **[admin-lessons.prompt.md](admin-lessons.prompt.md)** - Lessons Management
   - CRUD operations
   - Bulk actions
   - Data table

8. **[admin-sentences.prompt.md](admin-sentences.prompt.md)** - Sentences Management
   - CRUD operations
   - Bulk create (CSV/JSON)
   - Filter by lesson

## 🎯 Technology Stack

- **Frontend**: React 18 + TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **State**: React Context/Zustand
- **Routing**: React Router v6
- **HTTP**: Axios/Fetch
- **Audio**: HTML5 Audio API
- **Charts**: Recharts / Chart.js (for stats)
- **Forms**: React Hook Form + Zod
- **Animations**: Framer Motion (optional)
- **Illustrations**: unDraw, Storyset, Illustrations.co

## 🚀 Suggested Build Order

### Phase 1: Core Foundation (Week 1)
1. Landing page
2. Auth pages
3. Lessons list
4. Lesson detail

### Phase 2: Main Feature (Week 2)
5. Practice session ⭐
6. Stats dashboard

### Phase 3: Admin Panel (Week 3)
7. Admin lessons
8. Admin sentences

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/              # Reusable UI components (buttons, cards, modals)
│   │   ├── layout/          # Navbar, Footer, Layout wrappers
│   │   └── shared/          # Shared components (AudioPlayer, ProgressBar)
│   ├── pages/
│   │   ├── Landing.tsx
│   │   ├── Auth.tsx
│   │   ├── Lessons.tsx
│   │   ├── LessonDetail.tsx
│   │   ├── Practice.tsx
│   │   ├── Stats.tsx
│   │   └── admin/
│   │       ├── Lessons.tsx
│   │       └── Sentences.tsx
│   ├── lib/
│   │   ├── api.ts           # API client
│   │   ├── auth.ts          # Token management
│   │   └── utils.ts
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useAudio.ts
│   │   └── usePractice.ts
│   ├── types/
│   │   └── index.ts
│   ├── assets/
│   │   └── images/          # Illustrations, images
│   └── App.tsx
└── package.json
```

## 🔧 Setup Commands

```bash
# Create React app with Vite
npm create vite@latest frontend -- --template react-ts

# Install dependencies
npm install react-router-dom axios zustand react-hook-form zod recharts lucide-react

# Install Tailwind CSS
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Optional: Animation library
npm install framer-motion

# Optional: Confetti for celebrations
npm install canvas-confetti
```

## 🎨 Design System Guidelines

### General Principles
- **Design Flexibility**: Prompts cung cấp gợi ý, nhưng khuyến khích sáng tạo để UI đẹp hơn
- **Không cứng nhắc**: Tự do điều chỉnh layout, colors, spacing, animations
- **Visual Appeal**: Ưu tiên aesthetic và user experience
- **Images & Illustrations**: Luôn thêm visual elements để UI sinh động

### Get Design System
```bash
python3 .shared/ui-ux-pro-max/scripts/search.py "education language learning" --design-system -p "Vi-En Trainer"
```

### Stack-Specific Best Practices
```bash
# React guidelines
python3 .shared/ui-ux-pro-max/scripts/search.py "component hooks state" --stack react

# Tailwind patterns
python3 .shared/ui-ux-pro-max/scripts/search.py "card button form layout" --stack html-tailwind
```

### Resources
- **Icons**: [Lucide React](https://lucide.dev/)
- **Illustrations**: 
  - [unDraw](https://undraw.co) - Customizable illustrations
  - [Storyset](https://storyset.com) - Animated illustrations
  - [Illustrations.co](https://illustrations.co) - Free illustration library
- **Images**: [Unsplash](https://unsplash.com) - High-quality free photos
- **Patterns**: [Hero Patterns](https://heropatterns.com) - SVG background patterns
- **Gradients**: [UI Gradients](https://uigradients.com), [Mesh Gradients](https://meshgradient.com)

## 📚 API Documentation

- **Base URL**: `http://localhost:8000`
- **Swagger**: `http://localhost:8000/docs`
- **Postman**: `/postman/collections/Vi-En Reflex Trainer API.postman_collection.json`

## 🔐 Authentication Flow

1. User registers/logs in → Receive JWT tokens
2. Store in localStorage: `vi_en_token`, `vi_en_refresh`
3. Add to all API requests: `Authorization: Bearer {token}`
4. Auto-refresh 5 min before expiry
5. Logout → Clear localStorage + redirect to landing

## 🎵 Audio Handling

- Use HTML5 `<audio>` element
- Preload on page load: `<audio preload="auto">`
- Cache audio files in browser
- Show loading spinner during fetch
- Handle errors gracefully

## ✅ Quality Checklist

- [ ] Responsive: Mobile (375px) + Desktop (1440px)
- [ ] Dark mode support
- [ ] Loading states for all async operations
- [ ] Error handling with user-friendly messages
- [ ] Form validation with clear error messages
- [ ] Keyboard shortcuts (Practice page)
- [ ] Accessibility: ARIA labels, alt text, focus states
- [ ] Performance: Code splitting, lazy loading
- [ ] Images & Illustrations: Visual elements on every page
- [ ] Smooth animations & transitions
- [ ] Design flexibility: Không bị giới hạn bởi guidelines cứng

## 🎨 Design Quality Tips

1. **Always add visuals**: Empty states cần illustrations, headers cần images/gradients
2. **Flexible layouts**: Đừng fix cứng grid/spacing, điều chỉnh cho đẹp
3. **Color creativity**: Có thể thử nghiệm với gradients, color combinations
4. **Micro-interactions**: Thêm hover effects, transitions để UI sống động
5. **White space**: Đừng ngại dùng spacing generous để UI breathable

## 🎯 Next Steps

1. Copy prompt file vào editor
2. Chạy design system command
3. Build component theo template
4. Test với API backend
5. Move to next page

**Happy coding! 🚀**
