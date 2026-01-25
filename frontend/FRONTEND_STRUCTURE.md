# Frontend Structure - Vi-En Reflex Trainer

> **Mục đích**: Ứng dụng học tiếng Anh-Việt qua phản xạ, hỗ trợ cả guest và authenticated users với practice tracking

## 📚 Stack & Tools
- **Framework**: React 19 + TypeScript + Vite
- **Styling**: Tailwind CSS v4 (using `@import "tailwindcss"` syntax)
- **Routing**: React Router DOM v7 (client-side routing)
- **Icons**: Lucide React
- **Fonts**: Google Fonts (Baloo 2, Comic Neue)
- **Audio**: HTML5 Audio API
- **State Management**: React Hooks (useState, useEffect, useCallback, useRef)
- **HTTP Client**: Native Fetch API

## 🎨 Design System
- **Pattern**: Vibrant & Block-based, Gamification elements
- **Colors**:
  - Primary: `#4F46E5` (indigo-600)
  - Secondary: `#818CF8` (indigo-400)
  - Success/CTA: `#22C55E` (green-600)
  - Warning: `#F59E0B` (orange-600)
  - Error: `#EF4444` (red-600)
  - Background: Gradient `from-indigo-50 via-purple-50 to-pink-50`
  - Dark mode: `dark:from-gray-900 dark:via-indigo-950 dark:to-purple-950`
- **Typography**:
  - Headings: `font-family: 'Baloo 2', cursive` (friendly, rounded)
  - Body: `font-family: 'Comic Neue', cursive` (playful, readable)
- **Effects**: 
  - Glassmorphism cards (`bg-white/90 backdrop-blur-xl`)
  - Smooth transitions (200-300ms)
  - Hover scale effects (`hover:scale-105`)
  - Confetti animation on completion
  - Progress bars with gradients

## 📁 Project Structure

```
frontend/
├── src/
│   ├── main.tsx              # Entry point (renders <App />)
│   ├── App.tsx               # Router configuration (BrowserRouter + Routes)
│   ├── App.css               # Global app styles (reset #root styles)
│   ├── index.css             # Tailwind imports + font declarations
│   │
│   ├── pages/                # Page components (1 file = 1 route)
│   │   ├── Landing.tsx       # ✅ Homepage (/) - Hero, Features, CTA
│   │   ├── Auth.tsx          # ✅ Login/Register (/auth) - Toggle form
│   │   ├── ForgotPassword.tsx  # ✅ Request password reset
│   │   ├── ResetPassword.tsx   # ✅ Reset password with token
│   │   ├── Lessons.tsx       # ✅ Lessons list (/lessons) - Grid, search, filter
│   │   ├── LessonDetail.tsx  # ✅ Lesson details (/lessons/:id) - Sentences list
│   │   └── Practice.tsx      # ✅ Practice mode (/practice?lesson_id=x) - CORE FEATURE
│   │
│   ├── utils/                # Utility functions
│   │   └── auth.ts           # Token management, localStorage, auto-refresh
│   │
│   ├── components/           # Reusable components (currently empty)
│   ├── assets/               # Static images, icons
│   └── styles/               # Additional styles (if needed)
│
├── public/                   # Static assets served as-is
├── index.html               # HTML template with Google Fonts CDN
├── vite.config.ts           # Vite config (SPA routing enabled)
├── tailwind.config.js       # Tailwind custom theme
├── tsconfig.json            # TypeScript config
└── package.json             # Dependencies and scripts
```

## 🗺️ Routes & Pages

| Path | Component | Auth Required | Description | Key Features |
|------|-----------|---------------|-------------|--------------|
| `/` | `Landing` | ❌ No | Homepage với hero section | Call-to-action, feature highlights, social proof |
| `/auth` | `Auth` | ❌ No | Login/Register toggle form | JWT auth, email validation, guest mode option |
| `/forgot-password` | `ForgotPassword` | ❌ No | Request password reset | Email submission, success feedback |
| `/reset-password?token=xxx` | `ResetPassword` | ❌ No | Reset password với token | Token validation, password confirm, auto-redirect |
| `/lessons` | `Lessons` | ❌ No (Guest OK) | Danh sách bài học | Search, filter, pagination, progress badges |
| `/lessons/:id` | `LessonDetail` | ❌ No (Guest OK) | Chi tiết bài học | Sentence preview, audio playback, practice stats |
| `/practice?lesson_id=x` | `Practice` | ❌ No (Guest OK) | **CORE**: Practice mode | Smart sentence selection, progress tracking, keyboard shortcuts |

