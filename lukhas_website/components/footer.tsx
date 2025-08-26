export default function Footer() {
  return (
    <footer className="mt-24 border-t border-white/10 bg-black/30">
      <div className="mx-auto w-full max-w-screen-2xl px-6 md:px-10 lg:px-14 py-10">
        <div className="flex flex-col items-center gap-3 text-center">
          <div className="text-[11px] tracking-[0.18em] text-white/50 uppercase">LUKHΛS</div>
          <nav className="flex flex-wrap items-center justify-center gap-x-5 gap-y-2 text-[12px] text-white/60">
            <a className="hover:text-white/80" href="/products">Products</a>
            <a className="hover:text-white/80" href="/technology">Technology</a>
            <a className="hover:text-white/80" href="/pricing">Pricing</a>
            <a className="hover:text-white/80" href="/docs">Docs</a>
            <a className="hover:text-white/80" href="/privacy">Privacy</a>
            <a className="hover:text-white/80" href="/terms">Terms</a>
            <a className="hover:text-white/80" href="/compliance">Compliance</a>
          </nav>
          <div className="text-[11px] text-white/40">
            © {new Date().getFullYear()} LUKHΛS AI. Building Consciousness You Can Trust.
          </div>
        </div>
      </div>
    </footer>
  )
}
