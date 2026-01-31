import { useState, useEffect, useRef } from 'react';
import { Search, Plus, Pencil, Trash2, Upload, Play, Pause } from 'lucide-react';
import { api } from '../../utils/api';
import { useToast, ToastContainer } from '../../components/admin/Toast';
import SentenceForm from '../../components/admin/SentenceForm';
import type { SentenceFormData } from '../../components/admin/SentenceForm';
import BulkUploadModal from '../../components/admin/BulkUploadModal';
import type { BulkSentence } from '../../components/admin/BulkUploadModal';
import ConfirmDialog from '../../components/admin/ConfirmDialog';
import Pagination from '../../components/admin/Pagination';

interface Sentence {
  id: number;
  lesson_id: number;
  vi_text: string;
  en_text: string;
  order_index: number;
  created_at: string;
  updated_at: string;
}

interface Lesson {
  id: number;
  title: string;
}

interface PaginationInfo {
  page: number;
  limit: number;
  total_items: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export default function AdminSentences() {
  const [sentences, setSentences] = useState<Sentence[]>([]);
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [pagination, setPagination] = useState<PaginationInfo | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedLessonId, setSelectedLessonId] = useState<number | null>(null);

  // Audio playback state
  const [playingAudio, setPlayingAudio] = useState<{ id: number; lang: 'vi' | 'en' } | null>(null);
  const audioRef = useRef<HTMLAudioElement>(null);

