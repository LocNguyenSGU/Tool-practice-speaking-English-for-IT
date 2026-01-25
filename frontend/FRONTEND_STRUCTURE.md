# Frontend Structure - Vi-En Reflex Trainer

## 📚 Stack & Tools
- **Framework**: React 19 + TypeScript + Vite
- **Styling**: Tailwind CSS v4 (using `@import "tailwindcss"` syntax)
- **Routing**: React Router DOM v7
- **Icons**: Lucide React
- **Fonts**: Google Fonts (Baloo 2, Comic Neue)

## 🎨 Design System
- **Pattern**: Vibrant & Block-based
- **Colors**:
  - Primary: `#4F46E5` (indigo-600)
  - Secondary: `#818CF8` (indigo-400)
  - CTA: `#22C55E` (green-600)
  - Background: `#EEF2FF` (indigo-50)
- **Typography**:
  - Headings: `font-family: 'Baloo 2', cursive`
  - Body: `font-family: 'Comic Neue', cursive`
- **Effects**: Glassmorphism cards, smooth transitions (200-300ms)

## 📁 Project Structure

```
frontend/
├── src/
│   ├── main.tsx              # Entry point (renders <App />)
│   ├── App.tsx               # Router configuration
│   ├── App.css               # Global app styles (reset #root styles)
│   ├── index.css             # Tailwind imports + font declarations
│   │
│   ├── pages/                # Page components
│   │   ├── Landing.tsx       # Homepage (/)
│   │   ├── Auth.tsx          # Login/Register (/auth)
│   │   ├── ForgotPassword.tsx  # Forgot password flow
│   │   └── ResetPassword.tsx   # Reset password with token
│   │
│   ├── utils/                # Utility functions
│   │   └── auth.ts           # Token management, localStorage helpers
│   │
│   └── components/           # Reusable components (empty - to be added)
│
├── public/                   # Static assets
├── index.html               # HTML template with Google Fonts
├── vite.config.ts           # Vite config (SPA fallback enabled)
└── tailwind.config.js       # Tailwind custom colors
```

## 🗺️ Current Routes

| Path | Component | Status | Description |
|------|-----------|--------|-------------|
| `/` | `Landing` | ✅ Done | Homepage with hero, features, social proof |
| `/auth` | `Auth` | ✅ Done | Login/Register toggle form |
| `/forgot-password` | `ForgotPassword` | ✅ Done | Request password reset link |
| `/reset-password` | `ResetPassword` | ✅ Done | Reset password with token from email |
| `/lessons` | Placeholder | 🚧 TODO | Lessons list page |

## 🔐 Auth Flow

```
Landing (/) 
  → "Bắt đầu luyện tập" → /auth
  → "Thử ngay" → /lessons (guest mode)

Auth (/auth)
  → Login → Store token → /lessons
  → Register → Success → Switch to Login
  → "Quên mật khẩu?" → /forgot-password
  → "Tiếp tục không đăng ký" → /lessons

Forgot Password (/forgot-password)
  → Submit email → Success state
  → Email contains link → /reset-password?token=xxx

Reset Password (/reset-password?token=xxx)
  → Valid token → Form
  → Submit → Success → Auto redirect /auth (3s)
  → Invalid token → Show error + link to /forgot-password
```

## 📋 Checklist: Adding New Page

1. **Create page component**: `src/pages/YourPage.tsx`
   - Import `Link` from `react-router-dom` for navigation
   - Use design system colors and fonts
   - Add proper TypeScript types

2. **Add route in App.tsx**:
   ```tsx
   import YourPage from './pages/YourPage'
   // Add to Routes:
   <Route path="/your-path" element={<YourPage />} />
   ```

3. **Update navigation links**:
   - Use `<Link to="/your-path">` NOT `<a href>`
   - Ensure links from other pages point to new route

4. **Design guidelines**:
   - Container: `min-h-screen` for full height
   - Background: `bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50`
   - Cards: `bg-white/80 backdrop-blur-sm rounded-3xl shadow-2xl`
   - Buttons: `bg-gradient-to-r from-indigo-600 to-indigo-500`
   - Spacing: Use `space-y-3` or `space-y-4` for form elements
   - Icons: `strokeWidth={2.5}` for consistency

5. **Common patterns**:
   ```tsx
   // Headings
   <h1 style={{ fontFamily: "'Baloo 2', cursive" }}>Title</h1>
   
   // Body text
   <p style={{ fontFamily: "'Comic Neue', cursive" }}>Text</p>
   
   // Navigation button
   <Link to="/path" className="bg-gradient-to-r from-indigo-600 to-indigo-500 ...">
     Button Text
   </Link>
   
   // Input field
   <input className="pl-11 pr-4 py-2.5 rounded-xl border-2 ..." />
   ```

## 🔧 Important Config Files

### vite.config.ts
```ts
server: {
  historyApiFallback: true, // Enables SPA routing
}
```

### App.css
```css
#root {
  width: 100%;
  min-height: 100vh;
  margin: 0;
  padding: 0; /* No padding/max-width constraints */
}
```

### index.css
```css
@import "tailwindcss";
/* Font declarations using loaded Google Fonts */
```

## 🎯 Next Steps (TODO)

- [ ] Create Lessons page component
- [ ] Create Practice page component
- [ ] Add user dashboard
- [ ] Implement protected routes (auth guard)
- [ ] Add toast notifications (consider react-hot-toast)
- [ ] Create reusable form components
- [ ] Add loading states components
- [ ] Implement API error handling
- [ ] Add unit tests

## 📝 Notes

- **React Router v7**: Uses `Link` component for client-side navigation
- **Tailwind v4**: Some gradient classes changed (`bg-gradient-to-*` → `bg-linear-to-*` warnings OK)
- **Token Storage**: Using `localStorage` with keys: `vi_en_token`, `vi_en_refresh`, `vi_en_user`
- **API Base URL**: Currently hardcoded to `http://localhost:8000/api/v1`
- **Dev Server**: Port 5173 (check with `npm run dev` in frontend folder)
