import { useEffect, useState } from 'react';
import { 
  BookOpen, 
  Zap, 
  BarChart3, 
  Users, 
  ArrowRight,
  Volume2,
  Brain,
  Target,
  CheckCircle2,
  TrendingUp,
  Award,
  Mouse
} from 'lucide-react';

export default function Landing() {
  const [isVisible, setIsVisible] = useState(false);
  const [stats, setStats] = useState({ lessons: 0, sentences: 0, users: 0 });

  useEffect(() => {
    setIsVisible(true);
    // Animate stats counting
    const timer = setTimeout(() => {
      setStats({ lessons: 100, sentences: 1000, users: 500 });
    }, 500);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-indigo-100 to-indigo-50">
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center px-4 py-20 overflow-hidden">
        {/* Animated Background Pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-20 left-10 w-72 h-72 bg-primary rounded-full mix-blend-multiply filter blur-3xl animate-pulse"></div>
          <div className="absolute top-40 right-10 w-72 h-72 bg-secondary rounded-full mix-blend-multiply filter blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
          <div className="absolute bottom-20 left-1/2 w-72 h-72 bg-cta rounded-full mix-blend-multiply filter blur-3xl animate-pulse" style={{ animationDelay: '2s' }}></div>
        </div>

        <div className={`relative z-10 max-w-6xl mx-auto text-center transition-all duration-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
          {/* Badge */}
          <div className="inline-flex items-center gap-2 bg-white/90 backdrop-blur-sm px-6 py-3 rounded-full shadow-lg mb-8 border-3 border-primary/20">
            <Zap className="w-5 h-5 text-cta animate-pulse" />
            <span className="text-sm font-bold text-gray-900">Phương pháp mới: Luyện phản xạ, không học vẹt!</span>
          </div>

          {/* Headline */}
          <h1 className="text-5xl md:text-7xl font-bold text-gray-900 mb-6 leading-tight">
            Luyện phản xạ <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary via-secondary to-indigo-600">tiếng Anh</span> hiệu quả
          </h1>
          
          <p className="text-xl md:text-2xl text-gray-700 mb-12 max-w-3xl mx-auto leading-relaxed">
            Chuyển đổi nhanh từ Việt sang Anh với <strong className="text-primary">100+ bài học</strong>, <strong className="text-cta">1000+ câu</strong>, audio TTS và thuật toán thông minh
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
            <button className="group bg-gradient-to-r from-indigo-600 to-indigo-500 text-white px-10 py-5 rounded-2xl font-bold text-lg shadow-2xl hover:shadow-indigo-500/50 transition-all duration-300 hover:scale-105 cursor-pointer border-2 border-indigo-400">
              <span className="flex items-center gap-3 justify-center">
                Bắt đầu luyện tập
                <ArrowRight className="w-6 h-6 group-hover:translate-x-2 transition-transform" />
              </span>
            </button>
            
            <button className="group bg-white text-indigo-600 px-10 py-5 rounded-2xl font-bold text-lg shadow-xl hover:shadow-2xl transition-all duration-300 hover:scale-105 cursor-pointer border-2 border-indigo-600 hover:bg-indigo-50">
              <span className="flex items-center gap-3 justify-center">
                Thử ngay - Không cần đăng ký
                <Zap className="w-6 h-6 text-green-500 group-hover:rotate-12 transition-transform" />
              </span>
            </button>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-3 gap-8 max-w-2xl mx-auto">
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border-3 border-primary/10">
              <div className="text-4xl font-bold text-primary mb-2">{stats.lessons}+</div>
              <div className="text-sm text-gray-700 font-bold">Bài học</div>
            </div>
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border-3 border-cta/10">
              <div className="text-4xl font-bold text-cta mb-2">{stats.sentences}+</div>
              <div className="text-sm text-gray-700 font-bold">Câu luyện tập</div>
            </div>
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border-3 border-secondary/10">
              <div className="text-4xl font-bold text-secondary mb-2">{stats.users}+</div>
              <div className="text-sm text-gray-700 font-bold">Học viên</div>
            </div>
          </div>
        </div>

        {/* Scroll Indicator */}
        <div className="absolute bottom-10 left-1/2 -translate-x-1/2 animate-bounce">
          <Mouse className="w-8 h-8 text-gray-600" strokeWidth={2} />
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 px-4 bg-white/40 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-20">
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
              Tính năng <span className="text-primary">nổi bật</span>
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Công nghệ hiện đại kết hợp phương pháp học hiệu quả
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {/* Feature 1 */}
            <div className="group bg-gradient-to-br from-white to-indigo-50/50 rounded-3xl p-8 shadow-xl hover:shadow-2xl transition-all duration-300 hover:-translate-y-2 cursor-pointer border-3 border-primary/10">
              <div className="w-16 h-16 bg-gradient-to-br from-indigo-600 to-indigo-500 rounded-2xl flex items-center justify-center mb-6 group-hover:rotate-12 transition-transform duration-300">
                <Users className="w-8 h-8 text-white" strokeWidth={2.5} />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">Hybrid Mode</h3>
              <p className="text-gray-600 leading-relaxed">
                Luyện tập tự do không cần tài khoản, hoặc đăng ký để theo dõi tiến độ chi tiết
              </p>
            </div>

            {/* Feature 2 */}
            <div className="group bg-gradient-to-br from-white to-green-50/50 rounded-3xl p-8 shadow-xl hover:shadow-2xl transition-all duration-300 hover:-translate-y-2 cursor-pointer border-3 border-cta/10">
              <div className="w-16 h-16 bg-gradient-to-br from-green-600 to-green-500 rounded-2xl flex items-center justify-center mb-6 group-hover:rotate-12 transition-transform duration-300">
                <Brain className="w-8 h-8 text-white" strokeWidth={2.5} />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">Smart Algorithm</h3>
              <p className="text-gray-600 leading-relaxed">
                Thuật toán thông minh ưu tiên câu chưa thuộc, giúp bạn tiến bộ nhanh hơn
              </p>
            </div>

            {/* Feature 3 */}
            <div className="group bg-gradient-to-br from-white to-indigo-50/50 rounded-3xl p-8 shadow-xl hover:shadow-2xl transition-all duration-300 hover:-translate-y-2 cursor-pointer border-3 border-secondary/10">
              <div className="w-16 h-16 bg-gradient-to-br from-indigo-500 to-indigo-400 rounded-2xl flex items-center justify-center mb-6 group-hover:rotate-12 transition-transform duration-300">
                <Volume2 className="w-8 h-8 text-white" strokeWidth={2.5} />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">Audio TTS</h3>
              <p className="text-gray-600 leading-relaxed">
                Nghe phát âm chuẩn với công nghệ Text-to-Speech, luyện cả nghe lẫn nói
              </p>
            </div>

            {/* Feature 4 */}
            <div className="group bg-gradient-to-br from-white to-amber-50/50 rounded-3xl p-8 shadow-xl hover:shadow-2xl transition-all duration-300 hover:-translate-y-2 cursor-pointer border-3 border-amber-200/50">
              <div className="w-16 h-16 bg-gradient-to-br from-amber-600 to-amber-500 rounded-2xl flex items-center justify-center mb-6 group-hover:rotate-12 transition-transform duration-300">
                <BarChart3 className="w-8 h-8 text-white" strokeWidth={2.5} />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">Progress Tracking</h3>
              <p className="text-gray-600 leading-relaxed">
                Theo dõi tiến độ qua biểu đồ, xem số câu đã thuộc và tỷ lệ thành công
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-24 px-4 bg-gradient-to-br from-primary/5 to-secondary/5">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-20">
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
              Cách thức <span className="text-primary">hoạt động</span>
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Chỉ 3 bước đơn giản để bắt đầu hành trình chinh phục tiếng Anh
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-12 relative">
            {/* Connection Line */}
            <div className="hidden md:block absolute top-24 left-1/4 right-1/4 h-1 bg-gradient-to-r from-primary via-secondary to-cta opacity-20"></div>

            {/* Step 1 */}
            <div className="relative text-center">
              <div className="relative inline-block mb-8">
                <div className="w-32 h-32 bg-gradient-to-br from-indigo-600 to-indigo-500 rounded-full flex items-center justify-center shadow-2xl relative z-0">
                  <BookOpen className="w-16 h-16 text-white" strokeWidth={2.5} />
                </div>
                <div className="absolute -top-4 -right-4 w-16 h-16 bg-white rounded-full flex items-center justify-center text-3xl font-bold text-indigo-600 shadow-lg border-3 border-indigo-200 z-10">
                  1
                </div>
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">Chọn bài học</h3>
              <p className="text-gray-600 leading-relaxed">
                Duyệt qua 100+ bài học được phân loại theo chủ đề, từ cơ bản đến nâng cao
              </p>
            </div>

            {/* Step 2 */}
            <div className="relative text-center">
              <div className="relative inline-block mb-8">
                <div className="w-32 h-32 bg-gradient-to-br from-green-600 to-green-500 rounded-full flex items-center justify-center shadow-2xl relative z-0">
                  <Target className="w-16 h-16 text-white" strokeWidth={2.5} />
                </div>
                <div className="absolute -top-4 -right-4 w-16 h-16 bg-white rounded-full flex items-center justify-center text-3xl font-bold text-green-600 shadow-lg border-3 border-green-200 z-10">
                  2
                </div>
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">Luyện phản xạ</h3>
              <p className="text-gray-600 leading-relaxed">
                Đọc câu Việt, nghĩ câu Anh, lật thẻ kiểm tra và đánh giá độ chính xác
              </p>
            </div>

            {/* Step 3 */}
            <div className="relative text-center">
              <div className="relative inline-block mb-8">
                <div className="w-32 h-32 bg-gradient-to-br from-indigo-500 to-indigo-400 rounded-full flex items-center justify-center shadow-2xl relative z-0">
                  <TrendingUp className="w-16 h-16 text-white" strokeWidth={2.5} />
                </div>
                <div className="absolute -top-4 -right-4 w-16 h-16 bg-white rounded-full flex items-center justify-center text-3xl font-bold text-indigo-500 shadow-lg border-3 border-indigo-200 z-10">
                  3
                </div>
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">Theo dõi tiến độ</h3>
              <p className="text-gray-600 leading-relaxed">
                Xem biểu đồ tiến độ, số câu đã thuộc và thống kê chi tiết để cải thiện
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Social Proof Section */}
      <section className="py-24 px-4 bg-white/60 backdrop-blur-sm">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
              Kết quả <span className="text-primary">thực tế</span>
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Hàng trăm học viên đã cải thiện phản xạ tiếng Anh của mình
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 mb-16">
            {/* Achievement 1 */}
            <div className="bg-gradient-to-br from-primary/10 to-secondary/10 rounded-3xl p-8 text-center border-3 border-primary/20">
              <Award className="w-16 h-16 text-primary mx-auto mb-4" />
              <div className="text-5xl font-bold text-primary mb-2">85%</div>
              <p className="text-gray-700">Học viên cải thiện tốc độ phản xạ sau 1 tuần</p>
            </div>

            {/* Achievement 2 */}
            <div className="bg-gradient-to-br from-cta/10 to-green-100 rounded-3xl p-8 text-center border-3 border-cta/20">
              <CheckCircle2 className="w-16 h-16 text-cta mx-auto mb-4" />
              <div className="text-5xl font-bold text-cta mb-2">1000+</div>
              <p className="text-gray-700">Câu được luyện tập mỗi ngày</p>
            </div>

            {/* Achievement 3 */}
            <div className="bg-gradient-to-br from-secondary/10 to-indigo-100 rounded-3xl p-8 text-center border-3 border-secondary/20">
              <TrendingUp className="w-16 h-16 text-secondary mx-auto mb-4" />
              <div className="text-5xl font-bold text-secondary mb-2">92%</div>
              <p className="text-gray-700">Tỷ lệ hoàn thành bài học</p>
            </div>
          </div>

          {/* Testimonials */}
          <div className="grid md:grid-cols-2 gap-8">
            <div className="bg-white rounded-3xl p-8 shadow-xl border-3 border-primary/10">
              <div className="flex items-start gap-4 mb-4">
                <img 
                  src="/donaldtrump.jpeg" 
                  alt="Donald Trump" 
                  className="w-16 h-16 rounded-full object-cover border-3 border-primary/20"
                />
                <div>
                  <h4 className="text-xl font-bold text-gray-900">Donald Trump</h4>
                  <p className="text-sm text-gray-500">Former President</p>
                </div>
              </div>
              <p className="text-gray-600 leading-relaxed italic">
                "Sau 2 tuần luyện tập, tôi có thể phản xạ nhanh hơn rất nhiều khi nói chuyện với khách hàng nước ngoài. Thuật toán smart của app giúp tôi tập trung vào những câu còn yếu!"
              </p>
            </div>

            <div className="bg-white rounded-3xl p-8 shadow-xl border-3 border-cta/10">
              <div className="flex items-start gap-4 mb-4">
                <img 
                  src="/kimjongun.jpg" 
                  alt="Kim Jong Un" 
                  className="w-16 h-16 rounded-full object-cover border-3 border-cta/20"
                />
                <div>
                  <h4 className="text-xl font-bold text-gray-900">Kim Jong Un</h4>
                  <p className="text-sm text-gray-500">Supreme Leader</p>
                </div>
              </div>
              <p className="text-gray-600 leading-relaxed italic">
                "Mình thích nhất là không cần đăng ký vẫn luyện được. Audio TTS phát âm rất chuẩn, giúp mình tự tin hơn khi nói tiếng Anh!"
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="py-24 px-4 bg-gradient-to-br from-primary via-secondary to-indigo-600 text-white relative overflow-hidden">
        {/* Decorative Elements */}
        <div className="absolute top-10 left-10 w-32 h-32 border-3 border-white/20 rounded-full"></div>
        <div className="absolute bottom-10 right-10 w-48 h-48 border-3 border-white/20 rounded-full"></div>
        <div className="absolute top-1/2 left-1/4 w-24 h-24 bg-white/10 rounded-2xl rotate-45"></div>

        <div className="relative z-10 max-w-4xl mx-auto text-center">
          <h2 className="text-4xl md:text-6xl font-bold mb-6">
            Sẵn sàng chinh phục tiếng Anh?
          </h2>
          <p className="text-xl md:text-2xl mb-12 text-white/90 leading-relaxed">
            Tham gia cùng hàng trăm học viên đang luyện phản xạ mỗi ngày
          </p>

          <div className="flex flex-col sm:flex-row gap-6 justify-center mb-8">
            <button className="group bg-white text-indigo-600 px-12 py-6 rounded-2xl font-bold text-xl shadow-2xl hover:shadow-white/30 transition-all duration-300 hover:scale-105 cursor-pointer border-2 border-white">
              <span className="flex items-center gap-3 justify-center">
                Đăng ký miễn phí
                <ArrowRight className="w-6 h-6 group-hover:translate-x-2 transition-transform" />
              </span>
            </button>
            
            <button className="group bg-white/20 backdrop-blur-sm border-2 border-white text-white px-12 py-6 rounded-2xl font-bold text-xl hover:bg-white hover:text-indigo-600 transition-all duration-300 hover:scale-105 cursor-pointer shadow-xl">
              <span className="flex items-center gap-3 justify-center">
                Thử ngay
                <Zap className="w-6 h-6 group-hover:rotate-12 transition-transform" />
              </span>
            </button>
          </div>

          <p className="text-white/80 text-sm">
            ✨ Không cần thẻ tín dụng • Luyện tập ngay lập tức • Miễn phí mãi mãi
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <h3 className="text-2xl font-bold mb-4">Vi-En Trainer</h3>
              <p className="text-gray-300 text-sm leading-relaxed">
                Nền tảng luyện phản xạ tiếng Anh hiệu quả với công nghệ hiện đại
              </p>
            </div>

            <div>
              <h4 className="text-lg font-bold mb-4">Sản phẩm</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="/lessons" className="text-gray-300 hover:text-white transition-colors cursor-pointer">Bài học</a></li>
                <li><a href="/practice" className="text-gray-300 hover:text-white transition-colors cursor-pointer">Luyện tập</a></li>
                <li><a href="/stats" className="text-gray-300 hover:text-white transition-colors cursor-pointer">Thống kê</a></li>
              </ul>
            </div>

            <div>
              <h4 className="text-lg font-bold mb-4">Tài khoản</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="/login" className="text-gray-300 hover:text-white transition-colors cursor-pointer">Đăng nhập</a></li>
                <li><a href="/register" className="text-gray-300 hover:text-white transition-colors cursor-pointer">Đăng ký</a></li>
                <li><a href="/guest" className="text-gray-300 hover:text-white transition-colors cursor-pointer">Chế độ khách</a></li>
              </ul>
            </div>

            <div>
              <h4 className="text-lg font-bold mb-4">Hỗ trợ</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="/help" className="text-gray-300 hover:text-white transition-colors cursor-pointer">Trợ giúp</a></li>
                <li><a href="/about" className="text-gray-300 hover:text-white transition-colors cursor-pointer">Về chúng tôi</a></li>
                <li><a href="/contact" className="text-gray-300 hover:text-white transition-colors cursor-pointer">Liên hệ</a></li>
              </ul>
            </div>
          </div>

          <div className="border-t border-gray-700 pt-8 text-center">
            <p className="text-gray-400 text-sm">
              © 2026 Vi-En Reflex Trainer. Made with ❤️ for language learners.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
