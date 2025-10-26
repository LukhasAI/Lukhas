export default function TestPage() {
  return (
    <div className="min-h-screen bg-black text-white p-8">
      <h1 className="text-6xl font-thin mb-8">LUKHAS TEST</h1>
      <p className="text-xl text-gray-400 mb-4">If you can see this text in white on black background, Tailwind is working.</p>
      <div className="bg-white/10 p-4 rounded-lg mb-4">
        <p>This should be a semi-transparent white box</p>
      </div>
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 p-4 rounded-lg text-white">
        <p>This should have a purple to blue gradient background</p>
      </div>
    </div>
  )
}