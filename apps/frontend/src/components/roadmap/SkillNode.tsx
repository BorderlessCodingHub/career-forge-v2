type SkillNodeProps = { title: string; status?: string };

export function SkillNode({ title, status = "recomendado" }: SkillNodeProps) {
  return (
    <div className="rounded-node bg-surface-node px-4 py-3 text-sm text-text-primary">
      <span>{title}</span>
      <span className="ml-2 text-xs text-text-muted">{status}</span>
    </div>
  );
}
