import { useState, useEffect } from 'react';
import { Search, Plus, Pencil, Trash2 } from 'lucide-react';
import { api } from '../../utils/api';
import { useToast, ToastContainer } from '../../components/admin/Toast';
import LessonForm from '../../components/admin/LessonForm';
import type { LessonFormData } from '../../components/admin/LessonForm';
import ConfirmDialog from '../../components/admin/ConfirmDialog';
import Pagination from '../../components/admin/Pagination';

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

export default function AdminLessons() {
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [pagination, setPagination] = useState<PaginationInfo | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);

  // Form states
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingLesson, setEditingLesson] = useState<Lesson | null>(null);

  // Delete confirmation
  const [deleteLesson, setDeleteLesson] = useState<Lesson | null>(null);

  const { toasts, showToast, removeToast } = useToast();

  useEffect(() => {
    loadLessons();
  }, [currentPage, searchQuery]);

  const loadLessons = async () => {
    setIsLoading(true);
    try {
      const params = new URLSearchParams({
        page: currentPage.toString(),
        limit: '20',
        ...(searchQuery && { search: searchQuery }),
      });

      const response = await api.get(`/api/v1/lessons?${params}`);
      
      if (response.data) {
        setLessons(response.data.items || []);
        setPagination(response.data.pagination || null);
      }
    } catch (error) {
      showToast('error', 'Không thể tải danh sách bài học');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingLesson(null);
    setIsFormOpen(true);
  };

  const handleEdit = (lesson: Lesson) => {
    setEditingLesson(lesson);
    setIsFormOpen(true);
  };

  const handleDeleteClick = (lesson: Lesson) => {
    setDeleteLesson(lesson);
  };

  const handleSubmit = async (data: LessonFormData) => {
    try {
      if (editingLesson) {
        // Update
        const response = await api.put(`/api/v1/lessons/${editingLesson.id}`, data);
        if (response.error) {
          throw new Error(response.error);
        }
        showToast('success', 'Đã cập nhật bài học thành công!');
      } else {
        // Create
        const response = await api.post('/api/v1/lessons', data);
        if (response.error) {
          throw new Error(response.error);
        }
        showToast('success', 'Đã tạo bài học mới thành công!');
      }
      loadLessons();
    } catch (error) {
      throw error;
    }
  };

  const handleConfirmDelete = async () => {
    if (!deleteLesson) return;

    try {
      const response = await api.delete(`/api/v1/lessons/${deleteLesson.id}`);
      if (response.error) {
        throw new Error(response.error);
      }
      showToast('success', 'Đã xóa bài học thành công!');
      setDeleteLesson(null);
      loadLessons();
    } catch (error) {
      showToast('error', error instanceof Error ? error.message : 'Không thể xóa bài học');
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('vi-VN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    });
  };

  return (
    <div>
      <ToastContainer toasts={toasts} onRemove={removeToast} />

      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Quản lý Bài học</h1>
          <p className="text-gray-600 mt-2">Tạo, sửa, xóa bài học trong hệ thống</p>
        </div>
        <button
          onClick={handleCreate}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-medium transition-colors duration-200"
        >
          <Plus size={20} />
          Tạo Bài học
        </button>
      </div>

      {/* Search Bar */}
      <div className="mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setCurrentPage(1);
            }}
            placeholder="Tìm kiếm bài học..."
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          />
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
        ) : lessons.length === 0 ? (
          <div className="p-8 text-center">
            <p className="text-gray-600">Chưa có bài học nào. Tạo bài học đầu tiên!</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">ID</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Tiêu đề</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Mô tả</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Thứ tự</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Trạng thái</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Ngày tạo</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Hành động</th>
                </tr>
              </thead>
              <tbody>
                {lessons.map((lesson) => (
                  <tr key={lesson.id} className="border-b border-gray-200 hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3 text-sm text-gray-900">{lesson.id}</td>
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">{lesson.title}</td>
                    <td className="px-4 py-3 text-sm text-gray-600 max-w-xs truncate">
                      {lesson.description || '-'}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900">{lesson.order_index}</td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex px-2 py-1 text-xs font-medium rounded ${
                          lesson.is_active
                            ? 'bg-green-100 text-green-700'
                            : 'bg-gray-100 text-gray-700'
                        }`}
                      >
                        {lesson.is_active ? 'Hoạt động' : 'Không hoạt động'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">{formatDate(lesson.created_at)}</td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleEdit(lesson)}
                          className="p-1 text-indigo-600 hover:text-indigo-700 transition-colors"
                          title="Chỉnh sửa"
                        >
                          <Pencil size={18} />
                        </button>
                        <button
                          onClick={() => handleDeleteClick(lesson)}
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

      {/* Lesson Form Modal */}
      <LessonForm
        isOpen={isFormOpen}
        lesson={editingLesson || undefined}
        onClose={() => setIsFormOpen(false)}
        onSubmit={handleSubmit}
      />

      {/* Delete Confirmation */}
      <ConfirmDialog
        isOpen={!!deleteLesson}
        title="Xóa Bài học"
        message={`Xóa bài học "${deleteLesson?.title}" sẽ xóa tất cả câu liên quan. Bạn có chắc chắn?`}
        confirmLabel="Xóa"
        cancelLabel="Hủy"
        isDestructive
        onConfirm={handleConfirmDelete}
        onCancel={() => setDeleteLesson(null)}
      />
    </div>
  );
}
