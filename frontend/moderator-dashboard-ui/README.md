# Moderator Dashboard UI

A comprehensive B2B admin dashboard for managing parsing operations, domains, suppliers, and blacklist.

## Features

- **Dashboard**: Quick access to all major functions
- **Manual Parsing**: Start parsing for specific keywords with customizable depth and source
- **Parsing Runs**: View history of all parsing operations with detailed results
- **Pending Domains**: Review and make decisions on domains awaiting action
- **Keywords Database**: Manage and search keyword database
- **Suppliers Management**: Manage suppliers and resellers with complete information
- **Blacklist**: Manage globally blacklisted domains
- **Dark/Light Mode**: Full theme support with system preference detection

## Tech Stack

- **Frontend**: Next.js 16 + React 19
- **Styling**: Tailwind CSS v4 with custom design tokens
- **UI Components**: shadcn/ui (Radix UI primitives)
- **TypeScript**: Full type safety
- **Backend**: FastAPI (runs on http://127.0.0.1:8001)

## Getting Started

### Prerequisites

- Node.js 18+ 
- Backend API running on http://127.0.0.1:8001

### Installation

1. Install dependencies:
   ```bash
   npm install
   ```

2. Configure environment variables:
   ```bash
   cp .env.example .env.local
   ```
   
   Edit `.env.local` and set:
   ```
   NEXT_PUBLIC_API_URL=http://127.0.0.1:8001
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

4. Open [http://localhost:3000](http://localhost:3000)

## Project Structure

```
├── app/
│   ├── dashboard/           # Main dashboard and layout
│   ├── manual-parsing/      # Manual parsing interface
│   ├── parsing-runs/        # Parsing history and details
│   ├── domains/queue/       # Pending domains queue
│   ├── keywords/            # Keywords database
│   ├── suppliers/           # Suppliers management
│   └── blacklist/           # Blacklist management
├── components/
│   ├── ui/                  # shadcn/ui components
│   ├── app-sidebar.tsx      # Main navigation sidebar
│   ├── theme-toggle.tsx     # Theme switcher
│   ├── status-badge.tsx     # Status indicators
│   └── domain-results-accordion.tsx  # Domain results display
├── lib/
│   ├── api.ts              # API client with error handling
│   ├── types.ts            # TypeScript interfaces matching API
│   └── utils.ts            # Utility functions
└── app/globals.css         # Theme tokens and styles
```

## API Integration

The dashboard connects to the FastAPI backend at `http://127.0.0.1:8001` with the following endpoints:

- `/moderator/parsing-runs` - Parsing history
- `/moderator/manual-parsing` - Start manual parsing
- `/moderator/pending-domains` - Domain queue
- `/moderator/domains/{domain}/decision` - Domain decisions
- `/moderator/keywords` - Keywords database
- `/moderator/suppliers` - Suppliers management
- `/moderator/blacklist/domains` - Blacklist management

See `lib/types.ts` for complete API contracts.

## Design System

The dashboard uses a minimalist B2B admin aesthetic with:

- **Neutral color palette** for readability
- **Status colors**: Green (supplier), Purple (reseller), Black (blacklist), Yellow (pending)
- **Responsive tables** and accordions for data display
- **Clear empty/error/loading states** throughout

## Development

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## Notes

- All dates are displayed in local timezone using date-fns
- Auto-polling is enabled for active parsing runs (every 3 seconds)
- Domain decisions include optional company data for supplier/reseller statuses
- Blacklist uses root domains (without scheme or path)
