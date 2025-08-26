export default function SimplePage() {
  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(to bottom, #111827, #000000)',
      color: 'white',
      padding: '2rem',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Helvetica Neue", sans-serif'
    }}>
      <nav style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        background: 'rgba(0,0,0,0.8)',
        backdropFilter: 'blur(10px)',
        borderBottom: '1px solid rgba(255,255,255,0.1)',
        padding: '1rem 2rem',
        zIndex: 50
      }}>
        <div style={{ maxWidth: '1280px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1 style={{ fontSize: '1.5rem', letterSpacing: '0.3em', fontWeight: 100 }}>LUKHAS</h1>
          <div style={{ display: 'flex', gap: '2rem', alignItems: 'center' }}>
            <a href="#" style={{ color: 'white', textDecoration: 'none', fontSize: '0.875rem', letterSpacing: '0.1em' }}>PRODUCTS</a>
            <a href="#" style={{ color: 'white', textDecoration: 'none', fontSize: '0.875rem', letterSpacing: '0.1em' }}>TECHNOLOGY</a>
            <button style={{
              background: 'linear-gradient(to right, #7C3AED, #2563EB)',
              color: 'white',
              padding: '0.5rem 1.5rem',
              borderRadius: '0.5rem',
              border: 'none',
              cursor: 'pointer'
            }}>LUKHAS ID</button>
          </div>
        </div>
      </nav>

      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        textAlign: 'center',
        paddingTop: '4rem'
      }}>
        <div>
          <p style={{ fontSize: '0.875rem', letterSpacing: '0.3em', color: '#60A5FA', marginBottom: '2rem', textTransform: 'uppercase' }}>
            Logical Unified Knowledge Hyper-Adaptive Superior Systems
          </p>
          <h1 style={{ fontSize: '6rem', letterSpacing: '0.3em', fontWeight: 100, marginBottom: '2rem' }}>
            LUKHAS
          </h1>
          <p style={{ fontSize: '1.5rem', color: '#9CA3AF', marginBottom: '3rem' }}>
            Building Consciousness You Can Trust
          </p>

          <div style={{ display: 'flex', justifyContent: 'center', gap: '3rem', marginBottom: '3rem' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '3rem', marginBottom: '0.5rem' }}>⚛️</div>
              <p style={{ fontSize: '0.75rem', letterSpacing: '0.1em', textTransform: 'uppercase' }}>Identity</p>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '3rem', marginBottom: '0.5rem' }}>🧠</div>
              <p style={{ fontSize: '0.75rem', letterSpacing: '0.1em', textTransform: 'uppercase' }}>Consciousness</p>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '3rem', marginBottom: '0.5rem' }}>🛡️</div>
              <p style={{ fontSize: '0.75rem', letterSpacing: '0.1em', textTransform: 'uppercase' }}>Guardian</p>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
            <button style={{
              background: 'linear-gradient(to right, #7C3AED, #2563EB)',
              color: 'white',
              padding: '1rem 2rem',
              borderRadius: '0.5rem',
              border: 'none',
              fontSize: '1rem',
              cursor: 'pointer'
            }}>
              Explore MATADA
            </button>
            <button style={{
              background: 'transparent',
              color: 'white',
              padding: '1rem 2rem',
              borderRadius: '0.5rem',
              border: '1px solid rgba(255,255,255,0.2)',
              fontSize: '1rem',
              cursor: 'pointer'
            }}>
              View Products
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