### Practice Page - Chi tiết quan trọng

**File**: `src/pages/Practice.tsx` (~1100 lines - đã được tái cấu trúc)

**Chế độ hoạt động**:
- **Normal Mode**: Luyện tập theo thuật toán smart (authenticated) hoặc random (guest)
- **Review Mode**: Ôn lại tất cả câu theo thứ tự từ đầu đến cuối

**State Management**:
```typescript
// Core states
sentence: Sentence | null           // Câu hiện tại
progress: Progress | null            // Tiến độ (practiced/total)
practicedIds: Set<number>           // IDs đã practiced (localStorage cho guest, DB cho auth)
isReviewMode: boolean               // Đang ở chế độ ôn tập
reviewIndex: number                 // Index hiện tại trong review mode
allSentences: SentenceListItem[]    // Danh sách tất cả câu (cho sidebar)
showAnswer: boolean                 // Hiện/ẩn đáp án
playingAudio: 'vi' | 'en' | null   // Audio đang phát
isCompleted: boolean                // Đã hoàn thành bài học
```

**Helper Functions** (ngoài component để tránh re-render):
- `isAuthenticated()`: Check auth status
- `fetchWithAuth()`: Fetch với auto token refresh
- `loadPracticedIdsFromStorage()` / `savePracticedIdsToStorage()`: localStorage cho guest
- `mapToSentence()`: Convert API response to Sentence
- `calculateProgress()`: Tính % tiến độ

**Key Functions**:
- `fetchPracticedIds()`: Load practiced IDs từ backend (auth users)
- `fetchAllSentences()`: Load danh sách câu cho sidebar
- `loadNextSentence()`: Load câu tiếp theo (xử lý cả 2 modes)
- `recordPracticeAndNext()`: Ghi nhận + chuyển câu tiếp
- `skipSentence()`: Bỏ qua không ghi nhận
- `jumpToSentence()`: Nhảy đến câu cụ thể từ sidebar
- `startReviewMode()`: Bắt đầu chế độ ôn tập
- `triggerConfetti()`: Animation khi hoàn thành

**Features**:
- ✅ Dual mode: Authenticated (DB tracking) và Guest (localStorage)
- ✅ Smart sentence selection (least practiced first)
- ✅ Progress tracking với visual progress bar
- ✅ Sidebar danh sách câu với practiced indicators
- ✅ Audio playback (Vietnamese + English)
- ✅ Keyboard shortcuts (Space, E, Enter, Arrow keys)
- ✅ Review mode để ôn lại từ đầu
- ✅ Confetti animation khi hoàn thành
- ✅ Responsive design với mobile sidebar overlay
- ✅ Streak days badge (cho auth users)

**API Endpoints Used**:
- `GET /api/v1/practice/next?lesson_id=x`: Lấy câu tiếp theo
- `POST /api/v1/practice/record`: Ghi nhận đã practiced (auth only)
- `GET /api/v1/practice/practiced-ids?lesson_id=x`: Lấy IDs đã practiced
- `GET /api/v1/sentences?lesson_id=x`: Lấy tất cả câu
- `GET /api/v1/sentences/:id`: Lấy 1 câu cụ thể
- `GET /api/v1/audio/:id/:lang`: Stream audio file

## 🔐 Authentication & Authorization

### Auth Flow Diagram
```
Landing (/) 
  → "Bắt đầu luyện tập" → /auth
  → "Thử ngay" → /lessons (guest mode - không cần đăng nhập)

Auth (/auth)
  → Login Success → Store tokens → /lessons (với user info)
  → Register Success → Switch to Login tab
  → "Quên mật khẩu?" → /forgot-password
  → "Tiếp tục không đăng ký" → /lessons (guest mode)

Forgot Password (/forgot-password)
  → Submit email → Success message
  → Email contains reset link → /reset-password?token=xxx

Reset Password (/reset-password?token=xxx)
  → Valid token → Password reset form
  → Submit success → Auto redirect to /auth (3 seconds)
  → Invalid/expired token → Error message + link to /forgot-password
```

### Token Management (`utils/auth.ts`)

**Storage Keys**:
- `vi_en_token`: Access token (JWT)
- `vi_en_refresh`: Refresh token
- `vi_en_user`: User info (JSON)

