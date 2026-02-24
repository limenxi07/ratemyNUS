import SearchBar from '@/components/SearchBar';
import Link from 'next/link';

export default function Home() {
  return (
    <main className="min-h-screen">
      <div className="max-w-4xl mx-auto px-6 py-20">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h1 className="font-serif font-bold text-8xl text-text-body mb-4">
            ratemyNUS
          </h1>
          <p className="text-xl text-text-body/70 italic font-medium">
            Aggregated 2-minute NUSMods reviews
          </p>
        </div>

        {/* Search Bar */}
        <div className="mb-8">
          <SearchBar size="large" />
        </div>
      </div>
    </main>
  );
}