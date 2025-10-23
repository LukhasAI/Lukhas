import type { MDXComponents } from 'mdx/types'

// MDX component overrides for LUKHAS AI documentation
export function useMDXComponents(components: MDXComponents): MDXComponents {
  return {
    ...components,
    
    // Typography overrides with LUKHAS styling
    h1: ({ children }) => (
      <h1 className="text-3xl font-light text-white mb-6 tracking-tight">
        {children}
      </h1>
    ),
    h2: ({ children }) => (
      <h2 className="text-2xl font-light text-white mb-4 mt-8">
        {children}
      </h2>
    ),
    h3: ({ children }) => (
      <h3 className="text-xl font-medium text-white/90 mb-3 mt-6">
        {children}
      </h3>
    ),
    p: ({ children }) => (
      <p className="text-white/80 leading-relaxed mb-4">
        {children}
      </p>
    ),
    
    // Code blocks with LUKHAS theme
    code: ({ children }) => (
      <code className="px-1.5 py-0.5 bg-black/40 text-trinity-consciousness rounded text-sm font-mono">
        {children}
      </code>
    ),
    pre: ({ children }) => (
      <pre className="p-4 bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg overflow-x-auto mb-4">
        {children}
      </pre>
    ),
    
    // Lists with proper spacing
    ul: ({ children }) => (
      <ul className="list-disc list-inside space-y-2 mb-4 text-white/80">
        {children}
      </ul>
    ),
    ol: ({ children }) => (
      <ol className="list-decimal list-inside space-y-2 mb-4 text-white/80">
        {children}
      </ol>
    ),
    li: ({ children }) => (
      <li className="text-white/80">
        {children}
      </li>
    ),
    
    // Links with LUKHAS identity colors
    a: ({ href, children }) => (
      <a 
        href={href}
        className="text-trinity-identity hover:text-trinity-consciousness transition-colors underline decoration-trinity-identity/30"
      >
        {children}
      </a>
    ),
    
    // Blockquotes with LUKHAS styling
    blockquote: ({ children }) => (
      <blockquote className="pl-4 border-l-2 border-trinity-guardian/50 italic text-white/70 my-4">
        {children}
      </blockquote>
    ),
    
    // Tables with LUKHAS theme
    table: ({ children }) => (
      <div className="overflow-x-auto mb-4">
        <table className="min-w-full divide-y divide-white/10">
          {children}
        </table>
      </div>
    ),
    th: ({ children }) => (
      <th className="px-4 py-2 text-left text-xs font-medium text-white/60 uppercase tracking-wider bg-black/20">
        {children}
      </th>
    ),
    td: ({ children }) => (
      <td className="px-4 py-2 whitespace-nowrap text-sm text-white/80 border-t border-white/10">
        {children}
      </td>
    ),
    
    // Horizontal rule
    hr: () => (
      <hr className="my-8 border-white/10" />
    ),
    
    // Custom components for tone system
    ToneWrapper: ({ tone, children }: { tone: string; children: React.ReactNode }) => (
      <div data-tone={tone} className="mb-4">
        {children}
      </div>
    ),
    
    // Lambda symbol component
    Lambda: () => (
      <span className="text-trinity-identity" aria-label="Lambda">Λ</span>
    ),
    
    // LUKHAS brand component
    LUKHAS: () => (
      <span className="font-medium">LUKHAS AI</span>
    ),
    
    // Trinity components
    TrinityIdentity: ({ children }) => (
      <span className="text-trinity-identity">⚛️ {children}</span>
    ),
    TrinityConsciousness: ({ children }) => (
      <span className="text-trinity-consciousness">🧠 {children}</span>
    ),
    TrinityGuardian: ({ children }) => (
      <span className="text-trinity-guardian">🛡️ {children}</span>
    ),
  }
}