**Main Functions**:
```typescript
// Store & Retrieve
storeTokens(accessToken, refreshToken)
getAccessToken(): string | null
getRefreshToken(): string | null
storeUser(user: User)
getUser(): User | null

// Session Management
isAuthenticated(): boolean
clearAuth()  // Xóa tất cả auth data

// Auto Token Refresh
refreshAccessToken(): Promise<string | null>
setupTokenRefresh(expiresIn: number)  // Auto refresh 5 phút trước khi hết hạn
```

**Token Refresh Strategy**:
- Tự động refresh khi access token sắp hết hạn (5 phút trước)
- Khi API trả về 401, thử refresh token một lần
- Nếu refresh fail → `clearAuth()` → user cần login lại
- `fetchWithAuth()` helper tự động xử lý retry logic

### Guest vs Authenticated

| Feature | Guest Mode | Authenticated Mode |
|---------|-----------|-------------------|
| Practice | ✅ Có thể luyện tập | ✅ Có thể luyện tập |
| Progress Tracking | ✅ localStorage only | ✅ Database persistent |
| Practiced IDs | ✅ localStorage | ✅ Backend API |
| Streak Days | ❌ Không | ✅ Có |
| Cross-device Sync | ❌ Không | ✅ Có |
| Stats API | ❌ 401 Unauthorized | ✅ Full access |

## 🏗️ Code Architecture & Patterns

### Component Organization Pattern

**Pages** (`src/pages/*.tsx`):
- Large, feature-complete components (500-1100 lines)
- Handle own data fetching, state management
- Use hooks extensively: `useState`, `useEffect`, `useCallback`, `useRef`
- Self-contained logic (không dùng global state management)

**Best Practices đã áp dụng**:
1. **Helper Functions Outside Component**: 
   - Tách logic không phụ thuộc state ra ngoài để tránh re-render
   - VD: `fetchWithAuth()`, `mapToSentence()`, `calculateProgress()`

2. **useCallback cho Functions**:
   - Wrap functions được pass xuống children hoặc dùng trong dependencies
   - Giảm unnecessary re-renders

3. **useRef cho Non-State Values**:
   - Audio elements, canvas, timeout IDs
   - Không trigger re-render khi thay đổi

4. **Type Safety**:
   - Tất cả interfaces được define rõ ràng
   - Tránh `any`, dùng proper types

5. **Error Handling**:
   - Try-catch cho tất cả async operations
   - Graceful fallback cho failed requests

### Data Fetching Pattern

```typescript
// Standard pattern used across app
const [data, setData] = useState<Type | null>(null);
const [isLoading, setIsLoading] = useState(true);
const [error, setError] = useState<string | null>(null);

useEffect(() => {
  const fetchData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(url);
      if (!response.ok) throw new Error('...');
      const data = await response.json();
      setData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };
  
  fetchData();
}, [dependencies]);
```

### localStorage Pattern (Guest Mode)

```typescript
// Practice.tsx example
const STORAGE_KEY = `practiced_${lessonId}`;

// Load on mount
const [practicedIds, setPracticedIds] = useState<Set<number>>(() => {
  const stored = localStorage.getItem(STORAGE_KEY);
  return stored ? new Set(JSON.parse(stored)) : new Set();
});

// Auto-save on change
useEffect(() => {
  if (practicedIds.size > 0) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify([...practicedIds]));
  }
}, [practicedIds]);
```

### API Integration Pattern

**Base URL**: `http://localhost:8000/api/v1`

**Authenticated Requests**:
```typescript
const response = await fetchWithAuth(url, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(data)
});

// fetchWithAuth tự động:
// 1. Add Authorization header
// 2. Handle 401 với token refresh
// 3. Retry request sau khi refresh
// 4. Clear auth nếu refresh fail
```

**Guest Requests** (không cần auth):
```typescript
const response = await fetch(url);
// Không cần header, backend cho phép public access
```

## 📋 Checklist: Adding New Page

1. **Create page component**: `src/pages/YourPage.tsx`
   - Import `useNavigate`, `Link` from `react-router-dom`
   - Define TypeScript interfaces cho data structures
   - Use design system colors and fonts
   - Implement loading, error, and success states

2. **Add route in App.tsx**:
   ```tsx
   import YourPage from './pages/YourPage'
   // Add to Routes:
   <Route path="/your-path" element={<YourPage />} />
   ```

3. **Update navigation links** across app:
   - Use `<Link to="/your-path">` NOT `<a href>` (client-side routing)
   - Update Landing, Auth, Lessons pages nếu cần
   - Ensure breadcrumbs/back buttons work correctly

