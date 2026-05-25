type ForgeStepProps = { step: string; children: React.ReactNode };

export function ForgeStep({ step, children }: ForgeStepProps) {
  return (
    <li className="border-l-2 border-accent-mint pl-4">
      <span className="text-xs uppercase text-text-muted">{step}</span>
      <div className="mt-1 text-text-primary">{children}</div>
    </li>
  );
}
