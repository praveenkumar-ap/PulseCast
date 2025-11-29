import React from "react";
import { cn } from "@/lib/cn";

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "ghost";
  size?: "sm" | "md" | "lg";
  icon?: React.ReactNode;
};

export function Button({
  variant = "primary",
  size = "md",
  icon,
  className,
  children,
  ...props
}: ButtonProps) {
  const variantClasses: Record<ButtonProps["variant"], string> = {
    primary:
      "bg-primary text-heading shadow-card hover:bg-primary-strong focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-background",
    secondary:
      "bg-panel text-contrast border border-border hover:border-primary/70 hover:text-heading",
    ghost:
      "text-contrast hover:text-heading hover:bg-white/5 border border-transparent",
  };

  const sizeClasses: Record<ButtonProps["size"], string> = {
    sm: "text-sm px-3 py-1.5",
    md: "text-sm px-4 py-2",
    lg: "text-base px-5 py-2.5",
  };

  return (
    <button
      className={cn(
        "inline-flex items-center gap-2 rounded-full font-medium transition-all duration-150 ease-out",
        "focus:outline-none",
        variantClasses[variant],
        sizeClasses[size],
        className
      )}
      {...props}
    >
      {icon}
      {children}
    </button>
  );
}
