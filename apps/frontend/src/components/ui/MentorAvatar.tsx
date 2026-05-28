type MentorAvatarProps = {
  className?: string;
  label?: string;
};

export function MentorAvatar({ className = "h-7 w-7 text-xs", label = "RT" }: MentorAvatarProps) {
  return (
    <span
      className={`inline-flex shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-accent-mint to-accent font-semibold text-white ${className}`}
      aria-hidden
    >
      {label}
    </span>
  );
}
