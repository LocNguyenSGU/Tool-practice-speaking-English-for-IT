import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { 
  ArrowLeft,
  Play,
  Pause,
  Eye,
  EyeOff,
  Check,
  SkipForward,
  Trophy,
  Flame,
  Sparkles,
  List,
  X
} from 'lucide-react';
import { getAccessToken, refreshAccessToken, clearAuth } from '../utils/auth';

// =============================================================================
// TYPES
// =============================================================================
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

interface SentenceListItem {
  sentence_id: number;
  vietnamese: string;
  english: string;
  order_index: number;
}

interface Progress {
  practiced_count: number;
  total_in_lesson: number;
  percentage: number;
}

interface PracticeResponse {
  sentence: Sentence;
  progress: Progress;
}

interface RecordResponse {
  success: boolean;
  practiced_count: number;
  total_practice_count: number;
  streak_days: number;
}

// =============================================================================
// CONSTANTS
// =============================================================================
const API_BASE = 'http://localhost:8000/api/v1';

// =============================================================================
// HELPER FUNCTIONS (outside component to avoid recreation)
// =============================================================================

/** Check if user is authenticated */
const isAuthenticated = (): boolean => !!getAccessToken();

/** Get localStorage key for practiced IDs */
const getPracticedStorageKey = (lessonId: string): string => `practiced_${lessonId}`;

/** Load practiced IDs from localStorage (guest users only) */
const loadPracticedIdsFromStorage = (lessonId: string | null): Set<number> => {
  if (!lessonId || isAuthenticated()) return new Set();
  
  const stored = localStorage.getItem(getPracticedStorageKey(lessonId));
  if (stored) {
    try {
      return new Set(JSON.parse(stored));
    } catch {
      return new Set();
    }
  }
  return new Set();
};

/** Save practiced IDs to localStorage (guest users only) */
const savePracticedIdsToStorage = (lessonId: string, ids: Set<number>): void => {
  if (isAuthenticated() || ids.size === 0) return;
  localStorage.setItem(getPracticedStorageKey(lessonId), JSON.stringify([...ids]));
};

/** Fetch with auth and auto-refresh token */
const fetchWithAuth = async (
  url: string, 
  options: RequestInit = {}, 
  retryCount = 0
): Promise<Response> => {
  const token = getAccessToken();
  const headers = new Headers(options.headers);
  
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  
  const response = await fetch(url, { ...options, headers });
  
  if (response.status === 401 && retryCount === 0) {
    const newToken = await refreshAccessToken();
    if (newToken) {
      return fetchWithAuth(url, options, retryCount + 1);
    }
    clearAuth();
  }
  
  return response;
};

/** Convert API sentence to Sentence with audio URLs */
const mapToSentence = (s: Partial<Sentence> & { id: number }): Sentence => ({
  id: s.id,
  lesson_id: s.lesson_id || 0,
  vi_text: s.vi_text || '',
  en_text: s.en_text || '',
  order_index: s.order_index || 0,
  created_at: s.created_at || '',
  updated_at: s.updated_at || '',
  vi_audio_url: `/api/v1/audio/${s.id}/vi`,
  en_audio_url: `/api/v1/audio/${s.id}/en`
});

/** Calculate progress */
const calculateProgress = (practiced: number, total: number): Progress => ({
  practiced_count: practiced,
  total_in_lesson: total,
  percentage: total > 0 ? Math.round((practiced / total) * 100) : 0
});

