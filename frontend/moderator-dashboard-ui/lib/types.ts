// TypeScript types matching the API contracts

export interface ParsingRunDTO {
  runId: string
  requestId?: number
  status: "queued" | "running" | "succeeded" | "failed"
  createdAt?: string
  finishedAt?: string
  depth?: number
  source?: "google" | "yandex" | "both"
  totalKeys?: number
  errorMessage?: string
}

export interface ParsingRunsListResponseDTO {
  items: ParsingRunDTO[]
  limit: number
  offset: number
  total: number
}

export interface ParsingDomainGroupDTO {
  domain: string
  urls: string[]
  source: "google" | "yandex" | "both"
  title?: string
  status?: "supplier" | "reseller" | "blacklist" | null
}

export interface ParsingResultsByKeyDTO {
  keyId: number
  keyword?: string
  groups: ParsingDomainGroupDTO[]
}

export interface ParsingResultsResponseDTO {
  requestId: number
  runId: string
  results: ParsingResultsByKeyDTO[]
}

export interface ParsingRunEventDTO {
  timestamp: string
  level: "info" | "warn" | "error"
  message: string
  context?: Record<string, unknown> | null
}

export interface ParsingRunLogResponseDTO {
  runId: string
  events: ParsingRunEventDTO[]
}

export interface StartParsingResponseDTO {
  requestId: number
  runId: string
  status: "queued" | "running" | "succeeded" | "failed"
}

export interface DomainDecisionRequestDTO {
  status: "supplier" | "reseller" | "blacklist" | "pending"
  carddata?: {
    inn?: string
    name?: string
    email?: string
    phone?: string
    website?: string
  }
  comment?: string
}

export interface KeywordDTO {
  keyId: number
  requestId: number
  keyword: string
  status: "pending" | "parsed" | "failed"
  lastRunId?: string | null
  lastRunStatus?: "queued" | "running" | "succeeded" | "failed" | null
  lastRunAt?: string | null
  domainsFound: number
}

export interface KeywordsListResponseDTO {
  items: KeywordDTO[]
  limit: number
  offset: number
  total: number
}

export interface SupplierDTO {
  id: number
  type: "supplier" | "reseller"
  inn?: string
  name: string
  domain?: string
  email?: string
  phone?: string
  website?: string
  createdAt?: string
}

export interface SuppliersListResponseDTO {
  items: SupplierDTO[]
  limit: number
  offset: number
  total: number
}

export interface PendingDomainUrlDTO {
  url: string
  hitcount: number
  keys: string[]
}

export interface PendingDomainDTO {
  domain: string
  totalhits: number
  urlcount: number
  firstseenat: string
  lasthitat: string
  urls: PendingDomainUrlDTO[]
}

export interface PendingDomainDetailDTO {
  domain: string
  totalhits: number
  urlcount: number
  firstseenat: string
  lasthitat: string
  urls: PendingDomainUrlDTO[]
}

export interface PendingDomainListResponseDTO {
  items: PendingDomainDTO[]
  limit: number
  offset: number
  total: number
}

export interface ModeratorBlacklistUrlItemDTO {
  url: string
  comment?: string | null
  createdat: string
}

export interface ModeratorBlacklistDomainDTO {
  domain: string
  createdat: string
  comment?: string | null
  urls: ModeratorBlacklistUrlItemDTO[]
}

export interface ModeratorBlacklistDomainListResponseDTO {
  items: ModeratorBlacklistDomainDTO[]
  limit: number
  offset: number
  total: number
}
