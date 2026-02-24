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
        <h1 className="font-serif font-bold text-4xl text-text-body mb-8">
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
              <div className="text-sm text-text-body/50">
                {module.comment_count} reviews
              </div>
            </a>
          ))}
        </div>
      </div>
    </main>
  );
}