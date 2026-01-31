import { useState } from 'react';
import { API_BASE_URL } from '../config';
import { Link } from 'react-router-dom';
import { Mail, ArrowRight, ArrowLeft, CheckCircle2, Sparkles } from 'lucide-react';

export default function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  const validateEmail = (email: string): string | undefined => {
    if (!email) return 'Email là bắt buộc';
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) return 'Email không hợp lệ';
    return undefined;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const emailError = validateEmail(email);
    if (emailError) {
      setError(emailError);
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/forgot-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Có lỗi xảy ra');
      }

      setIsSuccess(true);
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Không thể gửi email. Vui lòng thử lại sau.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 flex items-center justify-center p-4 py-8">
      {/* Background Pattern */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-1/2 -left-1/2 w-full h-full bg-gradient-to-br from-indigo-100/20 to-transparent rounded-full blur-3xl" />
        <div className="absolute -bottom-1/2 -right-1/2 w-full h-full bg-gradient-to-tl from-green-100/20 to-transparent rounded-full blur-3xl" />
      </div>

      {/* Card */}
      <div className="relative w-full max-w-md my-8">
        {/* Floating decoration */}
        <div className="absolute -top-4 -right-4 w-20 h-20 bg-gradient-to-br from-indigo-400 to-indigo-600 rounded-2xl rotate-12 opacity-20 blur-xl" />
        <div className="absolute -bottom-4 -left-4 w-24 h-24 bg-gradient-to-br from-green-400 to-green-600 rounded-2xl -rotate-12 opacity-20 blur-xl" />

        <div className="relative bg-white/80 backdrop-blur-sm rounded-3xl shadow-2xl border-2 border-white/50 overflow-hidden">
          {!isSuccess ? (
            <>
              {/* Header */}
              <div className="bg-gradient-to-r from-indigo-600 to-indigo-500 p-6 text-center">
                <div className="inline-flex items-center justify-center w-14 h-14 bg-white/20 rounded-2xl mb-3 backdrop-blur-sm">
                  <Sparkles className="w-7 h-7 text-white" strokeWidth={2.5} />
                </div>
                <h1 className="text-2xl font-bold text-white mb-1" style={{ fontFamily: "'Baloo 2', cursive" }}>
                  Quên mật khẩu?
                </h1>
                <p className="text-indigo-100 text-sm" style={{ fontFamily: "'Comic Neue', cursive" }}>
                  Nhập email để nhận link đặt lại mật khẩu
                </p>
              </div>

              {/* Form */}
              <form onSubmit={handleSubmit} className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1.5" style={{ fontFamily: "'Baloo 2', cursive" }}>
                    Email
                  </label>
                  <div className="relative">
                    <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
                      <Mail className="w-5 h-5" strokeWidth={2.5} />
                    </div>
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => {
                        setEmail(e.target.value);
                        setError('');
                      }}
                      className={`w-full pl-11 pr-4 py-2.5 rounded-xl border-2 transition-all duration-200 ${
                        error
                          ? 'border-red-300 focus:border-red-500 focus:ring-2 focus:ring-red-200'
                          : 'border-gray-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200'
                      }`}
                      placeholder="email@example.com"
                      style={{ fontFamily: "'Comic Neue', cursive" }}
                    />
                  </div>
                  {error && (
                    <p className="text-red-500 text-sm mt-1" style={{ fontFamily: "'Comic Neue', cursive" }}>
                      {error}
                    </p>
                  )}
                </div>

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full bg-gradient-to-r from-indigo-600 to-indigo-500 text-white py-2.5 rounded-xl font-bold text-base shadow-lg hover:shadow-xl hover:from-indigo-700 hover:to-indigo-600 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  style={{ fontFamily: "'Baloo 2', cursive" }}
                >
                  {isLoading ? (
                    <span>Đang gửi...</span>
                  ) : (
                    <>
                      Gửi link đặt lại mật khẩu
                      <ArrowRight className="w-5 h-5" strokeWidth={2.5} />
                    </>
                  )}
                </button>

                {/* Back to Login */}
                <Link
                  to="/auth"
                  className="w-full bg-white border-2 border-gray-300 text-gray-700 py-2.5 rounded-xl font-bold text-base hover:bg-gray-50 transition-all duration-200 flex items-center justify-center gap-2"
                  style={{ fontFamily: "'Baloo 2', cursive" }}
                >
                  <ArrowLeft className="w-5 h-5" strokeWidth={2.5} />
                  Quay lại đăng nhập
                </Link>
              </form>
            </>
          ) : (
            <>
              {/* Success State */}
              <div className="p-8 text-center">
                <div className="inline-flex items-center justify-center w-20 h-20 bg-green-100 rounded-full mb-6">
                  <CheckCircle2 className="w-12 h-12 text-green-600" strokeWidth={2.5} />
                </div>
                
                <h2 className="text-2xl font-bold text-gray-900 mb-3" style={{ fontFamily: "'Baloo 2', cursive" }}>
                  Email đã được gửi!
                </h2>
                
                <p className="text-gray-600 mb-6" style={{ fontFamily: "'Comic Neue', cursive" }}>
                  Chúng tôi đã gửi link đặt lại mật khẩu đến email <strong>{email}</strong>. 
                  Vui lòng kiểm tra hộp thư của bạn.
                </p>

                <div className="space-y-3">
                  <p className="text-sm text-gray-500" style={{ fontFamily: "'Comic Neue', cursive" }}>
                    Không nhận được email?
                  </p>
                  
                  <button
                    onClick={() => {
                      setIsSuccess(false);
                      setEmail('');
                    }}
                    className="text-indigo-600 hover:text-indigo-700 font-semibold text-sm transition-colors duration-200"
                    style={{ fontFamily: "'Comic Neue', cursive" }}
                  >
                    Thử lại với email khác
                  </button>

                  <div className="pt-4">
                    <Link
                      to="/auth"
                      className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 font-semibold transition-colors duration-200"
                      style={{ fontFamily: "'Comic Neue', cursive" }}
                    >
                      <ArrowLeft className="w-4 h-4" strokeWidth={2.5} />
                      Quay lại đăng nhập
                    </Link>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
