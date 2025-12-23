import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

type StatusType = "supplier" | "reseller" | "blacklist" | "pending" | "queued" | "running" | "succeeded" | "failed"

interface StatusBadgeProps {
  status: StatusType
  className?: string
}

const statusConfig: Record<StatusType, { label: string; className: string }> = {
  supplier: {
    label: "Supplier",
    className: "bg-[var(--status-supplier)] text-white hover:bg-[var(--status-supplier)]/90",
  },
  reseller: {
    label: "Reseller",
    className: "bg-[var(--status-reseller)] text-white hover:bg-[var(--status-reseller)]/90",
  },
  blacklist: {
    label: "Blacklist",
    className: "bg-[var(--status-blacklist)] text-white hover:bg-[var(--status-blacklist)]/90",
  },
  pending: {
    label: "Pending",
    className: "bg-[var(--status-pending)] text-white hover:bg-[var(--status-pending)]/90",
  },
  queued: {
    label: "Queued",
    className: "bg-muted text-muted-foreground hover:bg-muted/90",
  },
  running: {
    label: "Running",
    className: "bg-blue-500 text-white hover:bg-blue-500/90",
  },
  succeeded: {
    label: "Succeeded",
    className: "bg-[var(--status-supplier)] text-white hover:bg-[var(--status-supplier)]/90",
  },
  failed: {
    label: "Failed",
    className: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
  },
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const config = statusConfig[status]

  // Fallback if status is not recognized
  if (!config) {
    return (
      <Badge className={cn("bg-muted text-muted-foreground", className)}>
        {status || "Unknown"}
      </Badge>
    )
  }

  return <Badge className={cn(config.className, className)}>{config.label}</Badge>
}
