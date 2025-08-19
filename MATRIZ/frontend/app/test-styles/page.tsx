export default function TestPage() {
  return (
    <div className="min-h-screen bg-black text-white p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        <h1 className="text-6xl font-thin">MATADA Test Page</h1>
        <p className="text-xl">Testing if Tailwind styles are working properly</p>
        
        <div className="grid grid-cols-3 gap-4">
          <div className="p-4 border border-purple-600 rounded">
            <div className="text-4xl mb-2">⚛️</div>
            <p className="text-sm uppercase tracking-wider">Identity</p>
          </div>
          <div className="p-4 border border-blue-600 rounded">
            <div className="text-4xl mb-2">🧠</div>
            <p className="text-sm uppercase tracking-wider">Consciousness</p>
          </div>
          <div className="p-4 border border-green-600 rounded">
            <div className="text-4xl mb-2">🛡️</div>
            <p className="text-sm uppercase tracking-wider">Guardian</p>
          </div>
        </div>
        
        <div className="space-y-4">
          <button className="px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded">
            Gradient Button
          </button>
          <button className="px-6 py-3 border border-white text-white rounded ml-4">
            Border Button
          </button>
        </div>
        
        <div className="p-6 bg-gray-900 rounded">
          <h2 className="text-2xl mb-4">Dark Panel</h2>
          <p>This is a test of a dark background panel with white text.</p>
        </div>
      </div>
    </div>
  )
}