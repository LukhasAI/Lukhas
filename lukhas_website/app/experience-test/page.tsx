export default function ExperienceTest() {
  return (
    <div className="min-h-screen bg-black text-white flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-constellation-identity mb-4">
          🌟 Experience Test Page - Updated
        </h1>
        <p className="text-constellation-vision">
          If you can see this, routing is working fine.
        </p>
        <p className="text-constellation-quantum mt-4">
          The original /experience route has compilation issues with dynamic imports.
        </p>
      </div>
    </div>
  )
}