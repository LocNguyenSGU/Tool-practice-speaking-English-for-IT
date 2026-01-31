import { useState } from 'react';
import { X, Upload, ChevronDown, ChevronUp } from 'lucide-react';

export interface BulkSentence {
  vi: string;
  en: string;
}

export interface BulkUploadModalProps {
  isOpen: boolean;
  lessons: Array<{ id: number; title: string }>;
  onClose: () => void;
  onSubmit: (lessonId: number, sentences: BulkSentence[]) => Promise<void>;
}

export default function BulkUploadModal({
  isOpen,
  lessons,
  onClose,
  onSubmit,
}: BulkUploadModalProps) {
  const [lessonId, setLessonId] = useState<number>(0);
  const [jsonInput, setJsonInput] = useState('');
  const [parsedSentences, setParsedSentences] = useState<BulkSentence[]>([]);
  const [showPreview, setShowPreview] = useState(false);
  const [showExample, setShowExample] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleParse = () => {
    setError(null);
    setParsedSentences([]);
    setShowPreview(false);

    if (!jsonInput.trim()) {
      setError('Vui lòng nhập dữ liệu JSON');
      return;
    }

    try {
      const parsed = JSON.parse(jsonInput);

      if (!Array.isArray(parsed)) {
        setError('Dữ liệu phải là một mảng JSON');
        return;
      }

      if (parsed.length === 0) {
        setError('Mảng không được rỗng');
        return;
      }

      // Validate each sentence
      const validated: BulkSentence[] = [];
      for (let i = 0; i < parsed.length; i++) {
        const item = parsed[i];
        if (!item.vi || !item.en) {
          setError(`Câu thứ ${i + 1}: Thiếu trường "vi" hoặc "en"`);
          return;
        }
        validated.push({ vi: item.vi.trim(), en: item.en.trim() });
      }

      setParsedSentences(validated);
      setShowPreview(true);
    } catch (err) {
      setError('JSON không hợp lệ: ' + (err instanceof Error ? err.message : 'Lỗi cú pháp'));
    }
  };

  const handleSubmit = async () => {
    setError(null);

    if (!lessonId) {
      setError('Vui lòng chọn bài học');
      return;
    }

    if (parsedSentences.length === 0) {
      setError('Vui lòng parse JSON trước khi submit');
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit(lessonId, parsedSentences);
      // Reset form
      setLessonId(0);
      setJsonInput('');
      setParsedSentences([]);
      setShowPreview(false);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Có lỗi xảy ra');
    } finally {
      setIsSubmitting(false);
    }
  };

  const exampleJson = `[
  {"vi": "Xin chào", "en": "Hello"},
  {"vi": "Tạm biệt", "en": "Goodbye"},
  {"vi": "Cảm ơn", "en": "Thank you"}
]`;

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />

      {/* Modal */}
      <div className="relative bg-white rounded-lg shadow-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Upload className="text-indigo-600" size={24} />
            <h2 className="text-xl font-semibold text-gray-900">Bulk Upload Câu</h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
            disabled={isSubmitting}
          >
            <X size={24} />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
              {error}
            </div>
          )}

          {/* Lesson Selection */}
          <div>
            <label htmlFor="bulk_lesson_id" className="block text-sm font-medium text-gray-700 mb-1">
              Chọn Bài học <span className="text-red-600">*</span>
            </label>
            <select
              id="bulk_lesson_id"
              value={lessonId}
              onChange={(e) => setLessonId(parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              required
            >
              <option value="">Chọn bài học</option>
              {lessons.map((lesson) => (
                <option key={lesson.id} value={lesson.id}>
                  {lesson.title}
                </option>
              ))}
            </select>
          </div>

          {/* JSON Input */}
          <div>
            <label htmlFor="json_input" className="block text-sm font-medium text-gray-700 mb-1">
              Nhập JSON Array
            </label>
            <textarea
              id="json_input"
              value={jsonInput}
              onChange={(e) => setJsonInput(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none font-mono text-sm"
              placeholder='[{"vi": "Xin chào", "en": "Hello"}]'
              rows={10}
            />
          </div>

          {/* Example Toggle */}
          <button
            type="button"
            onClick={() => setShowExample(!showExample)}
            className="flex items-center gap-2 text-sm text-indigo-600 hover:text-indigo-700"
          >
            {showExample ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
            {showExample ? 'Ẩn' : 'Xem'} ví dụ định dạng JSON
          </button>

          {showExample && (
            <div className="p-3 bg-gray-50 border border-gray-200 rounded-lg">
              <pre className="text-xs font-mono text-gray-700 whitespace-pre-wrap">{exampleJson}</pre>
            </div>
          )}

          {/* Parse Button */}
          <button
            type="button"
            onClick={handleParse}
            className="w-full px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg transition-colors duration-200"
          >
            Parse & Preview
          </button>

          {/* Preview Table */}
          {showPreview && parsedSentences.length > 0 && (
            <div className="border border-gray-200 rounded-lg overflow-hidden">
              <div className="bg-gray-50 px-4 py-2 border-b border-gray-200">
                <h3 className="text-sm font-medium text-gray-900">
                  Preview ({parsedSentences.length} câu)
                </h3>
              </div>
              <div className="max-h-64 overflow-y-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b border-gray-200 sticky top-0">
                    <tr>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-700">#</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-700">Tiếng Việt</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-700">English</th>
                    </tr>
                  </thead>
                  <tbody>
                    {parsedSentences.map((sentence, index) => (
                      <tr key={index} className="border-b border-gray-100 hover:bg-gray-50">
                        <td className="px-4 py-2 text-sm text-gray-600">{index + 1}</td>
                        <td className="px-4 py-2 text-sm text-gray-900">{sentence.vi}</td>
                        <td className="px-4 py-2 text-sm text-gray-900">{sentence.en}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

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
              type="button"
              onClick={handleSubmit}
              disabled={isSubmitting || !showPreview || parsedSentences.length === 0}
              className="px-4 py-2 text-sm font-medium text-white bg-green-600 hover:bg-green-700 rounded-lg transition-colors duration-200 disabled:opacity-50"
            >
              {isSubmitting ? 'Đang tạo...' : `Tạo ${parsedSentences.length} câu`}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