  // Form states
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingSentence, setEditingSentence] = useState<Sentence | null>(null);

  // Bulk upload
  const [isBulkModalOpen, setIsBulkModalOpen] = useState(false);

  // Delete confirmation
  const [deleteSentence, setDeleteSentence] = useState<Sentence | null>(null);

  const { toasts, showToast, removeToast } = useToast();

  useEffect(() => {
    loadLessons();
  }, []);

  useEffect(() => {
    loadSentences();
  }, [currentPage, searchQuery, selectedLessonId]);

  const loadLessons = async () => {
    try {
      const response = await api.get('/api/v1/lessons?limit=1000');
      if (response.data) {
        setLessons(response.data.items || []);
      }
    } catch (error) {
      showToast('error', 'Không thể tải danh sách bài học');
    }
  };

  const loadSentences = async () => {
    setIsLoading(true);
    try {
      const params = new URLSearchParams({
        page: currentPage.toString(),
        limit: '20',
        ...(searchQuery && { search: searchQuery }),
        ...(selectedLessonId && { lesson_id: selectedLessonId.toString() }),
      });

      const response = await api.get(`/api/v1/sentences?${params}`);
      
      if (response.data) {
        setSentences(response.data.items || []);
        setPagination(response.data.pagination || null);
      }
    } catch (error) {
      showToast('error', 'Không thể tải danh sách câu');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingSentence(null);
    setIsFormOpen(true);
  };

  const handleEdit = (sentence: Sentence) => {
    setEditingSentence(sentence);
    setIsFormOpen(true);
  };

  const handleDeleteClick = (sentence: Sentence) => {
    setDeleteSentence(sentence);
  };

  const handleSubmit = async (data: SentenceFormData) => {
    try {
      if (editingSentence) {
        // Update
        const response = await api.put(`/api/v1/sentences/${editingSentence.id}`, data);
        if (response.error) {
          throw new Error(response.error);
        }
        showToast('success', 'Đã cập nhật câu thành công!');
      } else {
        // Create
        const response = await api.post('/api/v1/sentences', data);
        if (response.error) {
          throw new Error(response.error);
        }
        showToast('success', 'Đã tạo câu mới thành công!');
      }
      loadSentences();
    } catch (error) {
      throw error;
    }
  };

  const handleBulkUpload = async (lessonId: number, bulkSentences: BulkSentence[]) => {
    try {
      const response = await api.post('/api/v1/sentences/bulk', {
        lesson_id: lessonId,
        sentences: bulkSentences,
      });

      if (response.error) {
        throw new Error(response.error);
      }

      showToast('success', `Đã tạo ${bulkSentences.length} câu thành công!`);
      loadSentences();
    } catch (error) {
      throw error;
    }
  };

  const handleConfirmDelete = async () => {
    if (!deleteSentence) return;

    try {
      const response = await api.delete(`/api/v1/sentences/${deleteSentence.id}`);
      if (response.error) {
        throw new Error(response.error);
      }
      showToast('success', 'Đã xóa câu thành công!');
      setDeleteSentence(null);
      loadSentences();
    } catch (error) {
      showToast('error', error instanceof Error ? error.message : 'Không thể xóa câu');
    }
  };

  const getLessonTitle = (lessonId: number) => {
    const lesson = lessons.find((l) => l.id === lessonId);
    return lesson?.title || `Lesson ${lessonId}`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('vi-VN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    });
  };

  // Audio playback functions
  const handlePlayAudio = (sentenceId: number, lang: 'vi' | 'en') => {
    if (playingAudio?.id === sentenceId && playingAudio?.lang === lang) {
      // Stop if already playing this audio
      audioRef.current?.pause();
      setPlayingAudio(null);
    } else {
      // Play new audio
      const audioUrl = `http://localhost:8000/api/v1/audio/${sentenceId}/${lang}`;
      if (audioRef.current) {
        audioRef.current.src = audioUrl;
        audioRef.current.play().catch((error) => {
          console.error('Audio playback failed:', error);
          showToast('error', 'Không thể phát audio');
        });
        setPlayingAudio({ id: sentenceId, lang });
      }
    }
  };

  const handleAudioEnded = () => {
    setPlayingAudio(null);
  };

  return (
    <div>
      <ToastContainer toasts={toasts} onRemove={removeToast} />
      
      {/* Hidden Audio Element */}
      <audio ref={audioRef} onEnded={handleAudioEnded} className="hidden" />

      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Quản lý Câu</h1>
          <p className="text-gray-600 mt-2">Tạo, sửa, xóa câu trong các bài học</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setIsBulkModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition-colors duration-200"
          >
            <Upload size={20} />
            Bulk Upload
          </button>
          <button
            onClick={handleCreate}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-medium transition-colors duration-200"
          >
            <Plus size={20} />
            Tạo Câu
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        {/* Lesson Filter */}
        <div>
          <label htmlFor="lesson_filter" className="block text-sm font-medium text-gray-700 mb-1">
            Lọc theo Bài học
          </label>
          <select
            id="lesson_filter"
            value={selectedLessonId || ''}
            onChange={(e) => {
              setSelectedLessonId(e.target.value ? parseInt(e.target.value) : null);
              setCurrentPage(1);
            }}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          >
            <option value="">Tất cả bài học</option>
            {lessons.map((lesson) => (
              <option key={lesson.id} value={lesson.id}>
                {lesson.title}
              </option>
            ))}
          </select>
        </div>

        {/* Search */}
        <div>
          <label htmlFor="search" className="block text-sm font-medium text-gray-700 mb-1">
            Tìm kiếm
          </label>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              id="search"
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setCurrentPage(1);
              }}
              placeholder="Tìm kiếm câu..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center">
            <div className="animate-pulse space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-16 bg-gray-200 rounded"></div>
              ))}
            </div>
          </div>
        ) : sentences.length === 0 ? (
          <div className="p-8 text-center">
            <p className="text-gray-600">
              {selectedLessonId
                ? 'Bài học chưa có câu nào'
                : 'Chưa có câu nào. Tạo câu đầu tiên hoặc sử dụng Bulk Upload!'}
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">ID</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Bài học</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Tiếng Việt</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">English</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Audio</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Thứ tự</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Ngày tạo</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Hành động</th>
                </tr>
              </thead>
              <tbody>
                {sentences.map((sentence) => (
                  <tr key={sentence.id} className="border-b border-gray-200 hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3 text-sm text-gray-900">{sentence.id}</td>
                    <td className="px-4 py-3 text-sm text-gray-600 max-w-[150px] truncate">
                      {getLessonTitle(sentence.lesson_id)}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900 max-w-[250px]">
                      <div className="truncate" title={sentence.vi_text}>
                        {sentence.vi_text}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900 max-w-[250px]">
                      <div className="truncate" title={sentence.en_text}>
                        {sentence.en_text}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-1">
                        <button
                          onClick={() => handlePlayAudio(sentence.id, 'vi')}
                          className={`p-1.5 rounded transition-colors ${
                            playingAudio?.id === sentence.id && playingAudio?.lang === 'vi'
                              ? 'bg-indigo-100 text-indigo-700'
                              : 'text-gray-600 hover:bg-gray-100 hover:text-indigo-600'
                          }`}
                          title="Nghe tiếng Việt"
                        >
                          {playingAudio?.id === sentence.id && playingAudio?.lang === 'vi' ? (
                            <Pause size={16} />
                          ) : (
                            <Play size={16} />
                          )}
                        </button>
                        <span className="text-xs text-gray-400">🇻🇳</span>
                        
                        <span className="mx-1 text-gray-300">|</span>
                        
                        <button
                          onClick={() => handlePlayAudio(sentence.id, 'en')}
                          className={`p-1.5 rounded transition-colors ${
                            playingAudio?.id === sentence.id && playingAudio?.lang === 'en'
                              ? 'bg-indigo-100 text-indigo-700'
                              : 'text-gray-600 hover:bg-gray-100 hover:text-indigo-600'
                          }`}
                          title="Nghe tiếng Anh"
                        >
                          {playingAudio?.id === sentence.id && playingAudio?.lang === 'en' ? (
                            <Pause size={16} />
                          ) : (
                            <Play size={16} />
                          )}
                        </button>
                        <span className="text-xs text-gray-400">🇺🇸</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900">{sentence.order_index}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">{formatDate(sentence.created_at)}</td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleEdit(sentence)}
                          className="p-1 text-indigo-600 hover:text-indigo-700 transition-colors"
                          title="Chỉnh sửa"
                        >
                          <Pencil size={18} />
                        </button>
                        <button
                          onClick={() => handleDeleteClick(sentence)}
                          className="p-1 text-red-600 hover:text-red-700 transition-colors"
                          title="Xóa"
                        >
                          <Trash2 size={18} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Pagination */}
      {pagination && pagination.total_pages > 1 && (
        <Pagination
          currentPage={pagination.page}
          totalPages={pagination.total_pages}
          totalItems={pagination.total_items}
          itemsPerPage={pagination.limit}
          onPageChange={setCurrentPage}
          showItemCount={true}
          showPageNumbers={true}
        />
      )}

      {/* Sentence Form Modal */}
      <SentenceForm
        isOpen={isFormOpen}
        sentence={editingSentence || undefined}
        lessons={lessons}
        onClose={() => setIsFormOpen(false)}
        onSubmit={handleSubmit}
      />

      {/* Bulk Upload Modal */}
      <BulkUploadModal
        isOpen={isBulkModalOpen}
        lessons={lessons}
        onClose={() => setIsBulkModalOpen(false)}
        onSubmit={handleBulkUpload}
      />

      {/* Delete Confirmation */}
      <ConfirmDialog
        isOpen={!!deleteSentence}
        title="Xóa Câu"
        message={`Bạn có chắc chắn muốn xóa câu "${deleteSentence?.vi_text}"?`}
        confirmLabel="Xóa"
        cancelLabel="Hủy"
        isDestructive
        onConfirm={handleConfirmDelete}
        onCancel={() => setDeleteSentence(null)}
      />
    </div>
  );
}
