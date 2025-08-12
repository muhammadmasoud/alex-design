import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Project } from "@/types";

interface Props {
  project: Project;
}

export default function ProjectCard({ project }: Props) {
  return (
    <Card className="overflow-hidden hover-scale">
      <CardHeader className="p-0">
        <img
          src={project.image || '/placeholder.svg'}
          alt={`${project.title} architecture project`}
          loading="lazy"
          className="h-48 w-full object-cover"
          onError={(e) => {
            const target = e.target as HTMLImageElement;
            target.src = '/placeholder.svg';
          }}
        />
      </CardHeader>
      <CardContent className="p-4">
        <h3 className="font-medium">{project.title}</h3>
        <p className="mt-1 line-clamp-3 text-sm text-muted-foreground">{project.description}</p>
      </CardContent>
    </Card>
  );
}
