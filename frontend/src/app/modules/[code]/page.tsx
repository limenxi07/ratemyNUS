async function getModule(code: string) {
  const res = await fetch(`http://localhost:8000/api/modules/${code}`, { cache: 'no-store' });
  if (!res.ok) return null;
  return res.json();
}

export default async function ModulePage({ params }: { params: { code: string } }) {
  const module = await getModule(params.code);

  if (!module) {
    return (
      <main className="min-h-screen">
        <div className="max-w-4xl mx-auto px-6 py-12">
          <div className="bg-peach/20 border-2 border-peach rounded-2xl p-8 text-center">
            <h2 className="font-serif font-bold text-2xl text-off-black mb-2">
              Module not found
            </h2>
            <p className="text-off-black/70">
              The module code "{params.code}" does not exist in our database.
            </p>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen">
      <div className="max-w-4xl mx-auto px-6 py-12">
        {/* Module Header */}
        <div className="bg-white border-2 border-sage rounded-2xl p-8 mb-6">
          <div className="font-serif font-bold text-4xl text-off-black mb-2">
            {module.code}
          </div>
          <div className="text-xl text-off-black/80 mb-6">
            {module.name}
          </div>

          {/* Quick Facts */}
          <div className="flex flex-wrap gap-4 text-sm">
            <div className="bg-sage-light px-4 py-2 rounded-xl">
              <span className="font-semibold">{module.units}</span> MCs
            </div>
            <div className="bg-sage-light px-4 py-2 rounded-xl">
              Sem <span className="font-semibold">{module.semesters.join(', ')}</span>
            </div>
            <div className="bg-sage-light px-4 py-2 rounded-xl">
              <span className="font-semibold">{module.comment_count}</span> reviews
            </div>
          </div>

          {/* Description */}
          {module.description && (
            <div className="mt-6 pt-6 border-t-2 border-sage/20">
              <h3 className="font-semibold text-off-black mb-2">Description</h3>
              <p className="text-off-black/70 leading-relaxed">
                {module.description}
              </p>
            </div>
          )}

          {/* NUSMods Link */}
          {module.url && (
            <div className="mt-6">
              <a
                href={module.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-block text-tan font-semibold hover:underline"
              >
                View on NUSMods →
              </a>
            </div>
          )}
        </div>

        {/* Placeholder for Sentiment Analysis */}
        <div className="bg-cream/50 border-2 border-sage/30 rounded-2xl p-8 text-center">
          <div className="text-off-black/60 mb-2">
            📊 AI-powered sentiment analysis coming soon
          </div>
          <p className="text-sm text-off-black/50">
            Aggregated scores for workload, difficulty, usefulness, and enjoyability will be displayed here
          </p>
        </div>
      </div>
    </main>
  );
}