export default function Loading() {
  return (
    <div className="min-h-screen">
      <div className="max-w-4xl mx-auto px-6 py-12">
        <div className="bg-surface border-2 border-outline-primary rounded-2xl p-8 mb-6 animate-pulse">
          <div className="h-10 bg-outline-primary/30 rounded w-1/3 mb-4"></div>
          <div className="h-6 bg-outline-primary/20 rounded w-2/3 mb-6"></div>
          <div className="flex gap-4">
            <div className="h-10 bg-outline-primary/20 rounded w-20"></div>
            <div className="h-10 bg-outline-primary/20 rounded w-24"></div>
            <div className="h-10 bg-outline-primary/20 rounded w-28"></div>
          </div>
        </div>
      </div>
    </div>
  )
}