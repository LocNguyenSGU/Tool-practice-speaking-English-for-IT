import { type LucideProps } from 'lucide-react';

export interface StatsCardProps {
  title: string;
  value: string | number;
  icon: React.ComponentType<LucideProps>;
  iconColor?: string;
  iconBg?: string;
  isLoading?: boolean;
}

export default function StatsCard({
  title,
  value,
  icon: Icon,
  iconColor = 'text-indigo-600',
  iconBg = 'bg-indigo-100',
  isLoading = false,
}: StatsCardProps) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-lg p-6 border border-gray-200 shadow-sm animate-pulse">
        <div className="flex items-center justify-between mb-4">
          <div className={`p-2 ${iconBg} rounded-lg`}>
            <div className="w-6 h-6 bg-gray-300 rounded"></div>
          </div>
        </div>
        <div className="h-9 bg-gray-300 rounded mb-2 w-20"></div>
        <div className="h-4 bg-gray-200 rounded w-32"></div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg p-6 border border-gray-200 shadow-sm hover:shadow-md transition-shadow duration-200">
      <div className="flex items-center justify-between mb-4">
        <div className={`p-2 ${iconBg} rounded-lg`}>
          <Icon className={iconColor} size={24} />
        </div>
      </div>
      <h3 className="text-3xl font-bold text-gray-900 mb-2">{value}</h3>
      <p className="text-sm text-gray-600">{title}</p>
    </div>
  );
}
