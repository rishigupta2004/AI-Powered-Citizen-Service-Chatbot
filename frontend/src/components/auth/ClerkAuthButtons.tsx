import { useEffect } from 'react'
import {
  SignedIn,
  SignedOut,
  SignInButton,
  SignUpButton,
  UserButton,
  useAuth,
} from '@clerk/clerk-react'

import { useAuthContext } from '../../contexts/AuthContext'
import { API_BASE_URL } from '../../lib/api'

const HAS_CLERK_KEY = Boolean(import.meta.env.VITE_CLERK_PUBLISHABLE_KEY)

export function ClerkAuthButtons() {
  if (!HAS_CLERK_KEY) {
    return null
  }

  return (
    <>
      <SignedOut>
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
      </SignedOut>
      <SignedIn>
        <div className="flex items-center gap-2">
          <UserButton />
          <ClerkSessionBridge />
        </div>
      </SignedIn>
    </>
  )
}

function ClerkSessionBridge() {
  const { getToken, userId, isLoaded, isSignedIn } = useAuth()
  const { setBackendSession } = useAuthContext()

  useEffect(() => {
    if (!isLoaded || !isSignedIn || !userId) return

    const sync = async () => {
      for (let attempt = 0; attempt < 3; attempt += 1) {
        try {
          const clerkToken = await getToken()
          if (!clerkToken) {
            await new Promise((resolve) => setTimeout(resolve, 350 * (attempt + 1)))
            continue
          }

          const res = await fetch(`${API_BASE_URL}/api/auth/clerk/sync`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ clerk_token: clerkToken }),
          })

          if (!res.ok) {
            await new Promise((resolve) => setTimeout(resolve, 350 * (attempt + 1)))
            continue
          }

          const data = await res.json()
          setBackendSession(data.access_token, data.refresh_token, data.user)
          return
        } catch {
          await new Promise((resolve) => setTimeout(resolve, 350 * (attempt + 1)))
        }
      }
      console.warn('Clerk sign-in succeeded, but backend session sync failed.')
    }

    void sync()
  }, [getToken, isLoaded, isSignedIn, setBackendSession, userId])

  return null
}
