import React, { useState, useEffect } from 'react'
import { buildMorphScriptPlan, runMorphScriptPlan, extractIntentFromMessage } from '../lib/morphScript'

// --- end heuristic + hook ---

// Supported shapes the runtime can render directly
const SUPPORTED_SHAPES = new Set(['sphere', 'torus', 'cube', 'consciousness'])

// Safety keywords – tone → safety cue
const VIOLENCE_WORDS = /(kill|hurt|attack|violence|explode|blood|murder|assault|shoot|stab|rage)/i

// Detect a likely noun request (single word, 3+ letters)
function detectUnknownNoun(msg: string): string | null {
    // Try quoted first: "cat" → cat
    const q = /"([a-zA-Z][a-zA-Z\s\-]{2,})"/.exec(msg)
    if (q?.[1]) {
        const word = q[1].trim()
        return SUPPORTED_SHAPES.has(word.toLowerCase()) ? null : word
    }
    // Then any noun-ish token after an action verb
    const m = /(make|turn|render|form|shape|draw)\s+([a-zA-Z][a-zA-Z\-]{2,})/i.exec(msg)
    if (m?.[2]) {
        const word = m[2].toLowerCase()
        return SUPPORTED_SHAPES.has(word) ? null : m[2]
    }
    return null
}

// Queue entry type
type QueuedShape = { noun: string; ts: number }

// Truthful fallback for unsupported shapes: render glyph text first and queue noun
const _oldExtract = extractIntentFromMessage;
// @ts-ignore allow reassignment of imported symbol in this plan file context
extractIntentFromMessage = function (msg: string) {
    const intent = _oldExtract(msg)
    if (!intent.shape && !intent.text) {
        const noun = detectUnknownNoun(msg)
        if (noun) {
            intent.text = noun.toUpperCase()
            // Inform ExperiencePage via window event for queueing
            try { window.dispatchEvent(new CustomEvent('lukhas-queue-shape', { detail: { noun } })) } catch { }
        }
    }
    // Special-case: cat stays nice :)
    if (!intent.shape && !intent.text && /\bcat(s)?\b/i.test(msg)) intent.text = 'CAT'
    return intent
}

// Sentiment + keyword color/tempo helpers
const POSITIVE_WORDS = /(love|great|awesome|amazing|calm|peace|serene|happy|nice|cool|excited|fast|energetic|bright)/i
const NEGATIVE_WORDS = /(sad|angry|slow|dark|bad|worse|worst|tired|heavy|cold|gloom|dull)/i
function sentimentScore(msg: string): number {
    const pos = msg.match(new RegExp(POSITIVE_WORDS, 'gi'))?.length || 0
    const neg = msg.match(new RegExp(NEGATIVE_WORDS, 'gi'))?.length || 0
    return Math.tanh((pos - neg) * 0.8) // [-1,1]
}
function mapKeywordsToColorTempo(msg: string): { color?: string; tempo?: number } {
    const m = msg.toLowerCase()
    if (/love|heart|romance|passion/.test(m)) return { color: '#ec4899', tempo: 1.15 }
    if (/calm|serene|breathe|meditat/.test(m)) return { color: '#38bdf8', tempo: 0.75 }
    if (/focus|clarity|clean|minimal/.test(m)) return { color: '#e5e7eb', tempo: 0.9 }
    if (/energy|hype|party|neon|glow|excited|fast/.test(m)) return { color: '#a78bfa', tempo: 1.25 }
    if (/nature|grow|heal|guardian|safe|trust/.test(m)) return { color: '#22c55e', tempo: 0.95 }
    if (/torus|donut/.test(m)) return { color: '#60a5fa', tempo: 1.05 }
    if (/cube|box/.test(m)) return { color: '#93c5fd', tempo: 0.9 }
    if (/sphere|orb|ball/.test(m)) return { color: '#e5e7eb', tempo: 1.0 }
    if (/helix|spiral|conscious/.test(m)) return { color: '#8b5cf6', tempo: 1.1 }
    return {}
}

// Morph progress estimation + bar state
function estimatePlanDuration(plan: any) {
    const tl = plan?.timeline || []
    let total = 0
    for (const step of tl) {
        if (step.text || step.svg) total += (step.constraints?.holdMs || 900) + 1200
        else total += 800
    }
    return Math.max(total, 1200)
}

