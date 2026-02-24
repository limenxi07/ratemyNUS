interface Comment {
  text: string;
  upvotes: number;
  date: string | null;
}

interface Props {
  comments: Comment[];
  count: number;
}

export default function InsufficientReviews({ comments, count }: Props) {
  return (
    <div className="bg-navbar/50 border-2 border-outline-primary rounded-2xl p-8">
      <div className="text-center mb-6">
        <div className="text-4xl mb-3">⚠️</div>
        <h3 className="font-serif font-bold text-xl text-text-body mb-2">
          Limited Review Data
        </h3>
        <p className="text-text-body/70">
          Only {count} review{count !== 1 ? 's' : ''} available. Showing all reviews below.
        </p>
      </div>

      <div className="space-y-4">
        {comments.map((comment, index) => (
          <div
            key={index}
            className="bg-surface border-2 border-outline-primary rounded-2xl p-6"
          >
            <p className="text-text-body/80 leading-relaxed mb-3">
              {comment.text}
            </p>
            <div className="flex items-center gap-4 text-sm text-text-body/60">
              <span>👍 {comment.upvotes} helpful</span>
              {comment.date && (
                <>
                  <span>•</span>
                  <span>{new Date(comment.date).toLocaleDateString('en-SG', { year: 'numeric', month: 'short' })}</span>
                </>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}