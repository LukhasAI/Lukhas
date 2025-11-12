import { Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import DiscoverPage from './pages/DiscoverPage'
import AppPage from './pages/AppPage'

function App() {
  return (
    <div className="min-h-screen bg-consciousness-deep text-awareness-silver">
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/discover" element={<DiscoverPage />} />
        <Route path="/app/:appId" element={<AppPage />} />
      </Routes>
    </div>
  )
}

export default App
