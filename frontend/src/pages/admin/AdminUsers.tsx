import { useState, useEffect } from 'react';
import { Search, Plus, Pencil, Trash2, Shield, ShieldOff, UserX, UserCheck } from 'lucide-react';
import { api } from '../../utils/api';
import { useToast, ToastContainer } from '../../components/admin/Toast';
import UserForm from '../../components/admin/UserForm';
import type { UserFormData } from '../../components/admin/UserForm';
import ConfirmDialog from '../../components/admin/ConfirmDialog';
import Pagination from '../../components/admin/Pagination';

interface User {
  id: string;
  email: string;
  username: string;
  is_active: boolean;
  is_admin: boolean;
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

export default function AdminUsers() {
  const [users, setUsers] = useState<User[]>([]);
  const [pagination, setPagination] = useState<PaginationInfo | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [filterType, setFilterType] = useState<'all' | 'admin' | 'regular' | 'active' | 'inactive'>('all');

  // Form states
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);

  // Delete confirmation
  const [deleteUser, setDeleteUser] = useState<User | null>(null);

  const { toasts, showToast, removeToast } = useToast();

  useEffect(() => {
    loadUsers();
  }, [currentPage, searchQuery, filterType]);

  const loadUsers = async () => {
    setIsLoading(true);
    try {
      const params = new URLSearchParams({
        page: currentPage.toString(),
        limit: '20',
        ...(searchQuery && { search: searchQuery }),
      });

      // Note: This endpoint might need to be created in backend
      const response = await api.get(`/api/v1/users?${params}`);
      
      if (response.data) {
        let filteredUsers = response.data.items || [];
        
        // Apply client-side filters
        if (filterType === 'admin') {
          filteredUsers = filteredUsers.filter((u: User) => u.is_admin);
        } else if (filterType === 'regular') {
          filteredUsers = filteredUsers.filter((u: User) => !u.is_admin);
        } else if (filterType === 'active') {
          filteredUsers = filteredUsers.filter((u: User) => u.is_active);
        } else if (filterType === 'inactive') {
          filteredUsers = filteredUsers.filter((u: User) => !u.is_active);
        }
        
        setUsers(filteredUsers);
        setPagination(response.data.pagination || null);
      }
    } catch (error) {
      showToast('error', 'Không thể tải danh sách người dùng');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingUser(null);
    setIsFormOpen(true);
  };

  const handleEdit = (user: User) => {
    setEditingUser(user);
    setIsFormOpen(true);
  };

  const handleDeleteClick = (user: User) => {
    setDeleteUser(user);
  };

  const handleSubmit = async (data: UserFormData) => {
    try {
      if (editingUser) {
        // Update
        const updateData: any = {
          is_active: data.is_active,
          is_admin: data.is_admin,
        };
        
        // Only include password if it's provided
        if (data.password) {
          updateData.password = data.password;
        }
        
        const response = await api.put(`/api/v1/users/${editingUser.id}`, updateData);
        if (response.error) {
          throw new Error(response.error);
        }
        showToast('success', 'Đã cập nhật người dùng thành công!');
      } else {
        // Create
        const response = await api.post('/api/v1/users', data);
        if (response.error) {
          throw new Error(response.error);
        }
        showToast('success', 'Đã tạo người dùng mới thành công!');
      }
      loadUsers();
    } catch (error) {
      throw error;
    }
  };

  const handleConfirmDelete = async () => {
    if (!deleteUser) return;

    try {
      const response = await api.delete(`/api/v1/users/${deleteUser.id}`);
      if (response.error) {
        throw new Error(response.error);
      }
      showToast('success', 'Đã xóa người dùng thành công!');
      setDeleteUser(null);
      loadUsers();
    } catch (error) {
      showToast('error', error instanceof Error ? error.message : 'Không thể xóa người dùng');
    }
  };

  const toggleUserStatus = async (user: User) => {
    try {
      const response = await api.put(`/api/v1/users/${user.id}`, {
        is_active: !user.is_active,
      });
      if (response.error) {
        throw new Error(response.error);
      }
      showToast('success', `Đã ${!user.is_active ? 'kích hoạt' : 'vô hiệu hóa'} tài khoản!`);
      loadUsers();
    } catch (error) {
      showToast('error', 'Không thể thay đổi trạng thái người dùng');
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('vi-VN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div>
      <ToastContainer toasts={toasts} onRemove={removeToast} />

      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Quản lý Người dùng</h1>
          <p className="text-gray-600 mt-2">Quản lý tài khoản và quyền người dùng</p>
        </div>
        <button
          onClick={handleCreate}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-medium transition-colors duration-200"
        >
          <Plus size={20} />
          Tạo Người dùng
        </button>
      </div>

      {/* Filters */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        {/* Filter Type */}
        <div>
          <label htmlFor="filter_type" className="block text-sm font-medium text-gray-700 mb-1">
            Lọc theo
          </label>
          <select
            id="filter_type"
            value={filterType}
            onChange={(e) => {
              setFilterType(e.target.value as typeof filterType);
              setCurrentPage(1);
            }}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          >
            <option value="all">Tất cả người dùng</option>
            <option value="admin">Chỉ Admin</option>
            <option value="regular">Người dùng thường</option>
            <option value="active">Đang hoạt động</option>
            <option value="inactive">Đã vô hiệu hóa</option>
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
              placeholder="Tìm email hoặc username..."
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
        ) : users.length === 0 ? (
          <div className="p-8 text-center">
            <p className="text-gray-600">Không tìm thấy người dùng nào</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Email</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Username</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Quyền</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Trạng thái</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Ngày tạo</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Hành động</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.id} className="border-b border-gray-200 hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3 text-sm text-gray-900">{user.email}</td>
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">{user.username}</td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex items-center gap-1 px-2 py-1 text-xs font-medium rounded ${
                          user.is_admin
                            ? 'bg-purple-100 text-purple-700'
                            : 'bg-gray-100 text-gray-700'
                        }`}
                      >
                        {user.is_admin ? (
                          <>
                            <Shield size={14} />
                            Admin
                          </>
                        ) : (
                          <>
                            <ShieldOff size={14} />
                            User
                          </>
                        )}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex items-center gap-1 px-2 py-1 text-xs font-medium rounded ${
                          user.is_active
                            ? 'bg-green-100 text-green-700'
                            : 'bg-red-100 text-red-700'
                        }`}
                      >
                        {user.is_active ? (
                          <>
                            <UserCheck size={14} />
                            Hoạt động
                          </>
                        ) : (
                          <>
                            <UserX size={14} />
                            Vô hiệu
                          </>
                        )}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">{formatDate(user.created_at)}</td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => toggleUserStatus(user)}
                          className={`p-1 transition-colors ${
                            user.is_active
                              ? 'text-red-600 hover:text-red-700'
                              : 'text-green-600 hover:text-green-700'
                          }`}
                          title={user.is_active ? 'Vô hiệu hóa' : 'Kích hoạt'}
                        >
                          {user.is_active ? <UserX size={18} /> : <UserCheck size={18} />}
                        </button>
                        <button
                          onClick={() => handleEdit(user)}
                          className="p-1 text-indigo-600 hover:text-indigo-700 transition-colors"
                          title="Chỉnh sửa"
                        >
                          <Pencil size={18} />
                        </button>
                        <button
                          onClick={() => handleDeleteClick(user)}
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

      {/* User Form Modal */}
      <UserForm
        isOpen={isFormOpen}
        user={editingUser || undefined}
        onClose={() => setIsFormOpen(false)}
        onSubmit={handleSubmit}
        isEditing={!!editingUser}
      />

      {/* Delete Confirmation */}
      <ConfirmDialog
        isOpen={!!deleteUser}
        title="Xóa Người dùng"
        message={`Bạn có chắc chắn muốn xóa người dùng "${deleteUser?.username}"? Hành động này không thể hoàn tác.`}
        confirmLabel="Xóa"
        cancelLabel="Hủy"
        isDestructive
        onConfirm={handleConfirmDelete}
        onCancel={() => setDeleteUser(null)}
      />
    </div>
  );
}
