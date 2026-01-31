import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Eye, EyeOff, Mail, User, Lock, ArrowRight, Sparkles } from 'lucide-react';
import toast, { Toaster } from 'react-hot-toast';

type AuthMode = 'login' | 'register';

interface FormData {
  email: string;
  username: string;
  password: string;
  confirmPassword: string;
}

interface FormErrors {
  email?: string;
  username?: string;
  password?: string;
  confirmPassword?: string;
}

export default function Auth() {
  const [mode, setMode] = useState<AuthMode>('login');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState<FormData>({
    email: '',
    username: '',
    password: '',
    confirmPassword: '',
  });
  const [errors, setErrors] = useState<FormErrors>({});

  // Validation functions
  const validateEmail = (email: string): string | undefined => {
    if (!email) return 'Email là bắt buộc';
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) return 'Email không hợp lệ';
    if (email.length > 100) return 'Email không được vượt quá 100 ký tự';
    return undefined;
  };

  const validateUsername = (username: string): string | undefined => {
    if (!username) return 'Tên đăng nhập là bắt buộc';
    if (username.length < 3) return 'Tên đăng nhập phải có ít nhất 3 ký tự';
    if (username.length > 50) return 'Tên đăng nhập không được vượt quá 50 ký tự';
    const usernameRegex = /^[a-zA-Z0-9_]+$/;
    if (!usernameRegex.test(username)) return 'Chỉ được dùng chữ cái, số và gạch dưới';
    return undefined;
  };

  const validatePassword = (password: string): string | undefined => {
    if (!password) return 'Mật khẩu là bắt buộc';
    if (password.length < 5) return 'Mật khẩu phải có ít nhất 5 ký tự';
    return undefined;
  };

  const getPasswordStrength = (password: string): { label: string; color: string; width: string } => {
    if (password.length === 0) return { label: '', color: '', width: '0%' };
    if (password.length < 6) return { label: 'Yếu', color: 'bg-red-500', width: '33%' };
    if (password.length < 10) return { label: 'Trung bình', color: 'bg-yellow-500', width: '66%' };
    return { label: 'Mạnh', color: 'bg-green-600', width: '100%' };
  };

  const handleInputChange = (field: keyof FormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error for this field
    setErrors(prev => ({ ...prev, [field]: undefined }));
  };

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    if (mode === 'register') {
      newErrors.email = validateEmail(formData.email);
      newErrors.username = validateUsername(formData.username);
    } else {
      // For login, identifier can be email or username
      if (!formData.email && !formData.username) {
        newErrors.email = 'Email hoặc tên đăng nhập là bắt buộc';
      }
    }

    newErrors.password = validatePassword(formData.password);

    if (mode === 'register') {
      if (formData.password !== formData.confirmPassword) {
        newErrors.confirmPassword = 'Mật khẩu không khớp';
      }
    }

    // Filter out undefined values
    const filteredErrors = Object.fromEntries(
      Object.entries(newErrors).filter(([_, v]) => v !== undefined)
    ) as FormErrors;

    setErrors(filteredErrors);
    
    const hasErrors = Object.keys(filteredErrors).length > 0;
    console.log('Validation errors:', filteredErrors);
    console.log('Has errors:', hasErrors);
    
    return !hasErrors;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    console.log('Form submitted. Mode:', mode);
    console.log('Form data:', formData);
    
    if (!validateForm()) {
      console.log('Validation failed. Errors:', errors);
      return;
    }

    console.log('Validation passed. Proceeding with API call...');
    setIsLoading(true);

    try {
      if (mode === 'register') {
        // Register API call
        const response = await fetch('http://localhost:8000/api/v1/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: formData.email,
            username: formData.username,
            password: formData.password,
          }),
        });

        if (!response.ok) {
          const data = await response.json();
          throw new Error(data.detail || 'Đăng ký thất bại');
        }

        // Auto-switch to login after registration
        toast.success('Đăng ký thành công! Vui lòng đăng nhập.', {
          duration: 3000,
          position: 'top-center',
        });
        setMode('login');
      } else {
        // Login API call
        const response = await fetch('http://localhost:8000/api/v1/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: formData.email || formData.username,
            password: formData.password,
          }),
        });

        if (!response.ok) {
          const data = await response.json();
          throw new Error(data.detail || 'Đăng nhập thất bại');
        }

        const data = await response.json();
        
        // Store tokens
        localStorage.setItem('vi_en_token', data.access_token);
        localStorage.setItem('vi_en_refresh', data.refresh_token);
        
        // Fetch user info to check if admin
        const userResponse = await fetch('http://localhost:8000/api/v1/auth/me', {
          headers: {
            'Authorization': `Bearer ${data.access_token}`,
          },
        });

        if (userResponse.ok) {
          const userData = await userResponse.json();
          // Store user data
          localStorage.setItem('vi_en_user', JSON.stringify(userData));
          
          // Redirect based on user role
          if (userData.is_admin) {
            window.location.href = '/admin';
          } else {
            window.location.href = '/lessons';
          }
        } else {
          // Fallback to lessons if we can't fetch user info
          window.location.href = '/lessons';
        }
      }
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Có lỗi xảy ra', {
        duration: 4000,
        position: 'top-center',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleGuestMode = () => {
    window.location.href = '/lessons';
  };

  const switchMode = () => {
    setMode(mode === 'login' ? 'register' : 'login');
    setErrors({});
    setFormData({ email: '', username: '', password: '', confirmPassword: '' });
  };

  const passwordStrength = getPasswordStrength(formData.password);

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 flex items-center justify-center p-4 py-8 overflow-y-auto">
      <Toaster />
      {/* Background Pattern */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-1/2 -left-1/2 w-full h-full bg-gradient-to-br from-indigo-100/20 to-transparent rounded-full blur-3xl" />
        <div className="absolute -bottom-1/2 -right-1/2 w-full h-full bg-gradient-to-tl from-green-100/20 to-transparent rounded-full blur-3xl" />
      </div>

      {/* Auth Card */}
      <div className="relative w-full max-w-md my-8">
        {/* Floating decoration */}
        <div className="absolute -top-4 -right-4 w-20 h-20 bg-gradient-to-br from-indigo-400 to-indigo-600 rounded-2xl rotate-12 opacity-20 blur-xl" />
        <div className="absolute -bottom-4 -left-4 w-24 h-24 bg-gradient-to-br from-green-400 to-green-600 rounded-2xl -rotate-12 opacity-20 blur-xl" />

        <div className="relative bg-white/80 backdrop-blur-sm rounded-3xl shadow-2xl border-2 border-white/50 overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-indigo-600 to-indigo-500 p-6 text-center">
            <div className="inline-flex items-center justify-center w-14 h-14 bg-white/20 rounded-2xl mb-3 backdrop-blur-sm">
              <Sparkles className="w-7 h-7 text-white" strokeWidth={2.5} />
            </div>
            <h1 className="text-2xl font-bold text-white mb-1" style={{ fontFamily: "'Baloo 2', cursive" }}>
              Vi-En Reflex Trainer
            </h1>
            <p className="text-indigo-100 text-sm" style={{ fontFamily: "'Comic Neue', cursive" }}>
              Rèn luyện phản xạ ngôn ngữ
            </p>
          </div>

          {/* Tab Switch */}
          <div className="flex gap-2 p-4 pb-0">
            <button
              onClick={() => mode === 'register' && switchMode()}
              className={`flex-1 py-2.5 rounded-xl font-semibold transition-all duration-200 ${
                mode === 'login'
                  ? 'bg-indigo-600 text-white shadow-lg'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
              style={{ fontFamily: "'Baloo 2', cursive" }}
            >
              Đăng nhập
            </button>
            <button
              onClick={() => mode === 'login' && switchMode()}
              className={`flex-1 py-2.5 rounded-xl font-semibold transition-all duration-200 ${
                mode === 'register'
                  ? 'bg-indigo-600 text-white shadow-lg'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
              style={{ fontFamily: "'Baloo 2', cursive" }}
            >
              Đăng ký
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="p-4 space-y-3">
            {/* Email/Username for Login */}
            {mode === 'login' && (
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1.5" style={{ fontFamily: "'Baloo 2', cursive" }}>
                  Email hoặc Tên đăng nhập
                </label>
                <div className="relative">
                  <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
                    <Mail className="w-5 h-5" strokeWidth={2.5} />
                  </div>
                  <input
                    type="text"
                    value={formData.email || formData.username}
                    onChange={(e) => handleInputChange('email', e.target.value)}
                    className={`w-full pl-11 pr-4 py-2.5 rounded-xl border-2 transition-all duration-200 ${
                      errors.email
                        ? 'border-red-300 focus:border-red-500 focus:ring-2 focus:ring-red-200'
                        : 'border-gray-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200'
                    }`}
                    placeholder="email@example.com hoặc username"
                    style={{ fontFamily: "'Comic Neue', cursive" }}
                  />
                </div>
                {errors.email && (
                  <p className="text-red-500 text-sm mt-1" style={{ fontFamily: "'Comic Neue', cursive" }}>
                    {errors.email}
                  </p>
                )}
              </div>
            )}

            {/* Email for Register */}
            {mode === 'register' && (
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
                    value={formData.email}
                    onChange={(e) => handleInputChange('email', e.target.value)}
                    className={`w-full pl-11 pr-4 py-2.5 rounded-xl border-2 transition-all duration-200 ${
                      errors.email
                        ? 'border-red-300 focus:border-red-500 focus:ring-2 focus:ring-red-200'
                        : 'border-gray-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200'
                    }`}
                    placeholder="email@example.com"
                    style={{ fontFamily: "'Comic Neue', cursive" }}
                  />
                </div>
                {errors.email && (
                  <p className="text-red-500 text-sm mt-1" style={{ fontFamily: "'Comic Neue', cursive" }}>
                    {errors.email}
                  </p>
                )}
              </div>
            )}

            {/* Username for Register */}
            {mode === 'register' && (
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1.5" style={{ fontFamily: "'Baloo 2', cursive" }}>
                  Tên đăng nhập
                </label>
                <div className="relative">
                  <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
                    <User className="w-5 h-5" strokeWidth={2.5} />
                  </div>
                  <input
                    type="text"
                    value={formData.username}
                    onChange={(e) => handleInputChange('username', e.target.value)}
                    className={`w-full pl-11 pr-4 py-2.5 rounded-xl border-2 transition-all duration-200 ${
                      errors.username
                        ? 'border-red-300 focus:border-red-500 focus:ring-2 focus:ring-red-200'
                        : 'border-gray-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200'
                    }`}
                    placeholder="johndoe"
                    style={{ fontFamily: "'Comic Neue', cursive" }}
                  />
                </div>
                {errors.username && (
                  <p className="text-red-500 text-sm mt-1" style={{ fontFamily: "'Comic Neue', cursive" }}>
                    {errors.username}
                  </p>
                )}
              </div>
            )}

            {/* Password */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1.5" style={{ fontFamily: "'Baloo 2', cursive" }}>
                Mật khẩu
              </label>
              <div className="relative">
                <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
                  <Lock className="w-5 h-5" strokeWidth={2.5} />
                </div>
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={formData.password}
                  onChange={(e) => handleInputChange('password', e.target.value)}
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
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors duration-200"
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
              
              {/* Password Strength Meter for Register */}
              {mode === 'register' && formData.password && (
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

            {/* Confirm Password for Register */}
            {mode === 'register' && (
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1.5" style={{ fontFamily: "'Baloo 2', cursive" }}>
                  Xác nhận mật khẩu
                </label>
                <div className="relative">
                  <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
                    <Lock className="w-5 h-5" strokeWidth={2.5} />
                  </div>
                  <input
                    type={showConfirmPassword ? 'text' : 'password'}
                    value={formData.confirmPassword}
                    onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
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
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors duration-200"
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
            )}

            {/* Remember Me & Forgot Password */}
            {mode === 'login' && (
              <div className="flex items-center justify-between">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    className="w-4 h-4 rounded border-2 border-gray-300 text-indigo-600 focus:ring-2 focus:ring-indigo-200"
                  />
                  <span className="text-sm text-gray-700" style={{ fontFamily: "'Comic Neue', cursive" }}>
                    Ghi nhớ đăng nhập
                  </span>
                </label>
                <Link
                  to="/forgot-password"
                  className="text-sm text-indigo-600 hover:text-indigo-700 font-semibold transition-colors duration-200"
                  style={{ fontFamily: "'Comic Neue', cursive" }}
                >
                  Quên mật khẩu?
                </Link>
              </div>
            )}

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
                  {mode === 'login' ? 'Đăng nhập' : 'Đăng ký'}
                  <ArrowRight className="w-5 h-5" strokeWidth={2.5} />
                </>
              )}
            </button>

            {/* Guest Mode Button */}
            <button
              type="button"
              onClick={handleGuestMode}
              className="w-full bg-white border-2 border-green-600 text-green-600 py-2.5 rounded-xl font-bold text-base hover:bg-green-50 transition-all duration-200 flex items-center justify-center gap-2"
              style={{ fontFamily: "'Baloo 2', cursive" }}
            >
              Tiếp tục không đăng ký
              <ArrowRight className="w-5 h-5" strokeWidth={2.5} />
            </button>
          </form>

          {/* Social Login Placeholder */}
          <div className="px-4 pb-4">
            <div className="relative my-4">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t-2 border-gray-200" />
              </div>
              <div className="relative flex justify-center">
                <span className="px-4 bg-white text-sm text-gray-500" style={{ fontFamily: "'Comic Neue', cursive" }}>
                  Hoặc tiếp tục với
                </span>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-3">
              <button
                type="button"
                className="py-3 px-4 bg-gray-50 hover:bg-gray-100 border-2 border-gray-200 rounded-xl transition-all duration-200 flex items-center justify-center"
              >
                <svg className="w-5 h-5" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
              </button>
              <button
                type="button"
                className="py-3 px-4 bg-gray-50 hover:bg-gray-100 border-2 border-gray-200 rounded-xl transition-all duration-200 flex items-center justify-center"
              >
                <svg className="w-5 h-5" fill="#1877F2" viewBox="0 0 24 24">
                  <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                </svg>
              </button>
              <button
                type="button"
                className="py-3 px-4 bg-gray-50 hover:bg-gray-100 border-2 border-gray-200 rounded-xl transition-all duration-200 flex items-center justify-center"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
