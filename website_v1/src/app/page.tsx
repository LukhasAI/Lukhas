import Hero from '@/components/homepage/Hero';
import ProductGrid from '@/components/homepage/ProductGrid';
import Vision from '@/components/homepage/Vision';
import About from '@/components/homepage/About';
import Careers from '@/components/homepage/Careers';
import Newsletter from '@/components/homepage/Newsletter';
import Footer from '@/components/homepage/Footer';

export default function HomePage() {
  return (
    <main className="min-h-screen bg-[var(--background)]">
      <Hero />
      <ProductGrid />
      <Vision />
      <About />
      <Careers />
      <Newsletter />
      <Footer />
    </main>
  );
}