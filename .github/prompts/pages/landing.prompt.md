# Landing Page - Vi-En Reflex Trainer

## Project Info
- **Tên dự án**: Vi-En Reflex Trainer
- **Loại sản phẩm**: Education App / Landing Page
- **Ngành**: Language Learning
- **Stack**: react + tailwind + lucide-react

## Page/Component
- **Tên page**: Landing Page
- **Mô tả ngắn**: Trang giới thiệu chính, thu hút người dùng đăng ký hoặc thử dùng (guest mode). Truyền tải giá trị: luyện phản xạ tiếng Anh qua câu Việt-Anh.

## Features
1. Hero section với headline hấp dẫn + CTA "Bắt đầu luyện tập" (dẫn đến /lessons)
2. Feature showcase: Hybrid mode (guest + user), Smart algorithm, Audio TTS, Progress tracking
3. How it works: 3 bước đơn giản (chọn lesson → luyện tập → theo dõi tiến độ)
4. Social proof: Stats (100+ lessons, 1000+ sentences) hoặc testimonials
5. CTA section cuối: "Đăng ký miễn phí" hoặc "Thử ngay không cần đăng ký"
6. Footer: Links đến /login, /register, /lessons

## API Endpoints

### GET /health
- **Response**:
```json
{
  "status": "ok",
  "timestamp": "2026-01-25T10:00:00Z"
}
```

### GET /api/v1/lessons (preview data)
- **Query params**: `page=1&limit=3` (hiển thị 3 lessons mẫu)
- **Response**:
```json
{
  "items": [
    {
      "id": 1,
      "title": "Greetings",
      "description": "Basic greetings",
      "order_index": 1,
      "is_active": true
    }
  ],
  "pagination": {
    "total_items": 100
  }
}
```

## UI States
- [x] Loading state: Skeleton cho hero section và features
- [ ] Empty state: N/A (static content)
- [ ] Error state: Fallback nếu API health check fail
- [x] Success state: Smooth scroll animations, fade-in effects

## Style Preferences
- **Mood**: modern, professional, inspiring
- **Dark mode**: both (default theo system preference)
- **Design flexibility**: Tự do điều chỉnh layout, spacing, colors để tạo landing page ấn tượng và độc đáo
- **Special effects**: 
  - Gradient backgrounds (có thể animated)
  - Smooth scroll animations
  - Card hover effects (lift + shadow hoặc sáng tạo khác)
  - Icon animations (pulse, bounce, rotate on hover)
  - Parallax scrolling (optional)

## Images & Illustrations
- **Hero section**: 
  - Background image: Learning/education themed từ [Unsplash](https://unsplash.com/s/photos/learning)
  - Hoặc: Gradient + animated shapes/orbs
  - Illustration: Student studying hoặc language learning concept
- **Feature cards**: Icon-based (Lucide React) với gradient backgrounds
- **How it works**: Numbered steps với illustrations cho mỗi bước
- **Social proof**: Avatar placeholders hoặc testimonial cards với profile images
- **Sources**:
  - Hero images: Unsplash (keywords: education, learning, study, language)
  - Illustrations: [unDraw](https://undraw.co), [Storyset](https://storyset.com)
  - Patterns: [Hero Patterns](https://heropatterns.com)

## Design Guidelines
- **Hero**: Full viewport height với gradient background hoặc hero image
- **Features**: Grid layout linh hoạt (có thể 2x2, 3 columns, hoặc sáng tạo khác)
- **How it works**: Timeline/stepper với icons/illustrations
- **CTA buttons**: Primary (nổi bật), Secondary (subtle)
- **Typography**: Headings bold, body text readable (16px+)
- **Spacing**: Generous padding/margins, breathable layout
- **Flexibility**: Tự do sắp xếp sections, thay đổi thứ tự nếu hợp lý hơn

## Component Structure
```
pages/Landing.tsx
├── HeroSection
│   ├── Headline
│   ├── Subheading
│   └── CTAButtons
├── FeaturesSection
│   └── FeatureCard (x4)
├── HowItWorksSection
│   └── Step (x3)
├── StatsSection (social proof)
└── CTASection + Footer
```