function ExperiencePage() {
    // ... other useState hooks ...
    const [lastPlan, setLastPlan] = useState < any | null > (null)
    const [modStats, setModStats] = useState < { sentiment: number; tempo: number; speed: number } > ({ sentiment: 0, tempo: 1, speed: 0.02 })
    const [morphBar, setMorphBar] = useState < { active: boolean; value: number; label: string } > ({ active: false, value: 0, label: 'Morphing…' })

    const [queuedShapes, setQueuedShapes] = useState < QueuedShape[] > ([])
    const [showQueue, setShowQueue] = useState(false)
    const [truthNotice, setTruthNotice] = useState < { active: boolean; noun?: string } > ({ active: false })
    const [safetyActive, setSafetyActive] = useState(false)
    const [replyEst, setReplyEst] = useState < { tokens: number; costUSD: number } | null > (null)

    useEffect(() => {
        function onQueue(e: any) {
            const noun = e?.detail?.noun
            if (!noun) return
            setQueuedShapes(prev => [{ noun, ts: Date.now() }, ...prev].slice(0, 20))
            // show truthful prompt once per noun
            setTruthNotice({ active: true, noun })
        }
        window.addEventListener('lukhas-queue-shape', onQueue)
        return () => window.removeEventListener('lukhas-queue-shape', onQueue)
    }, [])

    function activateGuardianCalm() {
        setSafetyActive(true)
        // calm palette + tempo
        handleConfigChange('accentColor', '#38bdf8')
        handleConfigChange('tempo', 0.75)
        handleConfigChange('morphSpeed', 0.015)
        setTimeout(() => setSafetyActive(false), 2000)
    }

    function estimateTokensAndCost(text: string, model: string = 'lukhas'): { tokens: number; costUSD: number } {
        // ultra-simple heuristic: ~4 chars per token + base overhead
        const tokens = Math.max(60, Math.ceil(text.length / 4) + 80)
        // soft placeholder costs per 1K tokens; refined when real pricing is wired
        const perK: Record<string, number> = { 'gpt-4o': 0.005, 'gpt-4o-mini': 0.0015, 'gpt-4-turbo': 0.01, lukhas: 0.0 }
        const rate = perK[model] ?? 0.005
        const costUSD = +(tokens / 1000 * rate).toFixed(4)
        return { tokens, costUSD }
    }

    // ... other handlers and effects ...

    function playMorphProgress(plan: any) {
        const total = estimatePlanDuration(plan)
        const start = performance.now()
        setMorphBar({ active: true, value: 0, label: 'Morphing…' })
        function tick() {
            const v = Math.min(1, (performance.now() - start) / total)
            setMorphBar({ active: true, value: v, label: v < 1 ? 'Morphing…' : 'Complete' })
            if (v < 1) requestAnimationFrame(tick)
            else setTimeout(() => setMorphBar({ active: false, value: 1, label: 'Complete' }), 600)
        }
        requestAnimationFrame(tick)
    }

    useEffect(() => {
        if (typeof window === 'undefined') return
        if ((window as any).legibilityHarness) return
        const s = document.createElement('script')
        s.src = '/legibility_harness.js'
        s.async = true
        s.onload = () => console.log('[Legibility] harness loaded')
        document.body.appendChild(s)
        return () => { try { document.body.removeChild(s) } catch { } }
    }, [])

    function handleSendMessage(message: string) {
        // ... existing code ...
        setRightPanelOpen(true)

        const intent = extractIntentFromMessage(message)

        // Safety by design: cap energy if very negative or violent language
        const violent = VIOLENCE_WORDS.test(message)
        const sent = sentimentScore(message)
        const danger = violent || sent < -0.6
        if (danger) {
            activateGuardianCalm()
        }

        // Estimate tokens & soft cost (for UI)
        try { setReplyEst(estimateTokensAndCost(message, (config?.selectedModel || 'lukhas'))) } catch { }

        // Sentiment → morph speed (safety-capped)
        const s = sentimentScore(message)
        const baseSpeed = config.morphSpeed ?? 0.02
        let effectiveSpeed = Math.min(0.1, Math.max(0.005, baseSpeed * (1 + s * 0.5)))
        if (danger) effectiveSpeed = Math.min(effectiveSpeed, 0.018)
        handleConfigChange('morphSpeed', effectiveSpeed)

        // Keyword → color/tempo
        const kt = mapKeywordsToColorTempo(message)
        if (kt.color) handleConfigChange('accentColor', kt.color)
        if (kt.tempo) handleConfigChange('tempo', kt.tempo)

        if (danger) {
            handleConfigChange('accentColor', '#38bdf8')
            handleConfigChange('tempo', Math.min(0.9, (kt.tempo ?? 1)))
        }

        setModStats({ sentiment: s, tempo: kt.tempo ?? (config.tempo ?? 1), speed: effectiveSpeed })

        if (intent.shape) handleConfigChange('shape', intent.shape)

        try {
            const plan = buildMorphScriptPlan(intent, config, effectiveSpeed)
            setLastPlan(plan)
            playMorphProgress(plan)
            runMorphScriptPlan(plan)
        } catch (e) {
            console.warn('Failed to run MorphScript plan:', e)
        }
    }

    return (
        <main>
            <div className="fixed left-1/2 -translate-x-1/2 top-16 z-40 flex items-center gap-2">
                <button onClick={activateGuardianCalm} className={`px-3 py-2 text-xs rounded-md border ${safetyActive ? 'bg-cyan-600/30 border-cyan-400/30' : 'bg-white/5 border-white/10 hover:bg-white/10'}`}>Instant Calm</button>
                <button onClick={() => setShowQueue(v => !v)} className="px-3 py-2 text-xs rounded-md bg-white/5 border border-white/10 hover:bg-white/10">
                    Queued shapes <span className="ml-1 px-1.5 py-0.5 text-[10px] rounded bg-white/10">{queuedShapes.length}</span>
                </button>
            </div>

            {/* ... existing JSX ... */}

            {morphBar.active && (
                <div className="fixed left-1/2 -translate-x-1/2 bottom-6 z-50 w-[min(560px,90vw)]">
                    <div className="mb-1 text-center text-[11px] text-white/70">
                        {morphBar.label} {Math.round(morphBar.value * 100)}%
                        {replyEst && (
                            <span className="ml-2 text-white/50">· est ${replyEst.costUSD.toFixed(3)} / {replyEst.tokens} tok</span>
                        )}
                    </div>
                    <div className="h-2 rounded-full bg-white/10 overflow-hidden border border-white/15">
                        <div className="h-full bg-gradient-to-r from-purple-500 via-blue-500 to-cyan-400" style={{ width: `${Math.round(morphBar.value * 100)}%` }} />
                    </div>
                </div>
            )}

            {showQueue && (
                <div className="fixed right-3 top-20 z-40 w-64 rounded-lg bg-black/70 backdrop-blur-xl border border-white/10 p-3">
                    <div className="text-xs text-white/60 mb-2">Queued Shapes</div>
                    <ul className="space-y-1 max-h-56 overflow-y-auto">
                        {queuedShapes.map((q, i) => (
                            <li key={q.ts + ':' + i} className="text-[11px] text-white/70 flex items-center justify-between">
                                <span>{q.noun}</span>
                                <span className="text-white/30">{new Date(q.ts).toLocaleTimeString()}</span>
                            </li>
                        ))}
                        {queuedShapes.length === 0 && <li className="text-[11px] text-white/40">Nothing queued yet.</li>}
                    </ul>
                </div>
            )}

            {/* ... existing JSX ... */}

            {/* Dev: Replay last MorphScript plan */}
            <button
                onClick={() => { if (lastPlan) runMorphScriptPlan(lastPlan) }}
                className="ml-3 px-3 py-2 rounded-md text-xs font-medium bg-white/5 border border-white/10 hover:bg-white/10"
                title="Replay last plan"
            >
                Play Plan
            </button>

            <div className="ml-3 px-3 py-2 rounded-md text-xs bg-white/5 border border-white/10 text-white/70">
                <span className="mr-3">Sent {modStats.sentiment >= 0 ? '+' : ''}{modStats.sentiment.toFixed(2)}</span>
                <span className="mr-3">Tempo {modStats.tempo.toFixed(2)}x</span>
                <span>Speed {modStats.speed.toFixed(3)}</span>
            </div>

            {truthNotice.active && (
                <div className="fixed left-1/2 -translate-x-1/2 bottom-24 z-50 w-[min(640px,92vw)] p-3 rounded-xl bg-black/70 backdrop-blur-xl border border-white/10">
                    <div className="text-sm text-white/90">That shape isn’t in my library yet.</div>
                    <div className="mt-1 text-[11px] text-white/60">Choose how to proceed for “{truthNotice.noun}”:</div>
                    <div className="mt-3 flex flex-wrap gap-2">
                        <button className="px-3 py-1.5 text-xs rounded-md bg-white/10 border border-white/15 hover:bg-white/15" onClick={() => setTruthNotice({ active: false })}>Render as GLYPH</button>
                        <button className="px-3 py-1.5 text-xs rounded-md bg-white/10 border border-white/15 hover:bg-white/15" onClick={() => { handleConfigChange('shape', 'sphere'); setTruthNotice({ active: false }) }}>Approximate (simple form)</button>
                        <button className="px-3 py-1.5 text-xs rounded-md bg-white/10 border border-white/15 hover:bg-white/15" onClick={() => setTruthNotice({ active: false })}>Queue it (keep motion)</button>
                    </div>
                </div>
            )}

        </main>
    )
}

