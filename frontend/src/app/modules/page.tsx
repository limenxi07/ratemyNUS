async function getModules() {
  const res = await fetch('http://localhost:8000/api/modules', { cache: 'no-store' });
  if (!res.ok) throw new Error('Failed to fetch modules');
  return res.json();
}

export default async function ModulesPage() {
  const modules = await getModules();

  return (
    <main className="min-h-screen">
      <div className="max-w-6xl mx-auto px-6 py-12">
        <h1 className="font-serif font-bold text-5xl text-text-body mb-10 text-center">
          Browse All Modules
        </h1>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {modules.map((module: any) => (
            <a
              key={module.code}
              href={`/modules/${module.code}`}
              className="block bg-surface border-2 border-outline-primary rounded-2xl p-6 hover:border-outline-active hover:shadow-lg transition"
            >
              <div className="font-semibold text-2xl font-serif mb-2">
                {module.code}
              </div>
              <div className="text-text-body/70 italic mb-4 line-clamp-2">
                {module.name}
              </div>
              <div className="flex items-center gap-3 text-xs flex-wrap">
                {module.sentiment_data && !module.sentiment_data.insufficient_data && module.sentiment_data.average && (
                  <>
                    {module.sentiment_data.average >= 4.0 ? (
                      <div className="px-2 py-1 rounded-lg font-semibold border bg-green/20 text-dark-green border-green">
                        {module.sentiment_data.average.toFixed(1)}/5.0
                      </div>
                    ) : module.sentiment_data.average >= 3.0 ? (
                      <div className="px-2 py-1 rounded-lg font-semibold border bg-yellow/20 text-dark-yellow border-yellow">
                        {module.sentiment_data.average.toFixed(1)}/5.0
                      </div>
                    ) : (
                      <div className="px-2 py-1 rounded-lg font-semibold border bg-peach/20 text-dark-peach border-peach">
                        {module.sentiment_data.average.toFixed(1)}/5.0
                      </div>
                    )}
                  </>
                )}
                <span className="text-text-body/30">•</span>
                <div className="text-text-body/50">
                  {module.comment_count} reviews
                </div>
              </div>
            </a>
          ))}
        </div>
      </div>
    </main>
  );
}