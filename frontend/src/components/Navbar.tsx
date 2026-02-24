import Link from 'next/link';

export default function Navbar() {
  return (
    <nav className="bg-navbar border-b-2 border-outline-primary">
      <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
        <Link href="/" className="font-serif font-bold text-2xl text-text-body hover:text-text-primary transition">
          ratemyNUS
        </Link>
        
        <div className="flex gap-9 font-medium">
          <Link href="/modules" className="font-serif font-semibold text-xl text-text-body hover:text-text-primary transition">
            browse
          </Link>
          <Link href="/about" className="font-serif font-semibold text-xl text-text-body hover:text-text-primary transition">
            about
          </Link>
        </div>
      </div>
    </nav>
  );
}