{/* Dev: Replay last MorphScript plan */ }
<button
  onClick={() => { if (lastPlan) runMorphScriptPlan(lastPlan) }}
  className="ml-3 px-3 py-2 rounded-md text-xs font-medium bg-white/5 border border-white/10 hover:bg-white/10"
  title="Replay last plan"
>
  Play Plan
</button>

<div className="ml-3 px-3 py-2 rounded-md text-xs bg-white/5 border border-white/10 text-white/70">
  <span className="mr-3">Sent {modStats.sentiment >= 0 ? '+' : ''}{modStats.sentiment.toFixed(2)}</span>
  <span className="mr-3">Tempo {modStats.tempo.toFixed(2)}x</span>
  <span>Speed {modStats.speed.toFixed(3)}</span>
</div>


// components/chat-interface.tsx

function threeLayerTone(base: string, hint?: string) {
    const poetic = `${base}`
    const friendly = hint ? `${hint}` : 'Say the word — I’ll shape the field to match.'
    const academic = 'Legibility and convergence are prioritized; complex silhouettes are approximated before true assets are added.'
    return `• Poetic: ${poetic}\n• Friendly: ${friendly}\n• Insight: ${academic}`
}

function generateLocalReply(txt: string): string {
    const t = txt.toLowerCase()
    // Known shapes
    if (t.match(/\btorus|donut\b/)) return threeLayerTone('A ring awakens; particles settle into an endless loop.', 'Switching to a torus now.')
    if (t.match(/\bcube|box\b/)) return threeLayerTone('Structure condenses into six quiet planes.', 'Forming a cube.')
    if (t.match(/\bsphere|orb|ball\b/)) return threeLayerTone('Symmetry blooms into a calm orb.', 'Centering into a sphere.')
    if (t.match(/\bhelix|spiral\b/)) return threeLayerTone('A spiral climbs; pitch matches your intent.', 'Evolving into a spiral.')
    if (t.match(/\bheart\b/)) return threeLayerTone('Warmth collects into a soft heartfield.', 'Shaping into a heart-like flow.')
    // Text
    if (t.match(/"([^"]+)"/) || t.includes('text:')) return threeLayerTone('Your words crystallize as a glyph.', 'Rendering your text and holding for legibility.')
    // Honest fallback for unknown shapes
    const asksShape = /\b(make|turn|render|form|shape)\b/.test(t)
    const mentionsNoun = /\b([a-z]{3,})\b/.test(t)
    const known = /(torus|donut|cube|box|sphere|orb|ball|helix|spiral|heart|conscious)/
    if (asksShape && mentionsNoun && !known.test(t)) {
        return threeLayerTone('I don’t have that silhouette yet.', 'Shall I render the word as a glyph first, or would you like a simple approximation?')
    }
    // General personality
    return threeLayerTone('Understood. The field is listening.', 'Ask for a shape or say a word in quotes to see it drawn in particles.')
}

