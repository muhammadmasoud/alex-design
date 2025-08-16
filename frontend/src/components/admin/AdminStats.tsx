import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart3, ImageIcon, FileText, HardDrive } from "lucide-react";

interface AdminStatsProps {
  statistics: {
    projects_count: number;
    services_count: number;
    storage: {
      media_size_mb: number;
      media_file_count: number;
      disk_total_gb: number;
      disk_free_gb: number;
      disk_used_gb: number;
      disk_usage_percent: number;
    };
  };
}

export default function AdminStats({ statistics }: AdminStatsProps) {
  const getStorageColor = (usagePercent: number) => {
    if (usagePercent > 90) return 'text-red-600';
    if (usagePercent > 80) return 'text-yellow-600';
    return 'text-green-600';
  };

  const formatSize = (sizeInMB: number) => {
    if (sizeInMB > 1024) {
      return `${(sizeInMB / 1024).toFixed(2)} GB`;
    }
    return `${sizeInMB.toFixed(2)} MB`;
  };

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total Projects</CardTitle>
          <ImageIcon className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{statistics.projects_count}</div>
          <p className="text-xs text-muted-foreground">
            Active portfolio projects
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total Services</CardTitle>
          <FileText className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{statistics.services_count}</div>
          <p className="text-xs text-muted-foreground">
            Available services
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Media Storage</CardTitle>
          <HardDrive className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{formatSize(statistics.storage.media_size_mb)}</div>
          <p className="text-xs text-muted-foreground">
            {statistics.storage.media_file_count} files stored
          </p>
          <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
              style={{ width: `${Math.min((statistics.storage.media_size_mb / 1024) / statistics.storage.disk_total_gb * 100, 100)}%` }}
            ></div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Disk Space</CardTitle>
          <BarChart3 className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className={`text-2xl font-bold ${getStorageColor(statistics.storage.disk_usage_percent)}`}>
            {statistics.storage.disk_free_gb.toFixed(1)} GB
          </div>
          <p className="text-xs text-muted-foreground">
            Free of {statistics.storage.disk_total_gb.toFixed(1)} GB total ({statistics.storage.disk_usage_percent}% used)
          </p>
          <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
            <div 
              className={`h-2 rounded-full transition-all duration-300 ${
                statistics.storage.disk_usage_percent > 90 ? 'bg-red-500' :
                statistics.storage.disk_usage_percent > 80 ? 'bg-yellow-500' : 'bg-green-500'
              }`}
              style={{ width: `${statistics.storage.disk_usage_percent}%` }}
            ></div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
