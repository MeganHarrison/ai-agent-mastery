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