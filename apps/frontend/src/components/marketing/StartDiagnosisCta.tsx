import Link from "next/link";

type StartDiagnosisCtaProps = {
  className?: string;
  testId: string;
};

export function StartDiagnosisCta({
  className = "",
  testId,
}: StartDiagnosisCtaProps) {
  return (
    <Link
      href="/"
      className={`welcome-cta inline-flex items-center justify-center rounded-md bg-accent px-5 py-2.5 text-sm font-medium text-white ${className}`}
      data-testid={testId}
    >
      Start diagnosis
    </Link>
  );
}
