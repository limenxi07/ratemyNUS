export default function Loading() {
  return (
    <main className="min-h-screen">
      <div className="max-w-6xl mx-auto px-6 py-12">
        <div className="h-10 bg-outline-primary/30 rounded w-1/3 mb-8 animate-pulse"></div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(12)].map((_, i) => (
            <div key={i} className="bg-surface border-2 border-outline-primary rounded-2xl p-6 animate-pulse">
              <div className="h-6 bg-outline-primary/30 rounded w-1/2 mb-2"></div>
              <div className="h-4 bg-outline-primary/20 rounded w-full mb-4"></div>
              <div className="h-3 bg-outline-primary/20 rounded w-2/3"></div>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}