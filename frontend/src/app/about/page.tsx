export default function AboutPage() {
  return (
    <main className="min-h-screen">
      <div className="max-w-3xl mx-auto px-6 py-12">
        <h1 className="font-serif font-bold text-4xl text-text-body mb-6">
          ratemyNUS
        </h1>

        <div className="bg-surface border-2 border-outline-primary rounded-2xl p-8 space-y-6">
          <div>
            <h2 className="font-serif font-semibold text-2xl text-text-body mb-3">
              What is this?
            </h2>
            <p className="text-text-body/70 italic leading-relaxed">
              ratemyNUS aggregates hundreds of student reviews from NUSMods into a 2-minute summary to make module information easily digestible.
            </p>
          </div>

          <div>
            <h2 className="font-serif font-semibold text-2xl text-text-body mb-3">
              How does it work?
            </h2>
            <p className="text-text-body/70 italic leading-relaxed">
              We scrape reviews from NUSMods Disqus comments, analyse them using AI, 
              and present aggregated scores for workload, difficulty, usefulness, and enjoyability. 
              We also select the top comments in terms of recency, upvotes, and insightfulness should you want to read more!
            </p>
          </div>

          <div>
            <h2 className="font-serif font-semibold text-2xl text-text-body mb-3">
              Current Coverage
            </h2>
            <p className="text-text-body/70 italic leading-relaxed">
              We currently cover 14 popular computing modules. More modules will be added soon!
            </p>
          </div>

          <div className="pt-4 border-t-2 border-outline-primary/20">
            <p className="text-sm text-text-body/50">
              Built by a CS dog, for fellow CS victims.
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}