4. **Design guidelines**:
   - Container: `min-h-screen` for full height
   - Background: `bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50`
   - Dark mode: `dark:from-gray-900 dark:via-indigo-950 dark:to-purple-950`
   - Cards: `bg-white/90 backdrop-blur-xl rounded-3xl shadow-2xl`
   - Buttons: `bg-gradient-to-r from-indigo-600 to-purple-600`
   - Spacing: Use `space-y-3` or `space-y-4` for form elements
   - Icons: `strokeWidth={2.5}` for consistency
   - Borders: `border-4` cho emphasis, `border-2` cho subtle

5. **Common component patterns**:
   ```tsx
   // Page Container
   <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 dark:from-gray-900 dark:via-indigo-950 dark:to-purple-950 p-4">
   
   // Glassmorphism Card
   <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-xl rounded-3xl p-8 shadow-2xl border-4 border-indigo-100 dark:border-indigo-900/50">
   
   // Headings
   <h1 className="text-3xl font-bold text-gray-900 dark:text-white" style={{ fontFamily: "'Baloo 2', cursive" }}>
     Title
   </h1>
   
   // Body text
   <p className="text-gray-600 dark:text-gray-400" style={{ fontFamily: "'Comic Neue', cursive" }}>
     Text content
   </p>
   
   // Primary Button
   <button className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white rounded-xl font-bold transition-all duration-200 cursor-pointer shadow-lg hover:shadow-xl transform hover:scale-105">
     Click Me
   </button>
   
   // Link Button
   <Link 
     to="/path" 
     className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white rounded-xl font-bold transition-all duration-200"
   >
     <Icon size={20} />
     Go to Page
   </Link>
   
   // Input field
   <input 
     type="text"
     className="w-full pl-11 pr-4 py-2.5 rounded-xl border-2 border-gray-300 dark:border-gray-600 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 dark:bg-gray-700 dark:text-white transition-all duration-200"
     placeholder="Enter text..."
   />
   
   // Loading Skeleton
   <div className="animate-pulse">
     <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded-lg mb-4 w-3/4"></div>
     <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded-lg w-1/2"></div>
   </div>
   ```

6. **Accessibility**:
   - Add `aria-label` cho icon buttons
   - Use semantic HTML (`<nav>`, `<main>`, `<section>`)
   - Ensure keyboard navigation works
   - Add loading states với text feedback

## 🔧 Important Config Files

### vite.config.ts
```ts
export default defineConfig({
  server: {
    historyApiFallback: true,  // Enables SPA routing - fallback to index.html
    port: 5173
  },
  plugins: [react()]
})
```

### App.css
```css
#root {
  width: 100%;
  min-height: 100vh;
  margin: 0;
  padding: 0;  /* No max-width constraints - full width app */
}
```

### index.css
```css
@import "tailwindcss";

/* Font declarations - must match fonts loaded in index.html */
```

### tailwind.config.js
```js
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',  // Enable dark mode via class
  theme: {
    extend: {
      // Custom colors, fonts, animations can be added here
    }
  }
}
```

## 🎯 Development Status

### Completed Features ✅
- [x] Landing page với hero section
- [x] Auth system (Login/Register/Forgot/Reset)
- [x] Lessons listing với search, filter, pagination
- [x] Lesson detail page với sentence preview
- [x] **Practice mode** (Core feature - fully functional)
  - [x] Normal practice mode (smart selection)
  - [x] Review mode (ôn lại từ đầu)
  - [x] Guest mode support (localStorage)
  - [x] Authenticated mode (DB tracking)
  - [x] Audio playback
  - [x] Keyboard shortcuts
  - [x] Progress tracking
  - [x] Sidebar với practiced indicators
  - [x] Confetti animation
  - [x] Responsive mobile layout

### TODO / Future Enhancements 🚧
- [ ] User dashboard (statistics, streaks, achievements)
- [ ] Protected routes với auth guard component
- [ ] Toast notifications library (react-hot-toast recommended)
- [ ] Reusable form components (Input, Button, Card)
- [ ] Global loading spinner component
- [ ] Better error handling với error boundary
- [ ] Unit tests (Vitest + React Testing Library)
- [ ] E2E tests (Playwright)
- [ ] Settings page (audio speed, auto-play, theme)
- [ ] Leaderboard / Social features
- [ ] Spaced repetition algorithm
- [ ] Export/Import progress
- [ ] Offline support (PWA)

