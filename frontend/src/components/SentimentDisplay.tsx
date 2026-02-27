interface SentimentData {
  workload: number;
  difficulty: number;
  usefulness: number;
  enjoyability: number;
  average: number;
  summary: string;
  reasoning: string;
  advice: {
    general?: string;
    midterm?: string;
    final?: string;
    practical?: string;
    assignments?: string;
    tutorial?: string;
    recitation?: string;
  };
  top_comments: Array<{
    text: string;
    upvotes: number;
    date: string;
    author?: string;
  }>;
}

interface Props {
  data: SentimentData;
}

export default function SentimentDisplay({ data }: Props) {
  const scores = [
    { label: 'Workload', value: data.workload},
    { label: 'Difficulty', value: data.difficulty},
    { label: 'Usefulness', value: data.usefulness},
    { label: 'Enjoyability', value: data.enjoyability},
  ];

  // Filter advice sections that exist
  const adviceEntries = Object.entries(data.advice).filter(([_, value]) => value);

  // Helper function to get color based on score
  const getScoreColor = (value: number, label: string) => {
    // For Workload and Difficulty: higher is bad (red)
    // For Usefulness and Enjoyability: higher is good (green)
    const isInverted = label === 'Workload' || label === 'Difficulty';
    
    if (isInverted) {
      // 4.0-5.0 = red (bad), 3.0-4.0 = yellow (moderate), 1.0-3.0 = green (good)
      if (value >= 4.0) return { border: 'border-peach', bg: 'bg-peach/60', text: 'text-dark-peach' };
      if (value >= 3.0) return { border: 'border-yellow', bg: 'bg-yellow/60', text: 'text-dark-yellow' };
      return { border: 'border-green', bg: 'bg-green/60', text: 'text-dark-green' };
    } else {
      // 4.0-5.0 = green (good), 3.0-4.0 = yellow (moderate), 1.0-3.0 = red (bad)
      if (value >= 4.0) return { border: 'border-green', bg: 'bg-green/60', text: 'text-dark-green' };
      if (value >= 3.0) return { border: 'border-yellow', bg: 'bg-yellow/60', text: 'text-dark-yellow' };
      return { border: 'border-peach', bg: 'bg-peach/60', text: 'text-dark-peach' };
    }
  };

  return (
    <div className="space-y-6">
      {/* Module Insights - Summary, Scoring, Advice */}
      <div className="bg-surface border-2 border-outline-primary rounded-2xl p-8 pb-0">
        {/* Summary */}
        <div className="text-center mb-8">
          <h3 className="font-serif font-bold text-4xl text-text-body mb-2 pb-3">
            Module Insights
          </h3>
          <p className="text-text-body/80 leading-relaxed">
            {data.summary}
          </p>
          <p className="text-sm text-text-body/60 pt-2 italic">(Scores out of 5.0)</p>
          <div className="flex justify-center gap-8 flex-wrap pt-6">
          {scores.map((score) => {
            const colors = getScoreColor(score.value, score.label);

            return (
              <div key={score.label} className="flex flex-col items-center">
                <div className="relative w-24 h-24 mb-3">
                  {/* Circle */}
                  <div className={`absolute inset-0 rounded-full border-4 ${colors.border} ${colors.bg} flex items-center justify-center`}>
                    <span className={`text-3xl font-bold ${colors.text}`}>
                      {score.value.toFixed(1)}
                    </span>
                  </div>
                </div>
                <div className="text-center">
                  <div className="font-semibold text-text-body/90 italic">{score.label}</div>
                </div>
              </div>
          )})}
        </div>
        </div>
      </div>
      
      <div className="bg-surface border-2 border-outline-primary rounded-2xl p-8">
        {/* Advice */}
        {adviceEntries.length > 0 && (
          <div>
            <h3 className="font-serif font-bold text-4xl text-text-body mb-2 pb-6 text-center">
              Advice for Future Students
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {adviceEntries.map(([category, advice]) => (
                <div key={category} className="bg-navbar/50 rounded-xl p-4">
                  <div className="font-semibold text-text-primary capitalize mb-2 center">
                    {category.charAt(0).toUpperCase() + category.slice(1)}
                  </div>
                  <p className="text-text-body/80 leading-relaxed">
                    {advice}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Top Comments */}
        {data.top_comments && data.top_comments[0].text != undefined && (
          <div className="bg-surface border-2 border-outline-primary rounded-2xl p-8">
          <div>
            <h3 className="font-serif font-bold text-4xl text-text-body mb-2 pb-6 text-center">
              Top Reviews
            </h3>
            
            <div className="space-y-4">
              {data.top_comments.map((comment, index) => (
                <div
                  key={index}
                  className="bg-navbar/50 rounded-xl p-4"
                >
                  <p className="text-text-body/80 leading-relaxed mb-3">
                    &quot;{comment.text}&quot;
                  </p>
                  <div className="flex items-center gap-4 text-sm text-text-body/60">
                    <span>{new Date(comment.date).toLocaleDateString('en-SG', { year: 'numeric', month: 'short' })}</span>
                    <span>•</span>
                    <span>{comment.upvotes} ⬆️</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
        )}
    </div>
  );
}