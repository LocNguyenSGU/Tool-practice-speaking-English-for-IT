import { useState, useEffect } from 'react';
import { BookOpen, FileText, Users, TrendingUp } from 'lucide-react';
import StatsCard from '../../components/admin/StatsCard';
import { api } from '../../utils/api';

interface DashboardStats {
  totalLessons: number;
  totalSentences: number;
  activeUsers: number;
  avgProgress: number;
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats>({
    totalLessons: 0,
    totalSentences: 0,
    activeUsers: 0,
    avgProgress: 0,
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    setIsLoading(true);
    try {
      // Fetch lessons count
      const lessonsRes = await api.get('/api/v1/lessons?limit=1');
      const totalLessons = lessonsRes.data?.pagination?.total_items || 0;

      // Fetch sentences count
      const sentencesRes = await api.get('/api/v1/sentences?limit=1');
      const totalSentences = sentencesRes.data?.pagination?.total_items || 0;

      // Fetch users count
      const usersRes = await api.get('/api/v1/users?limit=1');
      const totalUsers = usersRes.data?.pagination?.total_items || 0;

      setStats({
        totalLessons,
        totalSentences,
        activeUsers: totalUsers, // Future: fetch from users endpoint
        avgProgress: 0, // Future: calculate from practice data
      });
    } catch (error) {
      console.error('Failed to load stats:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">Tổng quan hệ thống Vi-En Reflex Trainer</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatsCard
          title="Tổng số bài học"
          value={stats.totalLessons}
          icon={BookOpen}
          iconColor="text-indigo-600"
          iconBg="bg-indigo-100"
          isLoading={isLoading}
        />
        <StatsCard
          title="Tổng số câu"
          value={stats.totalSentences}
          icon={FileText}
          iconColor="text-green-600"
          iconBg="bg-green-100"
          isLoading={isLoading}
        />
        <StatsCard
          title="Người dùng hoạt động"
          value={stats.activeUsers || '-'}
          icon={Users}
          iconColor="text-blue-600"
          iconBg="bg-blue-100"
          isLoading={isLoading}
        />
        <StatsCard
          title="Tiến độ trung bình"
          value={stats.avgProgress ? `${stats.avgProgress}%` : '-'}
          icon={TrendingUp}
          iconColor="text-purple-600"
          iconBg="bg-purple-100"
          isLoading={isLoading}
        />
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Thao tác nhanh</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <a
            href="/admin/lessons"
            className="flex items-center gap-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors duration-200"
          >
            <div className="p-2 bg-indigo-100 rounded-lg">
              <BookOpen className="text-indigo-600" size={20} />
            </div>
            <div>
              <h3 className="font-medium text-gray-900">Quản lý Bài học</h3>
              <p className="text-sm text-gray-600">Tạo, sửa, xóa bài học</p>
            </div>
          </a>
          <a
            href="/admin/sentences"
            className="flex items-center gap-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors duration-200"
          >
            <div className="p-2 bg-green-100 rounded-lg">
              <FileText className="text-green-600" size={20} />
            </div>
            <div>
              <h3 className="font-medium text-gray-900">Quản lý Câu</h3>
              <p className="text-sm text-gray-600">Thêm câu, bulk upload</p>
            </div>
          </a>
        </div>
      </div>
    </div>
  );
}
