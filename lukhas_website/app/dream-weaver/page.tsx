import DreamWeaverClient from './DreamWeaverClient'

export default function DreamWeaverPage() {
  return (
    <main className="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-2xl text-center">
        <h1 className="text-5xl font-thin mb-4">Dream Weaver</h1>
        <p className="text-lg text-gray-400 mb-8">
          Plant a seed of thought, and watch a dream unfold.
        </p>
        <DreamWeaverClient />
      </div>
    </main>
  )
}
