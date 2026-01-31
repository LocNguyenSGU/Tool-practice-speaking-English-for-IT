import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Search, 
  BookOpen, 
  ArrowRight, 
  ChevronLeft, 
  ChevronRight,
  FileText,
  TrendingUp
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
          className={`min-w-[40px] h-10 px-3 rounded-lg font-medium transition-colors duration-200 ${
            i === currentPage
              ? 'bg-indigo-600 text-white'
              : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
          }`}
        >
          {i}
        </button>
      );
    }

    return pages;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 flex items-center justify-center">
                <BookOpen className="w-6 h-6 text-indigo-600" strokeWidth={2} />
              </div>
              <div>
                <h1 className="text-2xl font-semibold text-gray-900">
                  Danh sách bài học
                </h1>
                <p className="text-sm text-gray-600 mt-0.5">
                  Chọn bài học để bắt đầu luyện tập
                </p>
              </div>
            </div>
            
            <Link
              to="/"
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors duration-200"
            >
              ← Trang chủ
            </Link>
          </div>

          {/* Search and Filters */}
          <div className="flex flex-col md:flex-row gap-3">
            {/* Search */}
            <form onSubmit={handleSearch} className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" strokeWidth={2} />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Tìm kiếm bài học..."
                  className="w-full pl-10 pr-4 py-2.5 text-sm rounded-lg border border-gray-300 focus:border-indigo-600 focus:ring-2 focus:ring-indigo-200 transition-all duration-200 outline-none"
                />
              </div>
            </form>

            {/* Filter & Sort */}
            <div className="flex gap-2">
              <select
                value={filterActive === null ? 'all' : filterActive.toString()}
                onChange={(e) => setFilterActive(e.target.value === 'all' ? null : e.target.value === 'true')}
                className="px-3 py-2.5 text-sm rounded-lg border border-gray-300 focus:border-indigo-600 focus:ring-2 focus:ring-indigo-200 transition-all duration-200 outline-none cursor-pointer bg-white"
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
                className="px-3 py-2.5 text-sm rounded-lg border border-gray-300 focus:border-indigo-600 focus:ring-2 focus:ring-indigo-200 transition-all duration-200 outline-none cursor-pointer bg-white"
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
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {isLoading ? (
          // Loading Skeleton
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="bg-white rounded-lg p-6 border border-gray-200 animate-pulse">
                <div className="h-5 bg-gray-200 rounded w-3/4 mb-3"></div>
                <div className="h-4 bg-gray-200 rounded mb-2"></div>
                <div className="h-4 bg-gray-200 rounded w-5/6 mb-4"></div>
                <div className="h-10 bg-gray-200 rounded"></div>
              </div>
            ))}
          </div>
        ) : error ? (
          // Error State
          <div className="max-w-md mx-auto text-center py-16">
            <div className="bg-white rounded-lg p-8 border border-gray-200 shadow-sm">
              <div className="w-12 h-12 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-4">
                <FileText className="w-6 h-6 text-red-600" strokeWidth={2} />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Có lỗi xảy ra
              </h3>
              <p className="text-sm text-gray-600 mb-6">
                {error}
              </p>
              <button
                onClick={fetchLessons}
                className="px-6 py-2.5 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors duration-200"
              >
                Thử lại
              </button>
            </div>
          </div>
        ) : lessons.length === 0 ? (
          // Empty State
          <div className="max-w-md mx-auto text-center py-16">
            <div className="bg-white rounded-lg p-8 border border-gray-200 shadow-sm">
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <BookOpen className="w-8 h-8 text-gray-400" strokeWidth={2} />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Chưa có bài học nào
              </h3>
              <p className="text-sm text-gray-600 mb-6">
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
                  className="px-6 py-2.5 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors duration-200"
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
              {lessons.map((lesson) => {
                const stats = lessonsStats.get(lesson.id);
                const progress = stats?.progress;

                return (
                  <div
                    key={lesson.id}
                    className="bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-all duration-200 hover:-translate-y-1 relative overflow-hidden"
                  >
                    {/* Subtle background decoration */}
                    <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-50 rounded-full -translate-y-16 translate-x-16 opacity-50"></div>
                    
                    <div className="relative p-6">
                      {/* Badge & Circular Progress */}
                      <div className="flex items-center justify-between mb-4">
                        <div className="inline-flex items-center px-3 py-1 bg-indigo-100 text-indigo-700 text-xs font-medium rounded-md">
                          Bài {lesson.order_index}
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
                                stroke="#22C55E"
                                strokeWidth="3"
                                strokeDasharray={`${progress.progress_percentage}, 100`}
                                strokeLinecap="round"
                                className="transition-all duration-500"
                              />
                            </svg>
                            {/* Percentage text */}
                            <div className="absolute inset-0 flex items-center justify-center">
                              <span className="text-xs font-semibold text-gray-700">
                                {progress.progress_percentage}%
                              </span>
                            </div>
                          </div>
                        )}
                      </div>

                      {/* Content */}
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">
                        {lesson.title}
                      </h3>
                      
                      <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                        {lesson.description}
                      </p>

                      {/* Stats */}
                      <div className="flex items-center gap-4 mb-4 text-xs text-gray-600">
                        <div className="flex items-center gap-1">
                          <FileText className="w-4 h-4" strokeWidth={2} />
                          <span>{stats?.sentence_count || 0} câu</span>
                        </div>
                        {progress && (
                          <div className="flex items-center gap-1 text-cta">
                            <TrendingUp className="w-4 h-4" strokeWidth={2} />
                            <span>{progress.total_practiced} đã học</span>
                          </div>
                        )}
                      </div>

                      {/* Progress Bar */}
                      {progress && (
                        <div className="mb-4">
                          <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-cta transition-all duration-500 rounded-full"
                              style={{ width: `${progress.progress_percentage}%` }}
                            ></div>
                          </div>
                        </div>
                      )}

                      {/* Buttons */}
                      <div className="flex gap-2">
                        <Link
                          to={`/lessons/${lesson.id}`}
                          className="flex-1 bg-white border border-gray-300 text-gray-700 px-4 py-2.5 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors duration-200 flex items-center justify-center gap-2"
                        >
                          <BookOpen className="w-4 h-4" strokeWidth={2} />
                          <span>Chi tiết</span>
                        </Link>
                        <Link
                          to={`/practice?lesson_id=${lesson.id}`}
                          className="flex-1 bg-indigo-600 text-white px-4 py-2.5 rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors duration-200 flex items-center justify-center gap-2"
                        >
                          <span>Luyện tập</span>
                          <ArrowRight className="w-4 h-4 transition-transform" strokeWidth={2} />
                        </Link>
                      </div>
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
                  className="w-10 h-10 rounded-lg bg-white border border-gray-300 text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200 flex items-center justify-center"
                >
                  <ChevronLeft className="w-5 h-5" strokeWidth={2} />
                </button>

                {renderPageNumbers()}

                <button
                  onClick={() => setCurrentPage(currentPage + 1)}
                  disabled={!pagination.has_next}
                  className="w-10 h-10 rounded-lg bg-white border border-gray-300 text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200 flex items-center justify-center"
                >
                  <ChevronRight className="w-5 h-5" strokeWidth={2} />
                </button>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}
