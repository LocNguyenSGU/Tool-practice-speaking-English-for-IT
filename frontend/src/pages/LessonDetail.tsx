import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { 
  ArrowLeft, 
  Play, 
  Pause,
  BookOpen,
  Calendar,
  FileText,
  TrendingUp,
  Sparkles,
  AlertCircle,
  ChevronLeft,
  ChevronRight
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

interface Sentence {
  id: number;
  lesson_id: number;
  vi_text: string;
  en_text: string;
  vi_audio_url: string;
  en_audio_url: string;
  order_index: number;
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

interface PracticeStats {
  total_practiced: number;
  total_practice_count: number;
  recent_practiced_count: number;
}

export default function LessonDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [sentences, setSentences] = useState<Sentence[]>([]);
  const [pagination, setPagination] = useState<PaginationInfo | null>(null);
  const [practiceStats, setPracticeStats] = useState<PracticeStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [playingAudio, setPlayingAudio] = useState<{ sentenceId: number; lang: 'vi' | 'en' } | null>(null);
  
  const audioRef = useRef<HTMLAudioElement>(null);

  useEffect(() => {
    if (id) {
      fetchLessonData();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id, currentPage]);

  const fetchLessonData = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Fetch lesson details
      const lessonResponse = await fetch(`http://localhost:8000/api/v1/lessons/${id}`);
      if (!lessonResponse.ok) {
        throw new Error('Failed to fetch lesson');
      }
      const lessonData = await lessonResponse.json();
      setLesson(lessonData);

      // Fetch sentences
      const params = new URLSearchParams({
        lesson_id: id!,
        page: currentPage.toString(),
        limit: '50'
      });
      const sentencesResponse = await fetch(`http://localhost:8000/api/v1/sentences?${params}`);
      if (!sentencesResponse.ok) {
        throw new Error('Failed to fetch sentences');
      }
      const sentencesData = await sentencesResponse.json();
      setSentences(sentencesData.items);
      setPagination(sentencesData.pagination);

      // Fetch practice stats if authenticated
      const token = getAccessToken();
      if (token) {
        try {
          const statsParams = new URLSearchParams({ lesson_id: id! });
          const statsResponse = await fetch(
            `http://localhost:8000/api/v1/practice/stats?${statsParams}`,
            {
              headers: {
                'Authorization': `Bearer ${token}`
              }
            }
          );
          if (statsResponse.ok) {
            const statsData = await statsResponse.json();
            setPracticeStats(statsData);
          }
        } catch (err) {
          console.warn('Failed to fetch practice stats:', err);
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const handlePlayAudio = async (sentenceId: number, lang: 'vi' | 'en') => {
    const sentence = sentences.find(s => s.id === sentenceId);
    if (!sentence) return;

    const audioUrl = lang === 'vi' ? sentence.vi_audio_url : sentence.en_audio_url;
    
    // If same audio is playing, pause it
    if (playingAudio?.sentenceId === sentenceId && playingAudio?.lang === lang) {
      audioRef.current?.pause();
      setPlayingAudio(null);
      return;
    }

    // Play new audio
    if (audioRef.current) {
      audioRef.current.src = `http://localhost:8000${audioUrl}`;
      setPlayingAudio({ sentenceId, lang });
      try {
        await audioRef.current.play();
      } catch (err) {
        console.error('Failed to play audio:', err);
        setPlayingAudio(null);
      }
    }
  };

  const handleAudioEnded = () => {
    setPlayingAudio(null);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('vi-VN', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 dark:from-gray-900 dark:via-indigo-950 dark:to-purple-950 p-4 md:p-8">
        <div className="max-w-6xl mx-auto">
          {/* Skeleton loader */}
          <div className="animate-pulse space-y-6">
            <div className="h-8 w-32 bg-indigo-200/50 dark:bg-indigo-800/50 rounded-lg"></div>
            <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl p-8 space-y-4">
              <div className="h-10 bg-indigo-200/50 dark:bg-indigo-800/50 rounded-lg w-3/4"></div>
              <div className="h-6 bg-indigo-200/50 dark:bg-indigo-800/50 rounded-lg w-full"></div>
              <div className="h-6 bg-indigo-200/50 dark:bg-indigo-800/50 rounded-lg w-2/3"></div>
            </div>
            <div className="space-y-3">
              {[1, 2, 3, 4, 5].map(i => (
                <div key={i} className="h-20 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-xl"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !lesson) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 dark:from-gray-900 dark:via-indigo-950 dark:to-purple-950 p-4 md:p-8">
        <div className="max-w-6xl mx-auto">
          <button
            onClick={() => navigate('/lessons')}
            className="flex items-center gap-2 px-4 py-2 text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 transition-colors duration-200 mb-6 cursor-pointer"
            style={{ fontFamily: "'Comic Neue', cursive" }}
          >
            <ArrowLeft size={20} />
            <span>Quay lại danh sách</span>
          </button>
          
          <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl p-8 text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-red-100 dark:bg-red-900/30 rounded-full mb-4">
              <AlertCircle className="text-red-600 dark:text-red-400" size={32} />
            </div>
            <h2 
              className="text-2xl font-bold text-gray-900 dark:text-white mb-2"
              style={{ fontFamily: "'Baloo 2', cursive" }}
            >
              Không thể tải bài học
            </h2>
            <p 
              className="text-gray-600 dark:text-gray-400 mb-6"
              style={{ fontFamily: "'Comic Neue', cursive" }}
            >
              {error || 'Bài học không tồn tại'}
            </p>
            <button
              onClick={fetchLessonData}
              className="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl transition-colors duration-200 cursor-pointer"
              style={{ fontFamily: "'Comic Neue', cursive" }}
            >
              Thử lại
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 dark:from-gray-900 dark:via-indigo-950 dark:to-purple-950 p-3 md:p-4">
      <audio ref={audioRef} onEnded={handleAudioEnded} className="hidden" />
      
      <div className="max-w-6xl mx-auto space-y-3">
        {/* Back Button */}
        <button
          onClick={() => navigate('/lessons')}
          className="flex items-center gap-1.5 px-3 py-1.5 text-sm text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 transition-colors duration-200 cursor-pointer"
          style={{ fontFamily: "'Comic Neue', cursive" }}
        >
          <ArrowLeft size={16} />
          <span>Quay lại</span>
        </button>

        {/* Lesson Header */}
        <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-xl p-4 md:p-5 shadow-lg border border-indigo-100 dark:border-indigo-900/50">
          <div className="flex items-start gap-4">
            {/* Icon Badge */}
            <div className="hidden md:flex items-center justify-center w-14 h-14 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl shrink-0 shadow-lg">
              <BookOpen className="text-white" size={28} />
            </div>
            
            <div className="flex-1">
              <div className="flex flex-wrap items-center gap-2 mb-2">
                <span 
                  className="px-2 py-0.5 bg-indigo-100 dark:bg-indigo-900/50 text-indigo-700 dark:text-indigo-300 rounded-full text-xs font-medium"
                  style={{ fontFamily: "'Comic Neue', cursive" }}
                >
                  Bài #{lesson.order_index}
                </span>
                {lesson.is_active && (
                  <span 
                    className="px-2 py-0.5 bg-green-100 dark:bg-green-900/50 text-green-700 dark:text-green-300 rounded-full text-xs font-medium flex items-center gap-1"
                    style={{ fontFamily: "'Comic Neue', cursive" }}
                  >
                    <Sparkles size={12} />
                    Active
                  </span>
                )}
              </div>
              
              <h1 
                className="text-xl md:text-2xl font-bold text-gray-900 dark:text-white mb-2"
                style={{ fontFamily: "'Baloo 2', cursive" }}
              >
                {lesson.title}
              </h1>
              
              <p 
                className="text-sm text-gray-700 dark:text-gray-300 mb-3"
                style={{ fontFamily: "'Comic Neue', cursive" }}
              >
                {lesson.description}
              </p>

              {/* Metadata */}
              <div className="flex flex-wrap items-center gap-3 text-xs text-gray-600 dark:text-gray-400">
                <div className="flex items-center gap-1.5">
                  <Calendar size={14} />
                  <span style={{ fontFamily: "'Comic Neue', cursive" }}>
                    {formatDate(lesson.created_at)}
                  </span>
                </div>
                <div className="flex items-center gap-1.5">
                  <FileText size={14} />
                  <span style={{ fontFamily: "'Comic Neue', cursive" }}>
                    {pagination?.total_items || 0} câu
                  </span>
                </div>
                {/* Progress Badge (if authenticated) */}
                {practiceStats && (
                  <div className="flex items-center gap-1.5 px-2 py-1 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-lg border border-green-200 dark:border-green-800">
                    <TrendingUp className="text-green-600 dark:text-green-400" size={14} />
                    <span 
                      className="text-green-700 dark:text-green-300 font-medium"
                      style={{ fontFamily: "'Comic Neue', cursive" }}
                    >
                      {practiceStats.total_practiced}/{pagination?.total_items || 0}
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Action Button */}
        <Link
          to={`/practice?lesson_id=${lesson.id}`}
          className="block w-full md:w-auto"
        >
          <button 
            className="w-full md:w-auto px-5 py-2.5 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white rounded-lg font-bold text-base shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200 cursor-pointer flex items-center justify-center gap-2"
            style={{ fontFamily: "'Baloo 2', cursive" }}
          >
            <Sparkles size={18} />
            Bắt đầu luyện tập
          </button>
        </Link>

        {/* Sentences Section */}
        <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-xl p-4 shadow-lg border border-indigo-100 dark:border-indigo-900/50">
          <h2 
            className="text-lg font-bold text-gray-900 dark:text-white mb-3 flex items-center gap-2"
            style={{ fontFamily: "'Baloo 2', cursive" }}
          >
            <FileText size={20} />
            Danh sách câu
          </h2>

          {sentences.length === 0 ? (
            <div className="text-center py-12">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-100 dark:bg-gray-700 rounded-full mb-4">
                <FileText className="text-gray-400 dark:text-gray-500" size={32} />
              </div>
              <p 
                className="text-gray-600 dark:text-gray-400 text-lg"
                style={{ fontFamily: "'Comic Neue', cursive" }}
              >
                Bài học chưa có câu nào
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              {sentences.map((sentence) => (
                <div
                  key={sentence.id}
                  className="bg-gradient-to-r from-white to-indigo-50/50 dark:from-gray-700/50 dark:to-indigo-900/20 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden"
                >
                  <div className="flex items-center gap-2 p-2">
                    {/* Order Index */}
                    <div className="shrink-0 w-7 h-7 bg-indigo-100 dark:bg-indigo-900/50 rounded-md flex items-center justify-center">
                      <span 
                        className="text-indigo-700 dark:text-indigo-300 font-bold text-xs"
                        style={{ fontFamily: "'Baloo 2', cursive" }}
                      >
                        {sentence.order_index}
                      </span>
                    </div>

                    {/* Texts Container */}
                    <div className="flex-1 grid grid-cols-1 md:grid-cols-2 gap-2">
                      {/* Vietnamese - Clickable */}
                      <button
                        onClick={() => handlePlayAudio(sentence.id, 'vi')}
                        className={`
                          w-full text-left px-3 py-2 rounded-lg border-2 transition-all duration-200 cursor-pointer
                          ${playingAudio?.sentenceId === sentence.id && playingAudio?.lang === 'vi'
                            ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/30 shadow-sm'
                            : 'border-transparent hover:border-indigo-300 dark:hover:border-indigo-700 hover:bg-indigo-50/50 dark:hover:bg-indigo-900/20'
                          }
                        `}
                      >
                        <div className="flex items-center gap-2">
                          <span className="text-sm shrink-0" role="img" aria-label="Vietnam flag">🇻🇳</span>
                          <p 
                            className="text-gray-900 dark:text-white font-medium text-sm flex-1"
                            style={{ fontFamily: "'Comic Neue', cursive" }}
                          >
                            {sentence.vi_text}
                          </p>
                          <div className="shrink-0">
                            {playingAudio?.sentenceId === sentence.id && playingAudio?.lang === 'vi' ? (
                              <Pause size={16} className="text-indigo-600 dark:text-indigo-400 animate-pulse" />
                            ) : (
                              <Play size={16} className="text-indigo-600 dark:text-indigo-400" />
                            )}
                          </div>
                        </div>
                      </button>

                      {/* English - Clickable */}
                      <button
                        onClick={() => handlePlayAudio(sentence.id, 'en')}
                        className={`
                          w-full text-left px-3 py-2 rounded-lg border-2 transition-all duration-200 cursor-pointer
                          ${playingAudio?.sentenceId === sentence.id && playingAudio?.lang === 'en'
                            ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/30 shadow-sm'
                            : 'border-transparent hover:border-purple-300 dark:hover:border-purple-700 hover:bg-purple-50/50 dark:hover:bg-purple-900/20'
                          }
                        `}
                      >
                        <div className="flex items-center gap-2">
                          <span className="text-sm shrink-0" role="img" aria-label="US flag">🇺🇸</span>
                          <p 
                            className="text-gray-700 dark:text-gray-300 text-sm flex-1"
                            style={{ fontFamily: "'Comic Neue', cursive" }}
                          >
                            {sentence.en_text}
                          </p>
                          <div className="shrink-0">
                            {playingAudio?.sentenceId === sentence.id && playingAudio?.lang === 'en' ? (
                              <Pause size={16} className="text-purple-600 dark:text-purple-400 animate-pulse" />
                            ) : (
                              <Play size={16} className="text-purple-600 dark:text-purple-400" />
                            )}
                          </div>
                        </div>
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Pagination */}
        {pagination && pagination.total_pages > 1 && (
          <div className="flex items-center justify-center gap-1.5">
            <button
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={!pagination.has_prev}
              className="p-1.5 bg-white/80 dark:bg-gray-800/80 rounded border border-gray-200 dark:border-gray-700 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-indigo-50 dark:hover:bg-indigo-900/20 transition-colors duration-200 cursor-pointer"
            >
              <ChevronLeft size={16} className="text-gray-700 dark:text-gray-300" />
            </button>
            
            <span 
              className="px-3 py-1 bg-white/80 dark:bg-gray-800/80 rounded border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300 text-xs"
              style={{ fontFamily: "'Comic Neue', cursive" }}
            >
              {pagination.page}/{pagination.total_pages}
            </span>
            
            <button
              onClick={() => setCurrentPage(p => Math.min(pagination.total_pages, p + 1))}
              disabled={!pagination.has_next}
              className="p-1.5 bg-white/80 dark:bg-gray-800/80 rounded border border-gray-200 dark:border-gray-700 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-indigo-50 dark:hover:bg-indigo-900/20 transition-colors duration-200 cursor-pointer"
            >
              <ChevronRight size={16} className="text-gray-700 dark:text-gray-300" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
