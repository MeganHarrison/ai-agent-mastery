
# AI Agent Mastery - Next.js Frontend

This is the Next.js frontend application for the AI Agent Mastery course.

## Features

- **Documents Page**: View and manage meeting documents and transcripts
  - Table view with sorting and filtering
  - Inline editing capabilities
  - Split-screen detail view
  - Automatic filtering of SOPs and documents
  - Integration with Fireflies for meeting recordings

## Getting Started

### Prerequisites

- Node.js 18+ installed
- Supabase account with database setup

### Installation

1. Install dependencies:
```bash
npm install
```

2. Set up environment variables:
```bash
cp .env.example .env
```

Edit `.env` with your Supabase credentials:
- `NEXT_PUBLIC_SUPABASE_URL`: Your Supabase project URL
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`: Your Supabase anon key

3. Run the development server:
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the application.

## Database Setup

Ensure your Supabase database has the `document_metadata` table with the following columns:
- id (uuid, primary key)
- title (text)
- type (text)
- project (text)
- date (text)
- summary (text)
- fireflies_link (text)
- speakers (text[])
- transcript (text)
- created_at (timestamp)
- updated_at (timestamp)

## Available Scripts

- `npm run dev` - Run development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## Tech Stack

- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Supabase** - Database and real-time subscriptions
- **Radix UI** - Headless UI components
- **Lucide Icons** - Icon library
- **date-fns** - Date formatting

## Project Structure

```
src/
├── app/
│   ├── documents/
│   │   └── page.tsx      # Documents page
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Home page
├── components/
│   └── ui/                # Reusable UI components
├── hooks/
│   └── use-toast.ts       # Toast notifications hook
└── lib/
    ├── supabase.ts        # Supabase client
    └── utils.ts           # Utility functions
```
=======
# Next.js AI Agent Dashboard

This is a Next.js 14+ application migrated from the original Vite frontend, featuring TypeScript, Tailwind CSS, shadcn/ui components, and Supabase authentication.

## Features

- **Next.js 14+** with App Router
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **shadcn/ui** components built on Radix UI
- **Supabase** authentication with email/password and Google OAuth
- **Dark mode** support with next-themes
- **Toast notifications** for user feedback

## Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Environment variables:**
   Copy `.env.example` to `.env.local` and fill in your Supabase credentials:
   ```bash
   cp .env.example .env.local
   ```

   Required environment variables:
   ```
   NEXT_PUBLIC_SUPABASE_URL=your-supabase-project-url
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
   NEXT_PUBLIC_AGENT_ENDPOINT=your-agent-api-endpoint
   NEXT_PUBLIC_ENABLE_STREAMING=true
   NEXT_PUBLIC_LANGFUSE_HOST_WITH_PROJECT=your-langfuse-host
   ```

3. **Run development server:**
   ```bash
   npm run dev
   ```

   The application will be available at [http://localhost:3000](http://localhost:3000)

## Project Structure

```
src/
├── app/                    # Next.js app directory
│   ├── auth/
│   │   └── callback/       # OAuth callback page
│   ├── chat/               # Chat page (authenticated)
│   ├── login/              # Login page
│   ├── globals.css         # Global styles
│   ├── layout.tsx          # Root layout
│   └── page.tsx            # Home page (redirects)
├── components/
│   ├── auth/               # Authentication components
│   ├── theme/              # Theme provider
│   └── ui/                 # shadcn/ui components
├── hooks/
│   └── useAuth.tsx         # Authentication hook
└── lib/
    ├── supabase.ts         # Supabase client
    └── utils.ts            # Utility functions
```

## Authentication Flow

1. **Login page** (`/login`) - Users can sign in with email/password or Google OAuth
2. **OAuth callback** (`/auth/callback`) - Handles Google OAuth redirects
3. **Protected routes** - Chat page requires authentication
4. **Automatic redirects** - Unauthenticated users are redirected to login

## Key Differences from Vite Version

1. **Environment variables** - Changed from `VITE_*` to `NEXT_PUBLIC_*` prefix
2. **Routing** - Uses Next.js App Router instead of React Router
3. **SSR/SSG** - Next.js provides server-side rendering capabilities
4. **File-based routing** - Pages are defined by file structure in `app/` directory
5. **Built-in optimizations** - Image optimization, font optimization, etc.

## Available Scripts

- `npm run dev` - Start development server on port 3000
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run test` - Run Playwright tests (when configured)

## Migration Notes

This application maintains the same visual design and functionality as the original Vite version while leveraging Next.js features for improved performance and developer experience.

The authentication system uses the same Supabase setup and should work seamlessly with existing user accounts and database schema.
