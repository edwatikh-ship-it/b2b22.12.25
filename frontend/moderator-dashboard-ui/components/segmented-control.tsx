"use client"

import { cn } from "@/lib/utils"

interface Option {
  value: string
  label: string
}

interface SegmentedControlProps {
  value: string
  onValueChange: (value: string) => void
  options: Option[]
}

export function SegmentedControl({ value, onValueChange, options }: SegmentedControlProps) {
  return (
    <div className="inline-flex p-1 bg-muted/50 rounded-lg gap-1">
      {options.map((option) => (
        <button
          key={option.value}
          type="button"
          onClick={() => onValueChange(option.value)}
          className={cn(
            "px-4 py-2 text-sm font-medium rounded-md transition-all duration-200",
            value === option.value
              ? "bg-background text-foreground shadow-sm"
              : "text-muted-foreground hover:text-foreground",
          )}
        >
          {option.label}
        </button>
      ))}
    </div>
  )
}
