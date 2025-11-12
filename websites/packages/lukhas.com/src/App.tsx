import { Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import SolutionsPage from './pages/SolutionsPage'
import EnterprisePage from './pages/EnterprisePage'

function App() {
  return (
    <div className="min-h-screen bg-consciousness-deep text-awareness-silver">
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/solutions" element={<SolutionsPage />} />
        <Route path="/enterprise" element={<EnterprisePage />} />
      </Routes>
    </div>
  )
}

export default App
