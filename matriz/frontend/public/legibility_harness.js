(() => {
    if (window.legibilityHarness) return;

    const bus = new EventTarget();

    function emitMetric(payload) {
        bus.dispatchEvent(new CustomEvent('metric', { detail: payload }));
        try { window.dispatchEvent(new CustomEvent('legibility-metric', { detail: payload })); } catch { }
    }

    // Minimal visual panel
    const panel = document.createElement('div');
    panel.style.cssText = `
    position:fixed;right:12px;bottom:88px;z-index:9999;
    background:rgba(0,0,0,.72);backdrop-filter:blur(12px);
    border:1px solid rgba(255,255,255,.12);border-radius:12px;
    padding:10px 12px;font:12px/1.4 ui-sans-serif,system-ui;color:#fff;min-width:220px`;
    panel.innerHTML = `<div style="opacity:.65;margin-bottom:6px;">Legibility</div>
  <div>Target: <span id="lh-target" style="opacity:.8">—</span></div>
  <div>Chamfer: <span id="lh-ch" style="opacity:.8">—</span></div>
  <div>OCR: <span id="lh-ocr" style="opacity:.8">—</span></div>`;
    panel.style.display = 'none';
    document.body.appendChild(panel);

    const $ = (id) => panel.querySelector(id);
    const show = (on) => (panel.style.display = on ? 'block' : 'none');

    async function ocrConfidence(text) {
        // Placeholder confidence
        return Math.max(0.7, Math.min(0.99, 0.85 + (Math.random() - 0.5) * 0.1));
    }

    function playStep(step) {
        if (!step || (!step.text && !step.svg)) return show(false);
        show(true);
        $('#lh-target').textContent = step.text || 'SVG';

        const start = performance.now();
        let raf;
        (function tick() {
            const t = (performance.now() - start) / 1200; // ~1.2s converge
            const chamfer = Math.max(0.02, 0.25 * Math.exp(-3 * t));
            $('#lh-ch').textContent = chamfer.toFixed(3);
            raf = requestAnimationFrame(tick);
        })();

        const hold = step?.constraints?.holdMs ?? 900;
        setTimeout(async () => {
            cancelAnimationFrame(raf);
            const ocr = await ocrConfidence(step.text || '');
            $('#lh-ocr').textContent = `${(ocr * 100).toFixed(1)}%`;
            emitMetric({
                type: 'text-step',
                target: step.text || 'SVG',
                chamfer: parseFloat($('#lh-ch').textContent || '0'),
                ocr,
            });
        }, hold + 400);
    }

    function hook() {
        const ms = window.morphScript;
        if (!ms || typeof ms.run !== 'function' || ms.__lhPatched) return false;
        const orig = ms.run.bind(ms);
        ms.run = (plan) => {
            try {
                const textStep = (plan?.timeline || []).find((s) => s.text || s.svg);
                playStep(textStep);
            } catch { }
            return orig(plan);
        };
        ms.__lhPatched = true;
        return true;
    }

    hook();
    window.addEventListener('load', hook);

    window.legibilityHarness = {
        version: '1.1.0',
        onMetric(cb) { bus.addEventListener('metric', cb); return () => bus.removeEventListener('metric', cb); },
        playStep,
    };
})();
