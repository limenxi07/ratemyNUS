import Link from 'next/link'

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <h2 className="font-serif font-bold text-4xl text-text-body mb-4">
          404 - Page Not Found
        </h2>
        <p className="text-text-body/70 mb-6">
          The page you're looking for doesn't exist.
        </p>
        <Link 
          href="/"
          className="bg-text-primary text-white px-6 py-3 rounded-xl inline-block hover:opacity-90"
        >
          Go Home
        </Link>
      </div>
    </div>
  )
}