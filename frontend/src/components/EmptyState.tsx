interface Props { title: string; description?: string; }
export default function EmptyState({ title, description }: Props) {
  return (
    <div className="text-center py-16">
      <h3 className="text-lg font-medium">{title}</h3>
      {description && <p className="mt-2 text-muted-foreground">{description}</p>}
    </div>
  );
}
