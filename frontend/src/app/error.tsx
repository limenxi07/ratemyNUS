'use client'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <h2 className="font-serif font-bold text-5xl text-text-body mb-4">
          Unexpected error
        </h2>
        <button
          onClick={() => reset()}
          className="bg-text-primary text-white px-6 py-3 rounded-xl hover:opacity-90"
        >
          Try again
        </button>
      </div>
    </div>
  )
}