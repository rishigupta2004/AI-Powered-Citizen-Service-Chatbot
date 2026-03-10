# Frontend Tree Decision

**Canonical tree:** `frontend/src/` (Vite + React + TypeScript)

**Rationale:**
- Package manager: npm with Vite (see `frontend/package.json` -> `"dev": "vite"`)
- Active components: `frontend/src/components/`, `frontend/src/contexts/`, `frontend/src/pages/`
- Active API client: `frontend/src/lib/api.ts`
- Auth context: `frontend/src/contexts/AuthContext.tsx`

**Legacy / removed:**
- `frontend/app/` - Next.js-style directory, not the active build target.
- `frontend/lib/api.ts` - deleted; functionality merged into `frontend/src/lib/api.ts`.

**Clerk integration entry point:** `frontend/src/main.tsx` wraps app in `<ClerkProvider>`.
