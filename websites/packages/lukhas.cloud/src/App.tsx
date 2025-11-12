import { Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import PricingPage from './pages/PricingPage'
import CompliancePage from './pages/CompliancePage'

function App() {
  return (
    <div className="min-h-screen bg-consciousness-deep text-awareness-silver">
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/pricing" element={<PricingPage />} />
        <Route path="/compliance" element={<CompliancePage />} />
      </Routes>
    </div>
  )
}

export default App
