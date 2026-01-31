import { useState, useEffect } from 'react';
import { API_BASE_URL } from '../config';
import { Link, useSearchParams, useNavigate } from 'react-router-dom';
import { Lock, Eye, EyeOff, ArrowRight, CheckCircle2, XCircle, Sparkles } from 'lucide-react';

export default function ResetPassword() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get('token');

  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [errors, setErrors] = useState<{ password?: string; confirmPassword?: string }>({});
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [tokenError, setTokenError] = useState(false);

  useEffect(() => {
    if (!token) {
      setTokenError(true);
    }
  }, [token]);

  const getPasswordStrength = (password: string): { label: string; color: string; width: string } => {
    if (password.length === 0) return { label: '', color: '', width: '0%' };
    if (password.length < 6) return { label: 'Yếu', color: 'bg-red-500', width: '33%' };
    if (password.length < 10) return { label: 'Trung bình', color: 'bg-yellow-500', width: '66%' };
    return { label: 'Mạnh', color: 'bg-green-600', width: '100%' };
  };

  const validatePassword = (password: string): string | undefined => {
    if (!password) return 'Mật khẩu là bắt buộc';
    if (password.length < 6) return 'Mật khẩu phải có ít nhất 6 ký tự';
    return undefined;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const newErrors: { password?: string; confirmPassword?: string } = {};
    
    newErrors.password = validatePassword(password);
    if (password !== confirmPassword) {
      newErrors.confirmPassword = 'Mật khẩu không khớp';
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/reset-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          token,
          new_password: password,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Không thể đặt lại mật khẩu');
      }

      setIsSuccess(true);
      // Redirect to login after 3 seconds
      setTimeout(() => {
        navigate('/auth');
      }, 3000);
    } catch (error) {
      setErrors({ 
        password: error instanceof Error ? error.message : 'Có lỗi xảy ra. Vui lòng thử lại.' 
      });
    } finally {
      setIsLoading(false);
    }
  };

  const passwordStrength = getPasswordStrength(password);

  if (tokenError) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 flex items-center justify-center p-4">
        <div className="relative w-full max-w-md">
          <div className="relative bg-white/80 backdrop-blur-sm rounded-3xl shadow-2xl border-2 border-white/50 overflow-hidden p-8 text-center">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-red-100 rounded-full mb-6">
              <XCircle className="w-12 h-12 text-red-600" strokeWidth={2.5} />
            </div>
            
            <h2 className="text-2xl font-bold text-gray-900 mb-3" style={{ fontFamily: "'Baloo 2', cursive" }}>
              Link không hợp lệ
            </h2>
            
            <p className="text-gray-600 mb-6" style={{ fontFamily: "'Comic Neue', cursive" }}>
              Link đặt lại mật khẩu không hợp lệ hoặc đã hết hạn. Vui lòng yêu cầu link mới.
            </p>

            <div className="space-y-3">
              <Link
                to="/forgot-password"
                className="w-full inline-block bg-gradient-to-r from-indigo-600 to-indigo-500 text-white py-2.5 rounded-xl font-bold text-base shadow-lg hover:shadow-xl transition-all duration-200"
                style={{ fontFamily: "'Baloo 2', cursive" }}
              >
                Yêu cầu link mới
              </Link>

              <Link
                to="/auth"
                className="w-full inline-block bg-white border-2 border-gray-300 text-gray-700 py-2.5 rounded-xl font-bold text-base hover:bg-gray-50 transition-all duration-200"
                style={{ fontFamily: "'Baloo 2', cursive" }}
              >
                Quay lại đăng nhập
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

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
                  Đặt lại mật khẩu
                </h1>
                <p className="text-indigo-100 text-sm" style={{ fontFamily: "'Comic Neue', cursive" }}>
                  Nhập mật khẩu mới của bạn
                </p>
              </div>

              {/* Form */}
              <form onSubmit={handleSubmit} className="p-6 space-y-4">
                {/* New Password */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1.5" style={{ fontFamily: "'Baloo 2', cursive" }}>
                    Mật khẩu mới
                  </label>
                  <div className="relative">
                    <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
                      <Lock className="w-5 h-5" strokeWidth={2.5} />
                    </div>
                    <input
                      type={showPassword ? 'text' : 'password'}
                      value={password}
                      onChange={(e) => {
                        setPassword(e.target.value);
                        setErrors({});
                      }}
                      className={`w-full pl-11 pr-12 py-2.5 rounded-xl border-2 transition-all duration-200 ${
                        errors.password
                          ? 'border-red-300 focus:border-red-500 focus:ring-2 focus:ring-red-200'
                          : 'border-gray-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200'
                      }`}
                      placeholder="••••••••"
                      style={{ fontFamily: "'Comic Neue', cursive" }}
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors duration-200"
                    >
                      {showPassword ? (
                        <EyeOff className="w-5 h-5" strokeWidth={2.5} />
                      ) : (
                        <Eye className="w-5 h-5" strokeWidth={2.5} />
                      )}
                    </button>
                  </div>
                  {errors.password && (
                    <p className="text-red-500 text-sm mt-1" style={{ fontFamily: "'Comic Neue', cursive" }}>
                      {errors.password}
                    </p>
                  )}
                  
                  {/* Password Strength Meter */}
                  {password && (
                    <div className="mt-2">
                      <div className="flex gap-1 h-1 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className={`transition-all duration-300 ${passwordStrength.color}`}
                          style={{ width: passwordStrength.width }}
                        />
                      </div>
                      <p className="text-xs mt-1 text-gray-600" style={{ fontFamily: "'Comic Neue', cursive" }}>
                        Độ mạnh: <span className="font-semibold">{passwordStrength.label}</span>
                      </p>
                    </div>
                  )}
                </div>

                {/* Confirm Password */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1.5" style={{ fontFamily: "'Baloo 2', cursive" }}>
                    Xác nhận mật khẩu mới
                  </label>
                  <div className="relative">
                    <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
                      <Lock className="w-5 h-5" strokeWidth={2.5} />
                    </div>
                    <input
                      type={showConfirmPassword ? 'text' : 'password'}
                      value={confirmPassword}
                      onChange={(e) => {
                        setConfirmPassword(e.target.value);
                        setErrors({ ...errors, confirmPassword: undefined });
                      }}
                      className={`w-full pl-11 pr-12 py-2.5 rounded-xl border-2 transition-all duration-200 ${
                        errors.confirmPassword
                          ? 'border-red-300 focus:border-red-500 focus:ring-2 focus:ring-red-200'
                          : 'border-gray-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200'
                      }`}
                      placeholder="••••••••"
                      style={{ fontFamily: "'Comic Neue', cursive" }}
                    />
                    <button
                      type="button"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors duration-200"
                    >
                      {showConfirmPassword ? (
                        <EyeOff className="w-5 h-5" strokeWidth={2.5} />
                      ) : (
                        <Eye className="w-5 h-5" strokeWidth={2.5} />
                      )}
                    </button>
                  </div>
                  {errors.confirmPassword && (
                    <p className="text-red-500 text-sm mt-1" style={{ fontFamily: "'Comic Neue', cursive" }}>
                      {errors.confirmPassword}
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
                    <span>Đang xử lý...</span>
                  ) : (
                    <>
                      Đặt lại mật khẩu
                      <ArrowRight className="w-5 h-5" strokeWidth={2.5} />
                    </>
                  )}
                </button>

                {/* Back to Login */}
                <Link
                  to="/auth"
                  className="block text-center text-gray-600 hover:text-gray-900 font-semibold transition-colors duration-200 text-sm"
                  style={{ fontFamily: "'Comic Neue', cursive" }}
                >
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
                  Đặt lại mật khẩu thành công!
                </h2>
                
                <p className="text-gray-600 mb-6" style={{ fontFamily: "'Comic Neue', cursive" }}>
                  Mật khẩu của bạn đã được đặt lại thành công. Bạn có thể đăng nhập với mật khẩu mới.
                </p>

                <p className="text-sm text-gray-500 mb-4" style={{ fontFamily: "'Comic Neue', cursive" }}>
                  Đang chuyển đến trang đăng nhập...
                </p>

                <Link
                  to="/auth"
                  className="inline-flex items-center gap-2 text-indigo-600 hover:text-indigo-700 font-semibold transition-colors duration-200"
                  style={{ fontFamily: "'Comic Neue', cursive" }}
                >
                  Đăng nhập ngay
                  <ArrowRight className="w-4 h-4" strokeWidth={2.5} />
                </Link>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
