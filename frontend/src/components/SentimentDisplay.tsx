interface SentimentData {
  workload: number;
  difficulty: number;
  usefulness: number;
  enjoyability: number;
  summary: string;
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
  }>;
}

interface Props {
  data: SentimentData;
}

export default function SentimentDisplay({ data }: Props) {
  const scores = [
    { label: 'Workload', value: data.workload, emoji: '📚' },
    { label: 'Difficulty', value: data.difficulty, emoji: '🧠' },
    { label: 'Usefulness', value: data.usefulness, emoji: '💡' },
    { label: 'Enjoyability', value: data.enjoyability, emoji: '😊' },
  ];

  // Filter advice sections that exist
  const adviceEntries = Object.entries(data.advice).filter(([_, value]) => value);

  return (
    <div className="space-y-6">
      {/* Score Circles */}
      <div className="bg-surface border-2 border-outline-primary rounded-2xl p-8">
        <h2 className="font-serif font-bold text-2xl text-text-body mb-6 text-center">
          📊 Student Insights
        </h2>
        
        <div className="flex justify-center gap-8 flex-wrap">
          {scores.map((score) => (
            <div key={score.label} className="flex flex-col items-center">
              <div className="relative w-24 h-24 mb-3">
                {/* Circle */}
                <div className="absolute inset-0 rounded-full border-4 border-outline-primary bg-navbar flex items-center justify-center">
                  <span className="text-3xl font-bold text-text-primary">
                    {score.value.toFixed(1)}
                  </span>
                </div>
              </div>
              <div className="text-center">
                <div className="text-2xl mb-1">{score.emoji}</div>
                <div className="font-semibold text-text-body">{score.label}</div>
                <div className="text-xs text-text-body/60">out of 5.0</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Summary & Advice */}
      <div className="bg-surface border-2 border-outline-primary rounded-2xl p-8">
        {/* Summary */}
        <div className="text-center mb-8">
          <h3 className="font-serif font-bold text-xl text-text-body mb-3">
            📝 Summary
          </h3>
          <p className="text-text-body/80 text-lg leading-relaxed">
            {data.summary}
          </p>
        </div>

        {/* Advice */}
        {adviceEntries.length > 0 && (
          <div className="pt-6 border-t-2 border-outline-primary">
            <h3 className="font-serif font-bold text-xl text-text-body mb-4 text-center">
              💡 Advice for Future Students
            </h3>
            
            <div className="space-y-4">
              {adviceEntries.map(([category, advice]) => (
                <div key={category} className="bg-navbar/50 rounded-xl p-4">
                  <div className="font-semibold text-text-primary capitalize mb-2">
                    {category === 'general' ? '🎯 General' : `📌 ${category.charAt(0).toUpperCase() + category.slice(1)}`}
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
      {data.top_comments && data.top_comments.length > 0 && (
        <div>
          <h3 className="font-serif font-bold text-xl text-text-body mb-4">
            🗣️ Representative Reviews
          </h3>
          
          <div className="space-y-4">
            {data.top_comments.map((comment, index) => (
              <div
                key={index}
                className="bg-surface border-2 border-outline-primary rounded-2xl p-6 hover:border-outline-active transition"
              >
                <p className="text-text-body/80 leading-relaxed mb-3">
                  &quot;{comment.text}&quot;
                </p>
                <div className="flex items-center gap-4 text-sm text-text-body/60">
                  <span>👍 {comment.upvotes} helpful</span>
                  <span>•</span>
                  <span>{new Date(comment.date).toLocaleDateString('en-SG', { year: 'numeric', month: 'short' })}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}