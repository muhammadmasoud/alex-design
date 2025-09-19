import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Project } from "@/types";
import { useNavigate } from "react-router-dom";
import { Calendar, Tag, Eye } from "lucide-react";
import { motion } from "framer-motion";
import ProgressiveImage from "./ProgressiveImage";


interface Props {
  project: Project;
}

export default function ProjectCard({ project }: Props) {
  const navigate = useNavigate();

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
    });
  };

  const handleClick = () => {
    navigate(`/projects/${project.id}`);
  };

  return (
    <motion.div
      whileHover={{ y: -8, scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      transition={{ duration: 0.2 }}
    >
      <Card 
        className="overflow-hidden cursor-pointer group shadow-lg hover:shadow-xl transition-all duration-300 border-0 bg-card/50 backdrop-blur-sm"
        onClick={handleClick}
      >
        <CardHeader className="p-0 relative">
          <div className="relative overflow-hidden h-48">
            <ProgressiveImage
              src={project.original_image_url || project.image || '/placeholder.svg'}
              optimizedSrc={project.image}
              alt={`${project.title} architecture project`}
              className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110"
              loading="lazy"
              showQualityIndicator={false}
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
            <div className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
              <div className="bg-white/90 dark:bg-black/90 rounded-full p-2 backdrop-blur-sm">
                <Eye className="h-4 w-4 text-gray-700 dark:text-gray-300" />
              </div>
            </div>
          </div>
          {project.category_name && (
            <div className="absolute top-3 left-3">
              <Badge variant="secondary" className="bg-white/90 dark:bg-black/90 text-gray-700 dark:text-gray-300 backdrop-blur-sm">
                <Tag className="h-3 w-3 mr-1" />
                {project.category_name}
              </Badge>
            </div>
          )}
        </CardHeader>
        <CardContent className="p-3 sm:p-4">
          <div className="space-y-2">
            <h3 className="font-semibold text-base sm:text-lg leading-tight group-hover:text-primary transition-colors duration-200">
              {project.title}
            </h3>
            <p className="line-clamp-2 text-xs sm:text-sm text-muted-foreground leading-relaxed">
              {project.description}
            </p>
            <div className="flex items-center justify-between pt-2">
              <div className="flex items-center gap-1 text-xs text-muted-foreground">
                <Calendar className="h-3 w-3" />
                <span className="text-xs">{formatDate(project.project_date)}</span>
              </div>
              <div className="text-xs text-primary font-medium group-hover:underline">
                View Details →
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
