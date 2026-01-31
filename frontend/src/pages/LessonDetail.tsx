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
      <div className="min-h-screen bg-gray-50 p-4 md:p-8">
        <div className="max-w-6xl mx-auto">
          {/* Skeleton loader */}
          <div className="animate-pulse space-y-6">
            <div className="h-8 w-32 bg-gray-200 rounded-lg"></div>
            <div className="bg-white rounded-lg p-8 border border-gray-200 space-y-4">
              <div className="h-8 bg-gray-200 rounded-lg w-3/4"></div>
              <div className="h-5 bg-gray-200 rounded-lg w-full"></div>
              <div className="h-5 bg-gray-200 rounded-lg w-2/3"></div>
            </div>
            <div className="space-y-3">
              {[1, 2, 3, 4, 5].map(i => (
                <div key={i} className="h-20 bg-white rounded-lg border border-gray-200"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !lesson) {
    return (
      <div className="min-h-screen bg-gray-50 p-4 md:p-8">
        <div className="max-w-6xl mx-auto">
          <button
            onClick={() => navigate('/lessons')}
            className="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:text-gray-900 transition-colors duration-200 mb-6 cursor-pointer"
          >
            <ArrowLeft size={20} strokeWidth={2} />
            <span>Quay lại danh sách</span>
          </button>
          
          <div className="bg-white rounded-lg p-8 border border-gray-200 text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-red-50 rounded-full mb-4">
              <AlertCircle className="text-red-600" size={32} strokeWidth={2} />
            </div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              Không thể tải bài học
            </h2>
            <p className="text-sm text-gray-600 mb-6">
              {error || 'Bài học không tồn tại'}
            </p>
            <button
              onClick={fetchLessonData}
              className="px-6 py-2.5 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors duration-200 cursor-pointer"
            >
              Thử lại
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8">
      <audio ref={audioRef} onEnded={handleAudioEnded} className="hidden" />
      
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Back Button */}
        <button
          onClick={() => navigate('/lessons')}
          className="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:text-gray-900 transition-colors duration-200 cursor-pointer"
        >
          <ArrowLeft size={18} strokeWidth={2} />
          <span>Quay lại danh sách</span>
        </button>

        {/* Lesson Header */}
        <div className="bg-white rounded-lg p-6 md:p-8 border border-gray-200 shadow-sm">
          <div className="flex items-start gap-4">
            {/* Icon Badge */}
            <div className="hidden md:flex items-center justify-center w-12 h-12 bg-indigo-100 rounded-lg shrink-0">
              <BookOpen className="text-indigo-600" size={24} strokeWidth={2} />
            </div>
            
            <div className="flex-1">
              <div className="flex flex-wrap items-center gap-2 mb-3">
                <span className="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-md text-xs font-medium">
                  Bài #{lesson.order_index}
                </span>
                {lesson.is_active && (
                  <span className="px-3 py-1 bg-green-50 text-green-700 rounded-md text-xs font-medium">
                    Active
                  </span>
                )}
              </div>
              
              <h1 className="text-2xl md:text-3xl font-semibold text-gray-900 mb-3">
                {lesson.title}
              </h1>
              
              <p className="text-sm text-gray-600 mb-4 leading-relaxed">
                {lesson.description}
              </p>

              {/* Metadata */}
              <div className="flex flex-wrap items-center gap-4 text-xs text-gray-600">
                <div className="flex items-center gap-1.5">
                  <Calendar size={16} strokeWidth={2} />
                  <span>{formatDate(lesson.created_at)}</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <FileText size={16} strokeWidth={2} />
                  <span>{pagination?.total_items || 0} câu</span>
                </div>
                {practiceStats && (
                  <div className="flex items-center gap-1.5 px-3 py-1.5 bg-green-50 rounded-md border border-green-200">
                    <TrendingUp className="text-cta" size={16} strokeWidth={2} />
                    <span className="text-cta font-medium">
                      {practiceStats.total_practiced}/{pagination?.total_items || 0} đã học
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
          <button className="w-full md:w-auto px-6 py-3 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors duration-200 cursor-pointer">
            Bắt đầu luyện tập
          </button>
        </Link>

        {/* Sentences Section */}
        <div className="bg-white rounded-lg p-6 border border-gray-200 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <FileText size={20} strokeWidth={2} />
            Danh sách câu
          </h2>

          {sentences.length === 0 ? (
            <div className="text-center py-12">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-100 rounded-full mb-4">
                <FileText className="text-gray-400" size={32} strokeWidth={2} />
              </div>
              <p className="text-gray-600 text-sm">
                Bài học chưa có câu nào
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              {sentences.map((sentence) => (
                <div
                  key={sentence.id}
                  className="bg-gray-50 rounded-lg border border-gray-200 overflow-hidden hover:border-gray-300 transition-colors duration-200"
                >
                  <div className="flex items-center gap-3 p-4">
                    {/* Order Index */}
                    <div className="shrink-0 w-8 h-8 bg-indigo-100 rounded-md flex items-center justify-center">
                      <span className="text-indigo-700 font-semibold text-sm">
                        {sentence.order_index}
                      </span>
                    </div>

                    {/* Texts Container */}
                    <div className="flex-1 grid grid-cols-1 md:grid-cols-2 gap-3">
                      {/* Vietnamese - Clickable */}
                      <button
                        onClick={() => handlePlayAudio(sentence.id, 'vi')}
                        className={`
                          w-full text-left px-4 py-3 rounded-lg border transition-all duration-200 cursor-pointer
                          ${playingAudio?.sentenceId === sentence.id && playingAudio?.lang === 'vi'
                            ? 'border-indigo-600 bg-indigo-50'
                            : 'border-gray-200 hover:border-indigo-300 hover:bg-indigo-50'
                          }
                        `}
                      >
                        <div className="flex items-center gap-3">
                          <span className="text-base shrink-0" role="img" aria-label="Vietnam flag">🇻🇳</span>
                          <p className="text-gray-900 font-medium text-sm flex-1">
                            {sentence.vi_text}
                          </p>
                          <div className="shrink-0">
                            {playingAudio?.sentenceId === sentence.id && playingAudio?.lang === 'vi' ? (
                              <Pause size={18} className="text-indigo-600" strokeWidth={2} />
                            ) : (
                              <Play size={18} className="text-gray-400" strokeWidth={2} />
                            )}
                          </div>
                        </div>
                      </button>

                      {/* English - Clickable */}
                      <button
                        onClick={() => handlePlayAudio(sentence.id, 'en')}
                        className={`
                          w-full text-left px-4 py-3 rounded-lg border transition-all duration-200 cursor-pointer
                          ${playingAudio?.sentenceId === sentence.id && playingAudio?.lang === 'en'
                            ? 'border-indigo-400 bg-indigo-50'
                            : 'border-gray-200 hover:border-indigo-300 hover:bg-indigo-50'
                          }
                        `}
                      >
                        <div className="flex items-center gap-3">
                          <span className="text-base shrink-0" role="img" aria-label="US flag">🇺🇸</span>
                          <p className="text-gray-700 text-sm flex-1">
                            {sentence.en_text}
                          </p>
                          <div className="shrink-0">
                            {playingAudio?.sentenceId === sentence.id && playingAudio?.lang === 'en' ? (
                              <Pause size={18} className="text-indigo-600" strokeWidth={2} />
                            ) : (
                              <Play size={18} className="text-gray-400" strokeWidth={2} />
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
          <div className="flex items-center justify-center gap-2">
            <button
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={!pagination.has_prev}
              className="w-10 h-10 rounded-lg bg-white border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 transition-colors duration-200 cursor-pointer flex items-center justify-center"
            >
              <ChevronLeft size={18} className="text-gray-700" strokeWidth={2} />
            </button>
            
            <span className="px-4 py-2 bg-white rounded-lg border border-gray-300 text-gray-700 text-sm font-medium">
              {pagination.page}/{pagination.total_pages}
            </span>
            
            <button
              onClick={() => setCurrentPage(p => Math.min(pagination.total_pages, p + 1))}
              disabled={!pagination.has_next}
              className="w-10 h-10 rounded-lg bg-white border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 transition-colors duration-200 cursor-pointer flex items-center justify-center"
            >
              <ChevronRight size={18} className="text-gray-700" strokeWidth={2} />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
