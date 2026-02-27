import SentimentDisplay from '@/components/SentimentDisplay';
import InsufficientReviews from '@/components/InsufficientReviews';

async function getModule(code: string) {
  const res = await fetch(`http://localhost:8000/api/modules/${code}`, { cache: 'no-store' });
  if (!res.ok) return null;
  return res.json();
}

export default async function ModulePage({ params }: { params: Promise<{ code: string }>  }) {
  const { code } = await params; 
  const module = await getModule(code);

  if (!module) {
    return (
      <main className="min-h-screen">
        <div className="max-w-4xl mx-auto px-6 py-12">
          <div className="bg-navbar/50 border-2 border-outline-primary rounded-2xl p-8 text-center">
            <h2 className="font-serif font-bold text-2xl text-text-body mb-2">
              Module not found
            </h2>
            <p className="text-text-body/70">
              The module code &quot;{code}&quot; does not exist in our database.
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
          <div className="font-serif font-bold text-5xl text-text-body mb-2">
            {module.code}
          </div>
          <div className="text-xl text-text-body/80 mb-4">
            {module.name}
          </div>

          {/* Quick Facts */}
          <div className="flex flex-wrap gap-4 text-sm">
            {module.sentiment_data && !module.sentiment_data.insufficient_data && module.sentiment_data.average && (
              // conditional rendering of average (with color coding) 
              <>
              {module.sentiment_data.average >= 4.0 ? (
                <div className="px-4 py-2 rounded-xl border-2 font-semibold bg-green/60 text-dark-green border-green">
                  {module.sentiment_data.average.toFixed(1)}/5.0
                </div>
              ) : module.sentiment_data.average >= 3.0 ? (
                <div className="px-4 py-2 rounded-xl border-2 font-semibold bg-yellow/60 text-dark-yellow border-yellow">
                  {module.sentiment_data.average.toFixed(1)}/5.0
                </div>
              ) : (
                <div className="px-4 py-2 rounded-xl border-2 font-semibold bg-peach/60 text-dark-peach border-peach">
                  {module.sentiment_data.average.toFixed(1)}/5.0
                </div>
              )}
            </>
            )}
            <div className="bg-navbar px-4 py-2 rounded-xl border-2 border-outline-primary">
              <span className="font-semibold text-text-primary">{module.units}</span> MCs
            </div>
            <div className="bg-navbar px-4 py-2 rounded-xl border-2 border-outline-primary">
              Sem <span className="font-semibold text-text-primary">{module.semesters.join(', ')}</span>
            </div>
            <div className="bg-navbar px-4 py-2 rounded-xl border-2 border-outline-primary">
              <span className="font-semibold text-text-primary">{module.comment_count}</span> reviews
            </div>
            <div className="bg-navbar px-4 py-2 rounded-xl border-2 border-outline-primary">
              <a className="font-semibold text-text-primary hover:underline" href={module.url} target="_blank" rel="noopener noreferrer">View on NUSMods →</a> 
            </div>
          </div>

          {/* Description // TODO: removed for now because it was too useless
          {module.description && (
            <div className="mt-6 pt-6 border-t-2 border-outline-primary/20">
              <p className="text-text-body/70 leading-relaxed">
                {module.description}
              </p>
            </div>
          )}*/
          }
          

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
          <div className="bg-surface border-2 border-outline-primary rounded-2xl p-8 text-center">
            <div className="text-text-body/60 italic">
              Sentiment analysis is not yet available. Please check back next time!
            </div>
          </div>
        )}
      </div>
    </main>
  );
}