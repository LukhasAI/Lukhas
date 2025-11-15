import { Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import PrivacyPage from './pages/PrivacyPage'
import TermsPage from './pages/TermsPage'
import ContactPage from './pages/ContactPage'
import CookiePolicyPage from './pages/CookiePolicyPage'
import PricingPage from './pages/PricingPage'
import PrivacyPage from './pages/PrivacyPage'
import TermsPage from './pages/TermsPage'
import ContactPage from './pages/ContactPage'
import CookiePolicyPage from './pages/CookiePolicyPage'
import CompliancePage from './pages/CompliancePage'
import PrivacyPage from './pages/PrivacyPage'
import TermsPage from './pages/TermsPage'
import ContactPage from './pages/ContactPage'
import CookiePolicyPage from './pages/CookiePolicyPage'

function App() {
  return (
    <div className="min-h-screen bg-consciousness-deep text-awareness-silver">
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/pricing" element={<PricingPage />} />
        <Route path="/compliance" element={<CompliancePage />} />
        <Route path="/privacy" element={<PrivacyPage />} />
        <Route path="/terms" element={<TermsPage />} />
        <Route path="/contact" element={<ContactPage />} />
        <Route path="/cookies" element={<CookiePolicyPage />} />
      </Routes>
    </div>
  )
}

export default App
