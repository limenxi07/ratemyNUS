import SentimentDisplay from '@/components/SentimentDisplay';
import InsufficientReviews from '@/components/InsufficientReviews';

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
          <div className="bg-navbar/50 border-2 border-outline-primary rounded-2xl p-8 text-center">
            <h2 className="font-serif font-bold text-2xl text-text-body mb-2">
              Module not found
            </h2>
            <p className="text-text-body/70">
              The module code &quot;{params.code}&quot; does not exist in our database.
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
        <div className="bg-surface border-2 border-outline-primary rounded-2xl p-8 mb-6">
          <div className="font-serif font-bold text-4xl text-text-body mb-2">
            {module.code}
          </div>
          <div className="text-xl text-text-body/80 mb-6">
            {module.name}
          </div>

          {/* Quick Facts */}
          <div className="flex flex-wrap gap-4 text-sm">
            <div className="bg-navbar px-4 py-2 rounded-xl border border-outline-primary">
              <span className="font-semibold text-text-primary">{module.units}</span> MCs
            </div>
            <div className="bg-navbar px-4 py-2 rounded-xl border border-outline-primary">
              Sem <span className="font-semibold text-text-primary">{module.semesters.join(', ')}</span>
            </div>
            <div className="bg-navbar px-4 py-2 rounded-xl border border-outline-primary">
              <span className="font-semibold text-text-primary">{module.comment_count}</span> reviews
            </div>
          </div>

          {/* Description */}
          {module.description && (
            <div className="mt-6 pt-6 border-t-2 border-outline-primary/20">
              <h3 className="font-semibold text-text-body mb-2">Description</h3>
              <p className="text-text-body/70 leading-relaxed">
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
                className="inline-block text-text-primary font-semibold hover:underline"
              >
                View on NUSMods →
              </a>
            </div>
          )}
        </div>

        {/* Sentiment Analysis or Insufficient Data */}
        {module.sentiment_data ? (
          module.sentiment_data.insufficient_data ? (
            <InsufficientReviews 
              comments={module.sentiment_data.raw_comments}
              count={module.comment_count}
            />
          ) : (
            <SentimentDisplay data={module.sentiment_data} />
          )
        ) : (
          <div className="bg-navbar/50 border-2 border-outline-primary rounded-2xl p-8 text-center">
            <div className="text-text-body/60 mb-2">
              📊 Sentiment analysis not yet available
            </div>
            <p className="text-sm text-text-body/50">
              Run sentiment analysis to see aggregated insights
            </p>
          </div>
        )}
      </div>
    </main>
  );
}