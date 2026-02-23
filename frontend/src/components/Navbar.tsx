import Link from 'next/link';

export default function Navbar() {
  return (
    <nav className="bg-cream border-b-2 border-sage">
      <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
        <Link href="/" className="font-serif font-bold text-2xl text-off-black hover:text-tan transition">
          ratemyNUS
        </Link>
        
        <div className="flex gap-6 font-medium">
          <Link href="/modules" className="text-off-black hover:text-tan transition">
            browse
          </Link>
          <Link href="/about" className="text-off-black hover:text-tan transition">
            about
          </Link>
        </div>
      </div>
    </nav>
  );
}