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
          <div className="text-2xl font-bold">{statistics.storage.media_size_mb} MB</div>
          <p className="text-xs text-muted-foreground">
            {statistics.storage.media_file_count} files stored
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Disk Space</CardTitle>
          <BarChart3 className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-green-600">{statistics.storage.disk_free_gb} GB</div>
          <p className="text-xs text-muted-foreground">
            Free of {statistics.storage.disk_total_gb} GB total
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