// In setTimeout reply simulation:
content: generateLocalReply(userMessage.content),

    // components/experience-sidebar.tsx

    {/* Provider Badges */ }
    < div className = "mb-3 flex items-center gap-2" >
    {
        ['openai', 'anthropic', 'google', 'perplexity'].map((p) => {
            const active = !!apiKeys[p as keyof typeof apiKeys]
            return (
                <span key={p} className={`px-2 py-1 text-[10px] rounded-md border ${active ? 'bg-white/10 border-white/20 text-white/80' : 'bg-white/[0.02] border-white/10 text-white/30'}`}>
                    {p}
                </span>
            )
        })
    }
</div >

    {/* Universal Key (Auto-detect) */ }
    < div className = "mb-4 p-3 rounded-lg bg-white/5 border border-white/10" >
  <label className="text-xs font-medium text-white/60 uppercase tracking-wider">Paste Any API Key</label>
  <div className="mt-2 flex gap-2">
    <input id="universal-key" type="password" placeholder="Paste key (OpenAI, Anthropic, Google, Perplexity)" className="flex-1 px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-xs text-white placeholder-white/30 focus:outline-none focus:border-white/20 focus:bg-white/10" />
    <button
      type="button"
      className="px-3 py-2 text-xs rounded-md bg-white/10 hover:bg-white/20 border border-white/10"
      onClick={() => {
        const el = document.getElementById('universal-key') as HTMLInputElement | null
        if (!el || !el.value) return
        const k = el.value.trim()
        let provider: keyof typeof apiKeys | null = null
        if (/^sk-/.test(k)) provider = 'openai'
        else if (/^sk-ant-/.test(k)) provider = 'anthropic'
        else if (/^AIza/.test(k) || /^AI[a-zA-Z]/.test(k)) provider = 'google'
        else if (/^pplx-/.test(k)) provider = 'perplexity'
        if (provider) { onApiKeyChange(provider, k); el.value = '' }
        else alert('Could not detect provider. Please paste the key into the correct field below.')
      }}
    >
      Detect → Assign
    </button>
  </div>
  <p className="mt-2 text-[10px] text-white/40">Keys stay on your device. Encrypt to a GLYPH to reuse safely.</p>
