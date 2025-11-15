import { Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import CompliancePage from './pages/CompliancePage'
import ContactPage from './pages/ContactPage'

function App() {
  return (
    <div className="min-h-screen bg-consciousness-deep text-awareness-silver">
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/compliance" element={<CompliancePage />} />
        <Route path="/contact" element={<ContactPage />} />
      </Routes>
    </div>
  )
}

export default App