## 📝 Important Notes & Best Practices

### React Router v7
- Uses `Link` component for client-side navigation (không reload page)
- `useNavigate()` hook cho programmatic navigation
- `useParams()` để lấy dynamic route params
- `useSearchParams()` để lấy query strings

### Tailwind CSS v4
- Some class names changed: `bg-gradient-to-*` → `bg-linear-to-*` (warnings are OK, old syntax still works)
- `flex-shrink-0` → `shrink-0` (new recommended syntax)
- Dark mode: use `dark:` prefix (e.g., `dark:bg-gray-800`)

### Token & Auth Storage
- **localStorage keys**: `vi_en_token`, `vi_en_refresh`, `vi_en_user`
- Never store sensitive data in localStorage (tokens are OK for this use case)
- Always clear auth on logout or token refresh failure
- Check `isAuthenticated()` before protected actions

### API Communication
- **Base URL**: `http://localhost:8000/api/v1` (should be env variable in production)
- **Auth header**: `Authorization: Bearer {token}`
- **Content-Type**: `application/json` for POST/PUT
- Always handle 401 errors (token expired)
- Implement retry logic for failed requests

### Performance Tips
- Use `useCallback` cho functions passed to children
- Use `useMemo` cho expensive computations
- Move helper functions outside component khi không cần access state
- Lazy load images và audio files
- Debounce search inputs

### State Management Guidelines
- **Local state**: `useState` cho UI state (modals, dropdowns, forms)
- **Server state**: Fetch on mount, store in state, handle loading/error
- **Derived state**: Calculate from existing state, không cần separate state
- **Refs**: Dùng cho DOM access và values không trigger re-render

### Error Handling Pattern
```typescript
try {
  // API call
} catch (err) {
  setError(err instanceof Error ? err.message : 'An error occurred');
  // Optional: Log to error tracking service
}
```

### Code Style
- **Naming**: camelCase cho variables/functions, PascalCase cho components
- **File naming**: PascalCase cho component files (Landing.tsx)
- **Constants**: UPPERCASE_SNAKE_CASE
- **Interfaces**: PascalCase, no `I` prefix
- **Async functions**: Always use try-catch
- **Comments**: Explain WHY, not WHAT (code should be self-explanatory)

## 🐛 Common Issues & Solutions

### Issue: Routes không hoạt động (404 on refresh)
**Solution**: Đảm bảo `vite.config.ts` có `historyApiFallback: true`

### Issue: Audio không play
**Solution**: Check audio URL format, ensure server is serving files correctly

### Issue: Token expired liên tục
**Solution**: Kiểm tra `setupTokenRefresh()` được gọi sau login, verify expiry time

### Issue: LocalStorage data bị mất
**Solution**: 
- Check browser privacy settings
- Don't clear localStorage manually
- Verify storage keys match constants

### Issue: Dark mode không hoạt động
**Solution**: Add `dark` class to `<html>` element, ensure Tailwind config có `darkMode: 'class'`

### Issue: TypeScript errors sau khi thêm dependencies
**Solution**: Run `npm install @types/{package-name}` cho type definitions

## 🔄 Recent Major Changes

### 2026-01-25: Practice Page Refactoring
- Loại bỏ unnecessary refs và sync useEffects
- Tách helper functions ra ngoài component
- Đơn giản hóa review mode logic (dùng array index thay vì order_index)
- Fix type errors và clean up dependencies
- Thêm `fetchPracticedIds()` API endpoint
- Cải thiện error handling và loading states

### Key Improvements:
1. **Better Performance**: Giảm re-renders bằng cách tách helpers ra ngoài
2. **Cleaner Code**: Từ 4 sync useEffects xuống 0
3. **Type Safety**: Fix tất cả `any` types
4. **Maintainability**: Clear separation of concerns

## 📚 Resources & References

- [React Docs](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [React Router v7](https://reactrouter.com/)
- [Lucide Icons](https://lucide.dev/icons/)
- [Vite Guide](https://vitejs.dev/guide/)

## 🤝 Contributing Guidelines

When adding new features:
1. Follow existing code patterns and structure
2. Add TypeScript types for all data
3. Implement loading and error states
4. Test both guest and authenticated modes
5. Ensure responsive design (mobile, tablet, desktop)
6. Add keyboard shortcuts where appropriate
7. Document complex logic with comments
8. Update this FRONTEND_STRUCTURE.md file
