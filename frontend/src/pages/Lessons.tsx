import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Search, 
  BookOpen, 
  ArrowRight, 
  ChevronLeft, 
  ChevronRight,
  FileText,
  TrendingUp,
  Sparkles
} from 'lucide-react';
import { getAccessToken } from '../utils/auth';

interface Lesson {
  id: number;
  title: string;
  description: string;
  order_index: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface PaginationInfo {
  page: number;
  limit: number;
  total_items: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

interface LessonStats {
  lesson_id: number;
  sentence_count: number;
  progress?: {
    total_practiced: number;
    progress_percentage: number;
  };
}

export default function Lessons() {
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [lessonsStats, setLessonsStats] = useState<Map<number, LessonStats>>(new Map());
  const [pagination, setPagination] = useState<PaginationInfo | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [filterActive, setFilterActive] = useState<boolean | null>(null);
  const [sortBy, setSortBy] = useState<'created_at' | 'order_index'>('order_index');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  
  const isAuthenticated = !!getAccessToken();

  useEffect(() => {
    fetchLessons();
  }, [currentPage, searchQuery, filterActive, sortBy, sortOrder]);

  const fetchLessons = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({
        page: currentPage.toString(),
        limit: '12',
        sort_by: sortBy,
        order: sortOrder,
      });

      if (searchQuery) params.append('search', searchQuery);
      if (filterActive !== null) params.append('is_active', filterActive.toString());

      const response = await fetch(`http://localhost:8000/api/v1/lessons?${params}`);
      
      if (!response.ok) {
        throw new Error('Không thể tải danh sách bài học');
      }

      const data = await response.json();
      setLessons(data.items);
      setPagination(data.pagination);

      // Fetch sentence counts and progress for each lesson
      await fetchLessonsStats(data.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Có lỗi xảy ra');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchLessonsStats = async (lessons: Lesson[]) => {
    const statsMap = new Map<number, LessonStats>();

    await Promise.all(
      lessons.map(async (lesson) => {
        try {
          // Fetch sentence count
          const countResponse = await fetch(
            `http://localhost:8000/api/v1/lessons/${lesson.id}/sentences-count`
          );
          const countData = await countResponse.json();

          const stats: LessonStats = {
            lesson_id: lesson.id,
            sentence_count: countData.sentences_count || 0,
          };

          // Fetch progress
          if (isAuthenticated) {
            // Authenticated: get from server
            try {
              const token = getAccessToken();
              const progressResponse = await fetch(
                `http://localhost:8000/api/v1/practice/stats?lesson_id=${lesson.id}`,
                {
                  headers: {
                    Authorization: `Bearer ${token}`,
                  },
                }
              );
              
              if (progressResponse.ok) {
                const progressData = await progressResponse.json();
                stats.progress = {
                  total_practiced: progressData.total_practiced || 0,
                  progress_percentage: stats.sentence_count > 0
                    ? Math.round((progressData.total_practiced / stats.sentence_count) * 100)
                    : 0,
                };
              }
            } catch (_err) {
              console.warn('Failed to fetch progress for lesson', lesson.id);
            }
          } else {
            // Guest: get from localStorage
            const storageKey = `practiced_${lesson.id}`;
            const stored = localStorage.getItem(storageKey);
            if (stored) {
              try {
                const practicedIds = JSON.parse(stored);
                const practicedCount = Array.isArray(practicedIds) ? practicedIds.length : 0;
                stats.progress = {
                  total_practiced: practicedCount,
                  progress_percentage: stats.sentence_count > 0
                    ? Math.round((practicedCount / stats.sentence_count) * 100)
                    : 0,
                };
              } catch (_err) {
                console.warn('Failed to parse localStorage for lesson', lesson.id);
              }
            }
          }

          statsMap.set(lesson.id, stats);
        } catch (_err) {
          console.warn('Failed to fetch stats for lesson', lesson.id);
        }
      })
    );

    setLessonsStats(statsMap);
  };

const handleSearch = (e: React.FormEvent) => {
  e.preventDefault();
  setCurrentPage(1);
  fetchLessons();
};

const renderPageNumbers = () => {
    if (!pagination) return null;

    const pages = [];
    const maxPagesToShow = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxPagesToShow / 2));
    let endPage = Math.min(pagination.total_pages, startPage + maxPagesToShow - 1);

    if (endPage - startPage < maxPagesToShow - 1) {
      startPage = Math.max(1, endPage - maxPagesToShow + 1);
    }

    for (let i = startPage; i <= endPage; i++) {
      pages.push(
        <button
          key={i}
          onClick={() => setCurrentPage(i)}
          className={`w-10 h-10 rounded-xl font-bold transition-all duration-200 ${
            i === currentPage
              ? 'bg-gradient-to-r from-indigo-600 to-indigo-500 text-white shadow-lg'
              : 'bg-white border-2 border-gray-200 text-gray-700 hover:border-indigo-300 hover:bg-indigo-50'
          }`}
          style={{ fontFamily: "'Baloo 2', cursive" }}
        >
          {i}
        </button>
      );
    }

    return pages;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b-2 border-indigo-100 sticky top-0 z-10 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-gradient-to-br from-indigo-600 to-indigo-500 rounded-2xl flex items-center justify-center shadow-lg">
                <BookOpen className="w-7 h-7 text-white" strokeWidth={2.5} />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900" style={{ fontFamily: "'Baloo 2', cursive" }}>
                  Danh sách bài học
                </h1>
                <p className="text-gray-600 text-sm" style={{ fontFamily: "'Comic Neue', cursive" }}>
                  Chọn bài học để bắt đầu luyện tập
                </p>
              </div>
            </div>
            
            <Link
              to="/"
              className="px-4 py-2 bg-white border-2 border-gray-300 text-gray-700 rounded-xl font-semibold hover:bg-gray-50 transition-all duration-200"
              style={{ fontFamily: "'Baloo 2', cursive" }}
            >
              ← Trang chủ
            </Link>
          </div>

          {/* Search and Filters */}
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <form onSubmit={handleSearch} className="flex-1">
              <div className="relative">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" strokeWidth={2.5} />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Tìm kiếm bài học..."
                  className="w-full pl-12 pr-4 py-3 rounded-xl border-2 border-gray-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all duration-200"
                  style={{ fontFamily: "'Comic Neue', cursive" }}
                />
              </div>
            </form>

            {/* Filter & Sort */}
            <div className="flex gap-3">
              <select
                value={filterActive === null ? 'all' : filterActive.toString()}
                onChange={(e) => setFilterActive(e.target.value === 'all' ? null : e.target.value === 'true')}
                className="px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all duration-200 cursor-pointer"
                style={{ fontFamily: "'Comic Neue', cursive" }}
              >
                <option value="all">Tất cả</option>
                <option value="true">Đang hoạt động</option>
                <option value="false">Không hoạt động</option>
              </select>

              <select
                value={`${sortBy}_${sortOrder}`}
                onChange={(e) => {
                  const [newSortBy, newSortOrder] = e.target.value.split('_');
                  setSortBy(newSortBy as 'created_at' | 'order_index');
                  setSortOrder(newSortOrder as 'asc' | 'desc');
                }}
                className="px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all duration-200 cursor-pointer"
                style={{ fontFamily: "'Comic Neue', cursive" }}
              >
                <option value="order_index_asc">Thứ tự tăng dần</option>
                <option value="order_index_desc">Thứ tự giảm dần</option>
                <option value="created_at_asc">Ngày tạo cũ nhất</option>
                <option value="created_at_desc">Ngày tạo mới nhất</option>
              </select>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {isLoading ? (
          // Loading Skeleton
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="bg-white/80 backdrop-blur-sm rounded-3xl p-6 shadow-lg animate-pulse">
                <div className="h-6 bg-gray-200 rounded-xl mb-4 w-3/4"></div>
                <div className="h-4 bg-gray-200 rounded-lg mb-2"></div>
                <div className="h-4 bg-gray-200 rounded-lg mb-4 w-5/6"></div>
                <div className="h-10 bg-gray-200 rounded-xl"></div>
              </div>
            ))}
          </div>
        ) : error ? (
          // Error State
          <div className="max-w-md mx-auto text-center py-16">
            <div className="bg-white/80 backdrop-blur-sm rounded-3xl p-8 shadow-2xl border-2 border-red-200">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <FileText className="w-8 h-8 text-red-600" strokeWidth={2.5} />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2" style={{ fontFamily: "'Baloo 2', cursive" }}>
                Có lỗi xảy ra
              </h3>
              <p className="text-gray-600 mb-6" style={{ fontFamily: "'Comic Neue', cursive" }}>
                {error}
              </p>
              <button
                onClick={fetchLessons}
                className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-indigo-500 text-white rounded-xl font-bold hover:shadow-lg transition-all duration-200"
                style={{ fontFamily: "'Baloo 2', cursive" }}
              >
                Thử lại
              </button>
            </div>
          </div>
        ) : lessons.length === 0 ? (
          // Empty State
          <div className="max-w-md mx-auto text-center py-16">
            <div className="bg-white/80 backdrop-blur-sm rounded-3xl p-8 shadow-2xl">
              <div className="w-20 h-20 bg-gradient-to-br from-indigo-100 to-purple-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <BookOpen className="w-10 h-10 text-indigo-600" strokeWidth={2.5} />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-3" style={{ fontFamily: "'Baloo 2', cursive" }}>
                Chưa có bài học nào
              </h3>
              <p className="text-gray-600 mb-6" style={{ fontFamily: "'Comic Neue', cursive" }}>
                {searchQuery
                  ? 'Không tìm thấy bài học phù hợp. Thử tìm kiếm với từ khóa khác.'
                  : 'Danh sách bài học đang trống. Vui lòng quay lại sau.'}
              </p>
              {searchQuery && (
                <button
                  onClick={() => {
                    setSearchQuery('');
                    setCurrentPage(1);
                  }}
                  className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-indigo-500 text-white rounded-xl font-bold hover:shadow-lg transition-all duration-200"
                  style={{ fontFamily: "'Baloo 2', cursive" }}
                >
                  Xóa tìm kiếm
                </button>
              )}
            </div>
          </div>
        ) : (
          <>
            {/* Lessons Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
              {lessons.map((lesson, index) => {
                const stats = lessonsStats.get(lesson.id);
                const progress = stats?.progress;

                return (
                  <div
                    key={lesson.id}
                    className="group bg-white/80 backdrop-blur-sm rounded-3xl p-6 shadow-lg hover:shadow-2xl transition-all duration-300 hover:-translate-y-2 border-2 border-white/50 cursor-pointer relative overflow-hidden"
                    style={{
                      animationDelay: `${index * 50}ms`,
                      animation: 'fadeInUp 0.5s ease-out forwards',
                    }}
                  >
                    {/* Background decoration */}
                    <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-indigo-100 to-purple-100 rounded-full -translate-y-16 translate-x-16 opacity-50 group-hover:scale-150 transition-transform duration-500"></div>
                    
                    {/* Badge & Circular Progress */}
                    <div className="relative mb-4 flex items-center justify-between">
                      <div className="inline-flex items-center gap-2 px-3 py-1 bg-gradient-to-r from-indigo-500 to-indigo-400 text-white text-sm rounded-full font-semibold shadow-md">
                        <Sparkles className="w-4 h-4" strokeWidth={2.5} />
                        <span style={{ fontFamily: "'Comic Neue', cursive" }}>
                          Bài {lesson.order_index}
                        </span>
                      </div>
                      
                      {/* Circular Progress */}
                      {progress && (
                        <div className="relative w-12 h-12">
                          <svg className="w-12 h-12 transform -rotate-90" viewBox="0 0 36 36">
                            {/* Background circle */}
                            <circle
                              cx="18"
                              cy="18"
                              r="15.5"
                              fill="none"
                              stroke="#E5E7EB"
                              strokeWidth="3"
                            />
                            {/* Progress circle */}
                            <circle
                              cx="18"
                              cy="18"
                              r="15.5"
                              fill="none"
                              stroke="url(#gradient-${lesson.id})"
                              strokeWidth="3"
                              strokeDasharray={`${progress.progress_percentage}, 100`}
                              strokeLinecap="round"
                              className="transition-all duration-500"
                            />
                            {/* Gradient definition */}
                            <defs>
                              <linearGradient id={`gradient-${lesson.id}`} x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" stopColor="#22C55E" />
                                <stop offset="100%" stopColor="#10B981" />
                              </linearGradient>
                            </defs>
                          </svg>
                          {/* Percentage text */}
                          <div className="absolute inset-0 flex items-center justify-center">
                            <span 
                              className="text-xs font-bold text-gray-700"
                              style={{ fontFamily: "'Baloo 2', cursive" }}
                            >
                              {progress.progress_percentage}%
                            </span>
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Content */}
                    <h3 className="text-xl font-bold text-gray-900 mb-2 relative" style={{ fontFamily: "'Baloo 2', cursive" }}>
                      {lesson.title}
                    </h3>
                    
                    <p className="text-gray-600 mb-4 line-clamp-2 relative" style={{ fontFamily: "'Comic Neue', cursive" }}>
                      {lesson.description}
                    </p>

                    {/* Stats */}
                    <div className="flex items-center gap-4 mb-4 text-sm relative">
                      <div className="flex items-center gap-1 text-gray-600">
                        <FileText className="w-4 h-4" strokeWidth={2.5} />
                        <span style={{ fontFamily: "'Comic Neue', cursive" }}>
                          {stats?.sentence_count || 0} câu
                        </span>
                      </div>
                      {progress && (
                        <div className="flex items-center gap-1 text-green-600">
                          <TrendingUp className="w-4 h-4" strokeWidth={2.5} />
                          <span style={{ fontFamily: "'Comic Neue', cursive" }}>
                            {progress.progress_percentage}% hoàn thành
                          </span>
                        </div>
                      )}
                    </div>

                    {/* Progress Bar */}
                    {progress && (
                      <div className="mb-4 relative">
                        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-gradient-to-r from-green-500 to-green-400 transition-all duration-500 rounded-full"
                            style={{ width: `${progress.progress_percentage}%` }}
                          ></div>
                        </div>
                      </div>
                    )}

                    {/* Buttons */}
                    <div className="relative flex gap-2">
                      <Link
                        to={`/lessons/${lesson.id}`}
                        className="flex-1 bg-gradient-to-r from-purple-600 to-purple-500 text-white px-4 py-3 rounded-xl font-bold shadow-lg hover:shadow-xl transition-all duration-200 flex items-center justify-center gap-2 group/btn"
                        style={{ fontFamily: "'Baloo 2', cursive" }}
                      >
                        <BookOpen className="w-5 h-5" strokeWidth={2.5} />
                        <span>Chi tiết</span>
                      </Link>
                      <Link
                        to={`/practice?lesson_id=${lesson.id}`}
                        className="flex-1 bg-gradient-to-r from-indigo-600 to-indigo-500 text-white px-4 py-3 rounded-xl font-bold shadow-lg hover:shadow-xl transition-all duration-200 flex items-center justify-center gap-2 group/btn"
                        style={{ fontFamily: "'Baloo 2', cursive" }}
                      >
                        <span>Luyện tập</span>
                        <ArrowRight className="w-5 h-5 group-hover/btn:translate-x-1 transition-transform" strokeWidth={2.5} />
                      </Link>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Pagination */}
            {pagination && pagination.total_pages > 1 && (
              <div className="flex items-center justify-center gap-2">
                <button
                  onClick={() => setCurrentPage(currentPage - 1)}
                  disabled={!pagination.has_prev}
                  className="w-10 h-10 rounded-xl bg-white border-2 border-gray-200 text-gray-700 hover:border-indigo-300 hover:bg-indigo-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center"
                >
                  <ChevronLeft className="w-5 h-5" strokeWidth={2.5} />
                </button>

                {renderPageNumbers()}

                <button
                  onClick={() => setCurrentPage(currentPage + 1)}
                  disabled={!pagination.has_next}
                  className="w-10 h-10 rounded-xl bg-white border-2 border-gray-200 text-gray-700 hover:border-indigo-300 hover:bg-indigo-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center"
                >
                  <ChevronRight className="w-5 h-5" strokeWidth={2.5} />
                </button>
              </div>
            )}
          </>
        )}
      </main>

      {/* Keyframes for animation */}
      <style>{`
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  );
}