</div >

    {/* Security & GLYPH */ }
    < div className = "mt-3 p-3 rounded-lg bg-white/5 border border-white/10" >
  <div className="text-xs text-white/70 font-medium">Security & GLYPH</div>
  <div className="mt-1 text-[11px] text-white/60">Keys stay on your device. Click <em>Encrypt → GLYPH</em> to turn a key into a short token like <code>Λ:openai:…</code> you can paste later.</div>
  <details className="mt-2">
    <summary className="text-[11px] text-white/50 cursor-pointer">How do I use or share a GLYPH?</summary>
    <ul className="mt-2 list-disc pl-4 text-[11px] text-white/50">
      <li>Paste the GLYPH where a key is requested — we decode it locally.</li>
      <li>Do not post GLYPHs publicly; treat them like keys.</li>
      <li>You can revoke a GLYPH by deleting it from this device and rotating your provider key.</li>
    </ul>
  </details>
</div >

    {/* Optional Sign in stub */ }
    < div className = "mb-3" >
  <a href="/api/auth/signin" className="px-3 py-2 text-xs rounded-md bg-white/5 border border-white/10 hover:bg-white/10">Sign in</a>
  <span className="ml-2 text-[10px] text-white/40">(Optional) Enables tiers and synced settings</span>
</div >

/*
 CEO Guardrails implemented in this plan file:
 1) Truthful prompts for unsupported shapes (glyph/approx/queue) + queued-shapes badge.
 2) Safety-by-design: cap energy on negative/violent prompts; Instant Calm button.
 3) Model UX signal: one field for keys lives in sidebar; here we surface soft per-reply cost next to progress.
 4) Legibility-first: harness panel supported; scaffold ready to log anonymized metrics on opt-in.
*/
