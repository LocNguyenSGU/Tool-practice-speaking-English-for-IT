import { useState, useEffect } from 'react';
import { X } from 'lucide-react';

export interface SentenceFormData {
  lesson_id: number;
  vi_text: string;
  en_text: string;
  order_index?: number;
}

export interface SentenceFormProps {
  isOpen: boolean;
  sentence?: SentenceFormData & { id?: number };
  lessons: Array<{ id: number; title: string }>;
  onClose: () => void;
  onSubmit: (data: SentenceFormData) => Promise<void>;
}

export default function SentenceForm({
  isOpen,
  sentence,
  lessons,
  onClose,
  onSubmit,
}: SentenceFormProps) {
  const [formData, setFormData] = useState<SentenceFormData>({
    lesson_id: 0,
    vi_text: '',
    en_text: '',
    order_index: undefined,
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (sentence) {
      setFormData({
        lesson_id: sentence.lesson_id,
        vi_text: sentence.vi_text,
        en_text: sentence.en_text,
        order_index: sentence.order_index,
      });
    } else {
      setFormData({
        lesson_id: lessons[0]?.id || 0,
        vi_text: '',
        en_text: '',
        order_index: undefined,
      });
    }
    setError(null);
  }, [sentence, isOpen, lessons]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!formData.lesson_id) {
      setError('Vui lòng chọn bài học');
      return;
    }

    if (!formData.vi_text.trim()) {
      setError('Câu tiếng Việt không được để trống');
      return;
    }

    if (!formData.en_text.trim()) {
      setError('Câu tiếng Anh không được để trống');
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit(formData);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Có lỗi xảy ra');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />

      {/* Modal */}
      <div className="relative bg-white rounded-lg shadow-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <h2 className="text-xl font-semibold text-gray-900">
            {sentence ? 'Chỉnh sửa Câu' : 'Tạo Câu mới'}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
            disabled={isSubmitting}
          >
            <X size={24} />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
              {error}
            </div>
          )}

          {/* Lesson Selection */}
          <div>
            <label htmlFor="lesson_id" className="block text-sm font-medium text-gray-700 mb-1">
              Bài học <span className="text-red-600">*</span>
            </label>
            <select
              id="lesson_id"
              value={formData.lesson_id}
              onChange={(e) => setFormData({ ...formData, lesson_id: parseInt(e.target.value) })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              required
              disabled={!!sentence}
            >
              <option value="">Chọn bài học</option>
              {lessons.map((lesson) => (
                <option key={lesson.id} value={lesson.id}>
                  {lesson.title}
                </option>
              ))}
            </select>
          </div>

          {/* Vietnamese Text */}
          <div>
            <label htmlFor="vi_text" className="block text-sm font-medium text-gray-700 mb-1">
              Tiếng Việt <span className="text-red-600">*</span>
            </label>
            <textarea
              id="vi_text"
              value={formData.vi_text}
              onChange={(e) => setFormData({ ...formData, vi_text: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
              placeholder="Nhập câu tiếng Việt"
              rows={3}
              maxLength={500}
              required
            />
          </div>

          {/* English Text */}
          <div>
            <label htmlFor="en_text" className="block text-sm font-medium text-gray-700 mb-1">
              English <span className="text-red-600">*</span>
            </label>
            <textarea
              id="en_text"
              value={formData.en_text}
              onChange={(e) => setFormData({ ...formData, en_text: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
              placeholder="Enter English sentence"
              rows={3}
              maxLength={500}
              required
            />
          </div>

          {/* Order Index */}
          <div>
            <label htmlFor="order_index" className="block text-sm font-medium text-gray-700 mb-1">
              Thứ tự
            </label>
            <input
              type="number"
              id="order_index"
              value={formData.order_index || ''}
              onChange={(e) =>
                setFormData({ ...formData, order_index: e.target.value ? parseInt(e.target.value) : undefined })
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="Để trống để tự động"
              min={1}
            />
            <p className="text-xs text-gray-500 mt-1">Để trống để tự động tăng thứ tự</p>
          </div>

          {/* Actions */}
          <div className="flex gap-3 justify-end pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors duration-200 disabled:opacity-50"
            >
              Hủy
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg transition-colors duration-200 disabled:opacity-50"
            >
              {isSubmitting ? 'Đang lưu...' : sentence ? 'Cập nhật' : 'Tạo mới'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
