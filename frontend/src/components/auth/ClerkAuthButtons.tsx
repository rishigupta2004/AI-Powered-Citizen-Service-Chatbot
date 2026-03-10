import { useEffect } from 'react'
import {
  Show,
  SignInButton,
  SignUpButton,
  UserButton,
  useAuth,
} from '@clerk/react'

import { useAuthContext } from '../../contexts/AuthContext'

export function ClerkAuthButtons() {
  return (
    <>
      <Show when="signed-out">
        <div className="flex items-center gap-2">
          <SignInButton mode="modal">
            <button className="rounded-full border border-[var(--border)] px-4 py-2 text-sm font-semibold text-[var(--foreground)] hover:bg-[var(--surface-2)]">
              Sign In
            </button>
          </SignInButton>
          <SignUpButton mode="modal">
            <button className="rounded-full bg-[var(--color-navy)] px-4 py-2 text-sm font-semibold text-white hover:bg-[var(--color-navy-700)]">
              Sign Up
            </button>
          </SignUpButton>
        </div>
      </Show>
      <Show when="signed-in">
        <div className="flex items-center gap-2">
          <UserButton />
          <ClerkSessionBridge />
        </div>
      </Show>
    </>
  )
}

function ClerkSessionBridge() {
  const { getToken, userId, isLoaded, isSignedIn } = useAuth()
  const { setBackendSession } = useAuthContext()

  useEffect(() => {
    if (!isLoaded || !isSignedIn || !userId) return

    const sync = async () => {
      try {
        const clerkToken = await getToken()
        if (!clerkToken) return

        const apiUrl = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
        const res = await fetch(`${apiUrl}/api/auth/clerk/sync`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ clerk_token: clerkToken }),
        })

        if (!res.ok) {
          return
        }

        const data = await res.json()
        setBackendSession(data.access_token, data.refresh_token, data.user)
      } catch {
        // Intentionally silent: Clerk UI should still function.
      }
    }

    void sync()
  }, [getToken, isLoaded, isSignedIn, setBackendSession, userId])

  return null
}
