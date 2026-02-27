export default function AboutPage() {
  return (
    <main className="min-h-screen">
      <div className="max-w-3xl mx-auto px-6 py-12">
        <h1 className="font-serif font-bold text-4xl text-text-body mb-6 text-center">
          about ratemyNUS
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
              We also recommend actionable advice for each module, should you choose to take it. 
            </p>
          </div>

          <div>
            <h2 className="font-serif font-semibold text-2xl text-text-body mb-3">
              How does the average score work?
            </h2>
            <p className="text-text-body/70 italic leading-relaxed">
              The average score is a simple average of the four sentiment scores (workload, difficulty, usefulness, enjoyability). We take the inverse of workload and difficulty scores since a higher score in those categories indicates a more negative sentiment. This score is rounded to the nearest 0.5. If you have any suggestions on how to improve this metric, please let us know!</p>
          </div>

          <div>
            <h2 className="font-serif font-semibold text-2xl text-text-body mb-3">
              What modules are covered?
            </h2>
            <p className="text-text-body/70 italic leading-relaxed">
              We currently cover 14 popular computing modules. More modules will be added soon!
            </p>
          </div>

          <div className="pt-4 border-t-2 border-outline-primary/20">
            <p className="text-sm text-text-body/50">
              Open to feedback and suggestions! Feel free to <a href="mailto:limenxi@u.nus.edu?subject=ratemyNUS%20feedback" className="text-text-primary hover:underline">reach out</a> &lt;3
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}