// =============================================================================
// COMPONENT
// =============================================================================
export default function Practice() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const lessonId = searchParams.get('lesson_id');
  
  // ---------------------------------------------------------------------------
  // STATE
  // ---------------------------------------------------------------------------
  const [sentence, setSentence] = useState<Sentence | null>(null);
  const [progress, setProgress] = useState<Progress | null>(null);
  const [streakDays, setStreakDays] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [playingAudio, setPlayingAudio] = useState<'vi' | 'en' | null>(null);
  const [isCompleted, setIsCompleted] = useState(false);
  const [allSentences, setAllSentences] = useState<SentenceListItem[]>([]);
  const [practicedIds, setPracticedIds] = useState<Set<number>>(() => 
    loadPracticedIdsFromStorage(lessonId)
  );
  const [showSidebar, setShowSidebar] = useState(true);
  const [isReviewMode, setIsReviewMode] = useState(false);
  const [reviewIndex, setReviewIndex] = useState(0); // Current index in allSentences during review

  // ---------------------------------------------------------------------------
  // REFS
  // ---------------------------------------------------------------------------
  const audioRef = useRef<HTMLAudioElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // ---------------------------------------------------------------------------
  // PERSIST PRACTICED IDS (guest users only)
  // ---------------------------------------------------------------------------
  useEffect(() => {
    if (lessonId) {
      savePracticedIdsToStorage(lessonId, practicedIds);
    }
  }, [practicedIds, lessonId]);

  // ---------------------------------------------------------------------------
  // FETCH PRACTICED IDS (authenticated users only)
  // ---------------------------------------------------------------------------
  const fetchPracticedIds = useCallback(async (): Promise<Set<number>> => {
    if (!lessonId || !isAuthenticated()) return new Set();

    try {
      const response = await fetchWithAuth(`${API_BASE}/practice/practiced-ids?lesson_id=${lessonId}`);
      if (!response.ok) return new Set();

      const data = await response.json();
      const ids = new Set<number>(data.sentence_ids || []);
      setPracticedIds(ids);
      return ids;
    } catch {
      return new Set();
    }
  }, [lessonId]);

  // ---------------------------------------------------------------------------
  // FETCH ALL SENTENCES (for sidebar + review mode)
  // ---------------------------------------------------------------------------
  const fetchAllSentences = useCallback(async (): Promise<SentenceListItem[]> => {
    if (!lessonId) return [];

    try {
      const response = await fetch(`${API_BASE}/sentences?lesson_id=${lessonId}&page=1&limit=1000`);
      if (!response.ok) return [];

      const data = await response.json();
      const sentences: SentenceListItem[] = (data.items || [])
        .map((s: { id: number; vi_text: string; en_text: string; order_index: number }) => ({
          sentence_id: s.id,
          vietnamese: s.vi_text,
          english: s.en_text,
          order_index: s.order_index
        }))
        .sort((a: SentenceListItem, b: SentenceListItem) => a.order_index - b.order_index);
      
      setAllSentences(sentences);
      return sentences;
    } catch {
      return [];
    }
  }, [lessonId]);

  // ---------------------------------------------------------------------------
  // FETCH SENTENCE BY ID (for jump to sentence)
  // ---------------------------------------------------------------------------
  const fetchSentenceById = useCallback(async (sentenceId: number): Promise<Sentence | null> => {
    try {
      const response = await fetch(`${API_BASE}/sentences/${sentenceId}`);
      if (!response.ok) return null;
      return await response.json();
    } catch {
      return null;
    }
  }, []);

  // ---------------------------------------------------------------------------
  // FETCH NEXT SENTENCE (normal practice mode)
  // ---------------------------------------------------------------------------
  const fetchNextSentenceFromAPI = useCallback(async (): Promise<{
    sentence: Sentence | null;
    progress: Progress | null;
    completed: boolean;
  }> => {
    if (!lessonId) {
      return { sentence: null, progress: null, completed: false };
    }

    const response = await fetchWithAuth(`${API_BASE}/practice/next?lesson_id=${lessonId}`);
    
    if (response.status === 401) {
      // Fallback to guest mode
      const guestResponse = await fetch(`${API_BASE}/practice/next?lesson_id=${lessonId}`);
      if (!guestResponse.ok) {
        throw new Error('Failed to fetch next sentence');
      }
      const data = await guestResponse.json();
      return {
        sentence: data.sentence || null,
        progress: data.progress || null,
        completed: !data.sentence && data.progress?.practiced_count >= data.progress?.total_in_lesson
      };
    }
    
    if (response.status === 404) {
      throw new Error('Không tìm thấy câu nào trong bài học này');
    }
    
    if (!response.ok) {
      throw new Error('Failed to fetch next sentence');
    }

    const data: PracticeResponse = await response.json();
    
    return {
      sentence: data.sentence || null,
      progress: data.progress || null,
      completed: !data.sentence && data.progress?.practiced_count >= data.progress?.total_in_lesson
    };
  }, [lessonId]);

  // ---------------------------------------------------------------------------
  // CONFETTI ANIMATION
  // ---------------------------------------------------------------------------
  const triggerConfetti = useCallback(() => {
    if (!canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    interface Particle {
      x: number;
      y: number;
      r: number;
      d: number;
      color: string;
      tilt: number;
      tiltAngleIncremental: number;
      tiltAngle: number;
    }

    const particles: Particle[] = [];
    const colors = ['#4F46E5', '#818CF8', '#22C55E', '#F59E0B', '#EF4444', '#EC4899'];

    for (let i = 0; i < 150; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height - canvas.height,
        r: Math.random() * 6 + 2,
        d: Math.random() * 150,
        color: colors[Math.floor(Math.random() * colors.length)],
        tilt: Math.floor(Math.random() * 10) - 10,
        tiltAngleIncremental: Math.random() * 0.07 + 0.05,
        tiltAngle: 0
      });
    }

    let animationFrame: number;
    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];
        ctx.beginPath();
        ctx.lineWidth = p.r / 2;
        ctx.strokeStyle = p.color;
        ctx.moveTo(p.x + p.tilt + p.r, p.y);
        ctx.lineTo(p.x + p.tilt, p.y + p.tilt + p.r);
        ctx.stroke();

        p.tiltAngle += p.tiltAngleIncremental;
        p.y += (Math.cos(p.d) + 3 + p.r / 2) / 2;
        p.tilt = Math.sin(p.tiltAngle) * 15;

        if (p.y > canvas.height) {
          particles[i] = { ...p, x: Math.random() * canvas.width, y: -10 };
        }
      }

      animationFrame = requestAnimationFrame(draw);
    };

    draw();
    setTimeout(() => {
      cancelAnimationFrame(animationFrame);
      ctx.clearRect(0, 0, canvas.width, canvas.height);
    }, 5000);
  }, []);

  // ---------------------------------------------------------------------------
  // MARK LESSON COMPLETED
  // ---------------------------------------------------------------------------
  const markCompleted = useCallback((totalSentences: number) => {
    setIsCompleted(true);
    setProgress(calculateProgress(totalSentences, totalSentences));
    triggerConfetti();
  }, [triggerConfetti]);

  // ---------------------------------------------------------------------------
  // LOAD NEXT SENTENCE (handles both modes)
  // ---------------------------------------------------------------------------
  const loadNextSentence = useCallback(async () => {
    if (!lessonId) {
      setError('Lesson ID is required');
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);
    setShowAnswer(false);

    try {
      if (isReviewMode) {
        // REVIEW MODE: get sentence by order from allSentences
        let sentences = allSentences;
        if (sentences.length === 0) {
          sentences = await fetchAllSentences();
        }

        if (sentences.length === 0) {
          throw new Error('Không có câu nào trong bài học này');
        }

        if (reviewIndex >= sentences.length) {
          // Review complete
          markCompleted(sentences.length);
          setIsReviewMode(false);
          setReviewIndex(0);
          setIsLoading(false);
          return;
        }

        const nextItem = sentences[reviewIndex];
        const sentenceData = await fetchSentenceById(nextItem.sentence_id);
        
        if (!sentenceData) {
          throw new Error('Không tìm thấy câu này');
        }

        setSentence(mapToSentence(sentenceData));
        setProgress(calculateProgress(reviewIndex, sentences.length));
      } else {
        // NORMAL MODE: fetch from practice API
        const { sentence: newSentence, progress: newProgress, completed } = await fetchNextSentenceFromAPI();

        if (completed || !newSentence) {
          // All sentences practiced - mark completed
          if (isAuthenticated() && allSentences.length > 0) {
            setPracticedIds(new Set(allSentences.map(s => s.sentence_id)));
          }
          markCompleted(newProgress?.total_in_lesson || allSentences.length);
          return;
        }

        setSentence(newSentence);
        
        // Set progress based on auth status
        if (isAuthenticated()) {
          setProgress(newProgress || calculateProgress(0, 1));
        } else {
          // Guest: use localStorage count
          const total = newProgress?.total_in_lesson || 1;
          setProgress(calculateProgress(practicedIds.size, total));
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  }, [
    lessonId, 
    isReviewMode, 
    reviewIndex, 
    allSentences, 
    practicedIds.size,
    fetchAllSentences, 
    fetchSentenceById, 
    fetchNextSentenceFromAPI, 
    markCompleted
  ]);

  // ---------------------------------------------------------------------------
  // RECORD PRACTICE & GO NEXT
  // ---------------------------------------------------------------------------
  const recordPracticeAndNext = useCallback(async () => {
    if (!sentence) return;

    if (isReviewMode) {
      // Review mode: just move to next
      setReviewIndex(prev => prev + 1);
      return;
    }

    // Record practice
    if (isAuthenticated()) {
      try {
        const response = await fetchWithAuth(`${API_BASE}/practice/record`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ sentence_id: sentence.id })
        });

        if (response.ok) {
          const data: RecordResponse = await response.json();
          setStreakDays(data.streak_days);
          setPracticedIds(prev => new Set([...prev, sentence.id]));
        }
      } catch {
        // Silently fail, continue to next
      }
    } else {
      // Guest: update local state
      setPracticedIds(prev => {
        const updated = new Set([...prev, sentence.id]);
        // Update progress immediately
        if (progress) {
          setProgress(calculateProgress(updated.size, progress.total_in_lesson));
        }
        return updated;
      });
    }

    loadNextSentence();
  }, [sentence, isReviewMode, progress, loadNextSentence]);

  // ---------------------------------------------------------------------------
  // SKIP SENTENCE (don't record, just move to next)
  // ---------------------------------------------------------------------------
  const skipSentence = useCallback(() => {
    if (isReviewMode) {
      setReviewIndex(prev => prev + 1);
    } else {
      loadNextSentence();
    }
  }, [isReviewMode, loadNextSentence]);

  // ---------------------------------------------------------------------------
  // JUMP TO SPECIFIC SENTENCE
  // ---------------------------------------------------------------------------
  const jumpToSentence = useCallback(async (sentenceId: number) => {
    setIsLoading(true);
    setError(null);
    setShowAnswer(false);

    try {
      const sentenceData = await fetchSentenceById(sentenceId);
      if (!sentenceData) {
        throw new Error('Không tìm thấy câu này');
      }
      setSentence(sentenceData);
      
      // Close sidebar on mobile
      if (window.innerWidth < 1024) {
        setShowSidebar(false);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  }, [fetchSentenceById]);

  // ---------------------------------------------------------------------------
  // START REVIEW MODE
  // ---------------------------------------------------------------------------
  const startReviewMode = useCallback(() => {
    setIsCompleted(false);
    setIsReviewMode(true);
    setReviewIndex(0);
    setError(null);
    
    // For guest users: clear practiced IDs for UI (not localStorage)
    if (!isAuthenticated()) {
      setPracticedIds(new Set());
    }
    
    // Will trigger loadNextSentence via useEffect
  }, []);

  // ---------------------------------------------------------------------------
  // AUDIO PLAYBACK
  // ---------------------------------------------------------------------------
  const handlePlayAudio = useCallback(async (lang: 'vi' | 'en') => {
    if (!sentence || !audioRef.current) return;

    if (playingAudio === lang) {
      audioRef.current.pause();
      setPlayingAudio(null);
      return;
    }

    const audioUrl = lang === 'vi' ? sentence.vi_audio_url : sentence.en_audio_url;
    audioRef.current.src = `${API_BASE.replace('/api/v1', '')}${audioUrl}`;
    setPlayingAudio(lang);
    
    try {
      await audioRef.current.play();
    } catch {
      setPlayingAudio(null);
    }
  }, [sentence, playingAudio]);

  const handleAudioEnded = useCallback(() => {
    setPlayingAudio(null);
  }, []);

  // ---------------------------------------------------------------------------
  // INITIAL LOAD
  // ---------------------------------------------------------------------------
  useEffect(() => {
    if (lessonId) {
      fetchAllSentences();
      fetchPracticedIds(); // Load practiced IDs for authenticated users
      loadNextSentence();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lessonId]);

  // Load sentence when entering review mode or reviewIndex changes
  useEffect(() => {
    if (isReviewMode) {
      loadNextSentence();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isReviewMode, reviewIndex]);

  // ---------------------------------------------------------------------------
  // KEYBOARD SHORTCUTS
  // ---------------------------------------------------------------------------
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      // Ignore if typing in input
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }

      switch (e.key) {
        case ' ': // Space - Play Vietnamese
          e.preventDefault();
          if (sentence) handlePlayAudio('vi');
          break;
        case 'e':
        case 'E': // E - Play English
          e.preventDefault();
          if (sentence && showAnswer) handlePlayAudio('en');
          break;
        case 'Enter':
        case 'h':
        case 'H': // Enter or H - Toggle answer
          e.preventDefault();
          setShowAnswer(prev => !prev);
          break;
        case 'ArrowRight':
        case 'y':
        case 'Y': // Right Arrow or Y - Mastered
          e.preventDefault();
          if (sentence) recordPracticeAndNext();
          break;
        case 'ArrowLeft':
        case 's':
        case 'S': // Left Arrow or S - Skip
          e.preventDefault();
          if (sentence) skipSentence();
          break;
        case 'Escape': // Esc - Exit
          e.preventDefault();
          navigate(`/lessons/${lessonId}`);
          break;
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [sentence, showAnswer, lessonId, navigate, handlePlayAudio, recordPracticeAndNext, skipSentence]);

  // ---------------------------------------------------------------------------
  // RENDER: No lesson ID
  // ---------------------------------------------------------------------------

  if (!lessonId) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4" >
            Thiếu thông tin bài học
          </h1>
          <button
            onClick={() => navigate('/lessons')}
            className="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition-colors duration-200 cursor-pointer"
            
          >
            Quay lại danh sách
          </button>
        </div>
      </div>
    );
  }

  // ---------------------------------------------------------------------------
  // RENDER: Completed
  // ---------------------------------------------------------------------------
  if (isCompleted) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4 relative overflow-hidden">
        <canvas ref={canvasRef} className="absolute inset-0 pointer-events-none" />
        
        <div className="max-w-md w-full bg-white backdrop-blur-sm rounded-lg p-8 shadow-lg text-center relative z-10 border border-green-200">
          <div className="inline-flex items-center justify-center w-24 h-24 bg-gradient-to-br from-green-500 to-emerald-600 rounded-full mb-6 shadow-lg">
            <Trophy className="text-white" size={48} />
          </div>
          
          <h1 className="text-3xl font-bold text-gray-900 mb-3" >
            Xuất sắc! 🎉
          </h1>
          
          <p className="text-lg text-gray-700 mb-8" >
            Bạn đã hoàn thành tất cả câu trong bài học này!
          </p>

          {progress && (
            <div className="mb-4 text-sm text-gray-600">
              <p >
                Đã luyện: {progress.practiced_count}/{progress.total_in_lesson} câu
              </p>
            </div>
          )}

          {streakDays > 0 && (
            <div className="mb-6 inline-flex items-center gap-2 px-4 py-2 bg-orange-100 rounded-lg">
              <Flame className="text-orange-600" size={24} />
              <span className="text-orange-700 font-bold text-lg">
                Streak: {streakDays} ngày
              </span>
            </div>
          )}

          <div className="mb-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
            <p className="text-xs text-blue-700">
              ℹ️ <strong>Lưu ý:</strong> Tiến độ của bạn đã được lưu! "Ôn lại từ đầu" chỉ giúp bạn học lại các câu, không xóa tiến độ đã hoàn thành.
            </p>
          </div>

          <div className="flex flex-col gap-3">
            <button
              onClick={startReviewMode}
              className="w-full px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold transition-colors duration-200 cursor-pointer"
              
            >
              Ôn lại từ đầu
            </button>
            
            <button
              onClick={() => navigate('/lessons')}
              className="w-full px-6 py-3 bg-gray-200 hover:bg-gray-300 text-gray-900 rounded-lg font-bold transition-all duration-200 cursor-pointer"
              
            >
              Về danh sách bài học
            </button>
          </div>
        </div>
      </div>
    );
  }

  // ---------------------------------------------------------------------------
  // RENDER: Error
  // ---------------------------------------------------------------------------
  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white backdrop-blur-sm rounded-lg p-8 text-center shadow-xl">
          <h2 className="text-2xl font-bold text-gray-900 mb-4" >
            Có lỗi xảy ra
          </h2>
          <p className="text-gray-600 mb-6" >
            {error}
          </p>
          <div className="flex gap-3">
            <button
              onClick={loadNextSentence}
              className="flex-1 px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition-colors duration-200 cursor-pointer"
              
            >
              Thử lại
            </button>
            <button
              onClick={() => navigate(`/lessons/${lessonId}`)}
              className="flex-1 px-6 py-3 bg-gray-200 hover:bg-gray-300 text-gray-900 rounded-lg transition-colors duration-200 cursor-pointer"
              
            >
              Quay lại
            </button>
          </div>
        </div>
      </div>
    );
  }

  // ---------------------------------------------------------------------------
  // RENDER: Main Practice View
  // ---------------------------------------------------------------------------

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <audio ref={audioRef} onEnded={handleAudioEnded} className="hidden" />
      
      <div className="max-w-7xl mx-auto flex gap-4">
        {/* Main Content */}
        <div className={`flex-1 transition-all duration-300 ${showSidebar ? 'lg:mr-0' : ''}`}>
          {/* Header */}
          <div className="flex items-center justify-between mb-4">
            {/* Exit Button */}
            <button
              onClick={() => navigate(`/lessons/${lessonId}`)}
              className="flex items-center gap-2 px-3 py-2 text-gray-600 hover:text-gray-900 transition-colors duration-200 cursor-pointer"
              
            >
              <ArrowLeft size={20} />
              <span className="hidden sm:inline">Thoát</span>
            </button>

            <div className="flex items-center gap-2">
              {/* Review Mode Badge */}
              {isReviewMode && (
                <div className="flex items-center gap-2 px-3 py-2 bg-blue-100 rounded-lg shadow-sm">
                  <Sparkles className="text-blue-600" size={20} />
                  <span className="text-blue-700 font-bold text-sm">
                    Chế độ ôn tập
                  </span>
                </div>
              )}

              {/* Streak Badge */}
              {streakDays > 0 && (
                <div className="flex items-center gap-2 px-3 py-2 bg-orange-100 rounded-lg shadow-sm">
                  <Flame className="text-orange-600" size={20} />
                  <span className="text-orange-700 font-bold text-sm">
                    {streakDays} ngày
                  </span>
                </div>
              )}

              {/* Toggle Sidebar Button - visible on all screen sizes */}
              <button
                onClick={() => setShowSidebar(!showSidebar)}
                className="flex items-center gap-2 px-3 py-2 bg-indigo-100 text-indigo-700 rounded-lg transition-colors duration-200 cursor-pointer hover:bg-indigo-200"
              >
                {showSidebar ? <X size={20} /> : <List size={20} />}
                <span className="hidden sm:inline text-sm">{showSidebar ? 'Ẩn' : 'Danh sách'}</span>
              </button>
            </div>
          </div>

        {/* Progress Bar */}
        {progress && (
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">
                {progress.practiced_count}/{progress.total_in_lesson} câu
              </span>
              <span className="text-sm font-bold text-indigo-600">
                {progress.percentage}%
              </span>
            </div>
            <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-indigo-600 transition-all duration-500 ease-out rounded-full"
                style={{ width: `${progress.percentage}%` }}
              />
            </div>
          </div>
        )}

        {/* Sentence Card */}
        {isLoading ? (
          <div className="bg-white backdrop-blur-sm rounded-lg p-8 md:p-12 shadow-lg border border-indigo-100 animate-pulse">
            <div className="h-8 bg-gray-200 rounded-lg mb-6 w-3/4 mx-auto"></div>
            <div className="h-6 bg-gray-200 rounded-lg mb-4 w-1/2 mx-auto"></div>
            <div className="h-12 bg-gray-200 rounded-lg w-full"></div>
          </div>
        ) : sentence ? (
          <div className="bg-white backdrop-blur-sm rounded-lg p-8 md:p-12 shadow-lg border border-indigo-100 mb-6">
            {/* Vietnamese Text */}
            <div className="text-center mb-8">
              <div className="flex items-center justify-center gap-2 mb-4">
                <span className="text-2xl" role="img" aria-label="Vietnam flag">🇻🇳</span>
                <h2 className="text-3xl md:text-4xl font-bold text-gray-900">
                  {sentence.vi_text}
                </h2>
              </div>

              {/* Vietnamese Audio */}
              <button
                onClick={() => handlePlayAudio('vi')}
                className={`
                  inline-flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all duration-200 cursor-pointer shadow-md
                  ${playingAudio === 'vi'
                    ? 'bg-indigo-600 text-white'
                    : 'bg-indigo-100 text-indigo-700 hover:bg-indigo-200'
                  }
                `}
                
              >
                {playingAudio === 'vi' ? (
                  <>
                    <Pause size={20} className="animate-pulse" />
                    Đang phát...
                  </>
                ) : (
                  <>
                    <Play size={20} />
                    Nghe tiếng Việt
                  </>
                )}
              </button>
            </div>

            {/* Divider */}
            <div className="relative my-8">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t-2 border-gray-200"></div>
              </div>
              <div className="relative flex justify-center">
                <button
                  onClick={() => setShowAnswer(!showAnswer)}
                  className="px-4 py-2 bg-white text-gray-600 hover:text-gray-900 transition-colors duration-200 cursor-pointer flex items-center gap-2"
                  
                >
                  {showAnswer ? <EyeOff size={16} /> : <Eye size={16} />}
                  <span className="text-sm font-medium">
                    {showAnswer ? 'Ẩn đáp án' : 'Hiện đáp án'}
                  </span>
                </button>
              </div>
            </div>

            {/* English Text (Collapsible) */}
            <div
              className={`
                text-center transition-all duration-300 overflow-hidden
                ${showAnswer ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0'}
              `}
            >
              <div className="flex items-center justify-center gap-2 mb-4">
                <span className="text-2xl" role="img" aria-label="US flag">🇺🇸</span>
                <h3 className="text-2xl md:text-3xl font-bold text-gray-700">
                  {sentence.en_text}
                </h3>
              </div>

              {/* English Audio */}
              <button
                onClick={() => handlePlayAudio('en')}
                className={`
                  inline-flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all duration-200 cursor-pointer shadow-md
                  ${playingAudio === 'en'
                    ? 'bg-indigo-600 text-white'
                    : 'bg-indigo-100 text-indigo-700 hover:bg-indigo-200'
                  }
                `}
                
              >
                {playingAudio === 'en' ? (
                  <>
                    <Pause size={20} className="animate-pulse" />
                    Playing...
                  </>
                ) : (
                  <>
                    <Play size={20} />
                    Listen English
                  </>
                )}
              </button>
            </div>
          </div>
        ) : null}

        {/* Action Buttons */}
        {sentence && (
          <>
            {isReviewMode && (
              <div className="mb-3 p-3 bg-blue-50 rounded-lg text-center">
                <p className="text-sm text-blue-700">
                  ℹ️ <strong>Chế độ ôn tập:</strong> Tiến độ sẽ không được cập nhật
                </p>
              </div>
            )}
            <div className="grid grid-cols-2 gap-3 mb-4">
              <button
                onClick={recordPracticeAndNext}
                className="flex items-center justify-center gap-2 px-6 py-4 bg-green-600 hover:bg-green-700 text-white rounded-lg font-semibold shadow-md hover:shadow-lg transition-all duration-200 cursor-pointer"
              >
                <Check size={24} />
                <div className="text-left">
                  <div>{isReviewMode ? 'Tiếp theo' : 'Đã thuộc'}</div>
                  <div className="text-xs opacity-75">→ hoặc Y</div>
                </div>
              </button>

              <button
                onClick={skipSentence}
                className="flex items-center justify-center gap-2 px-6 py-4 bg-gray-200 hover:bg-gray-300 text-gray-900 rounded-lg font-semibold shadow-md hover:shadow-lg transition-all duration-200 cursor-pointer"
              >
                <SkipForward size={24} />
                <div className="text-left">
                  <div>Bỏ qua</div>
                  <div className="text-xs opacity-75">← hoặc S</div>
                </div>
              </button>
            </div>
          </>
        )}

        {/* Keyboard Shortcuts Hint */}
        <div className="text-center bg-indigo-50 rounded-lg p-3">
          <p className="text-xs text-gray-600 mb-2 font-semibold">
            ⚡ Phím tắt
          </p>
          <div className="flex flex-wrap justify-center gap-2 text-xs">
            <span className="inline-flex items-center gap-1 px-2 py-1 bg-white rounded">
              <kbd className="px-1.5 py-0.5 bg-gray-100 rounded font-mono">Space</kbd>
              <span className="text-gray-600">Nghe Vi</span>
            </span>
            <span className="inline-flex items-center gap-1 px-2 py-1 bg-white rounded">
              <kbd className="px-1.5 py-0.5 bg-gray-100 rounded font-mono">E</kbd>
              <span className="text-gray-600">Nghe En</span>
            </span>
            <span className="inline-flex items-center gap-1 px-2 py-1 bg-white rounded">
              <kbd className="px-1.5 py-0.5 bg-gray-100 rounded font-mono">Enter</kbd>
              <span className="text-gray-600">Đáp án</span>
            </span>
            <span className="inline-flex items-center gap-1 px-2 py-1 bg-white rounded">
              <kbd className="px-1.5 py-0.5 bg-gray-100 rounded font-mono">→</kbd>
              <span className="text-gray-600">Thuộc</span>
            </span>
            <span className="inline-flex items-center gap-1 px-2 py-1 bg-white rounded">
              <kbd className="px-1.5 py-0.5 bg-gray-100 rounded font-mono">←</kbd>
              <span className="text-gray-600">Bỏ qua</span>
            </span>
          </div>
        </div>
      </div>

      {/* Sidebar */}
      <div className={`
        fixed lg:static inset-y-0 right-0 w-80 bg-white 
        shadow-lg lg:shadow-lg rounded-l-3xl lg:rounded-lg 
        transition-transform duration-300 ease-in-out z-50
        ${showSidebar ? 'translate-x-0' : 'translate-x-full'}
      `}>
        {/* Sidebar Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <h3 className="text-lg font-bold text-gray-900">
            Danh sách câu ({practicedIds.size}/{allSentences.length})
          </h3>
          <button
            onClick={() => setShowSidebar(false)}
            className="lg:hidden p-2 text-gray-500 hover:text-gray-700 transition-colors cursor-pointer"
          >
            <X size={20} />
          </button>
        </div>

        {/* Sentence List */}
        <div className="overflow-y-auto h-[calc(100vh-80px)] p-4 space-y-2">
          {allSentences.length === 0 ? (
            <div className="text-center text-gray-500 py-8">
              <p>Đang tải...</p>
            </div>
          ) : (
            allSentences.map((item) => {
              const isPracticed = practicedIds.has(item.sentence_id);
              const isCurrent = sentence?.id === item.sentence_id;
              
              return (
                <button
                  key={item.sentence_id}
                  onClick={() => jumpToSentence(item.sentence_id)}
                  className={`
                    w-full p-3 rounded-lg transition-all duration-200 cursor-pointer
                    hover:scale-[1.02] active:scale-[0.98]
                    ${isCurrent 
                      ? 'bg-indigo-100 ring-2 ring-indigo-500' 
                      : isPracticed
                        ? 'bg-green-50 hover:bg-green-100'
                        : 'bg-gray-50 hover:bg-gray-100'
                    }
                  `}
                >
                  <div className="flex items-start gap-3">
                    {/* Status Icon */}
                    <div className="flex-shrink-0 mt-1">
                      {isPracticed ? (
                        <div className="w-6 h-6 rounded-full bg-green-500 flex items-center justify-center">
                          <Check size={14} className="text-white" />
                        </div>
                      ) : (
                        <div className="w-6 h-6 rounded-full border-2 border-gray-300"></div>
                      )}
                    </div>

                    {/* Sentence Content */}
                    <div className="flex-1 min-w-0">
                      <p 
                        className={`text-sm font-medium mb-1 ${
                          isCurrent 
                            ? 'text-indigo-900' 
                            : 'text-gray-900'
                        }`}
                      >
                        {item.vietnamese}
                      </p>
                      <p 
                        className={`text-xs ${
                          isCurrent 
                            ? 'text-indigo-600' 
                            : 'text-gray-600'
                        }`}
                      >
                        {item.english}
                      </p>
                    </div>
                  </div>
                </button>
              );
            })
          )}
        </div>
      </div>
      </div>

      {/* Mobile Overlay */}
      {showSidebar && (
        <div 
          className="lg:hidden fixed inset-0 bg-black/50 z-40"
          onClick={() => setShowSidebar(false)}
        />
      )}
    </div>
  );
}
