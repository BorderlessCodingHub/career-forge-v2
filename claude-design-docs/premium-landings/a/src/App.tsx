import Navbar from './components/Navbar';
import Hero from './components/Hero';
import SocialProof from './components/SocialProof';
import Features from './components/Features';
import Curriculum from './components/Curriculum';
import Benefits from './components/Benefits';
import Testimonials from './components/Testimonials';
import Pricing from './components/Pricing';
import FAQ from './components/FAQ';
import CTA from './components/CTA';
import Footer from './components/Footer';
import ScrollToTop from './components/ScrollToTop';

export default function App() {
  return (
    <div className="min-h-screen bg-surface-950 text-surface-200 font-sans antialiased">
      <Navbar />
      <main>
        <Hero />
        <SocialProof />
        <Features />
        <Curriculum />
        <Benefits />
        <Testimonials />
        <Pricing />
        <FAQ />
        <CTA />
      </main>
      <Footer />
      <ScrollToTop />
    </div>
  );
}
