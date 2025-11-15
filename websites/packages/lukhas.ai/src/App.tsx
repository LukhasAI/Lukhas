import { Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import AboutPage from './pages/AboutPage'
import PlaygroundPage from './pages/PlaygroundPage'
import TechnologyPage from './pages/TechnologyPage'
import PricingPage from './pages/PricingPage'
import UseCasesPage from './pages/UseCasesPage'
import FAQPage from './pages/FAQPage'
import PrivacyPage from './pages/PrivacyPage'
import TermsPage from './pages/TermsPage'
import ContactPage from './pages/ContactPage'
import CookiePolicyPage from './pages/CookiePolicyPage'

function App() {
  return (
    <div className="min-h-screen bg-consciousness-deep text-awareness-silver">
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="/playground" element={<PlaygroundPage />} />
        <Route path="/technology" element={<TechnologyPage />} />
        <Route path="/pricing" element={<PricingPage />} />
        <Route path="/use-cases" element={<UseCasesPage />} />
        <Route path="/faq" element={<FAQPage />} />
        <Route path="/privacy" element={<PrivacyPage />} />
        <Route path="/terms" element={<TermsPage />} />
        <Route path="/contact" element={<ContactPage />} />
        <Route path="/cookies" element={<CookiePolicyPage />} />
      </Routes>
    </div>
  )
}

export default App
