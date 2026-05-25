// Career Forge — Live Roadmap Forge screen + Reveal frame

const FORGE_SCRIPT = [
  { delay: 0,    kind: 'thought',  label: 'Lendo seu diagn\u00f3stico inicial',
    detail: 'perfil = iniciante_js \u00b7 2 fortes \u00b7 3 lacunas \u00b7 motiv = space_tech' },
  { delay: 700,  kind: 'query',    label: 'Cruzando com trilhas validadas',
    detail: 'SELECT trail FROM corpus WHERE role = "backend" \u2192 2.847 resultados' },
  { delay: 1500, kind: 'artifact', label: 'Sinal forte: JavaScript base',
    detail: 'pode pular fundamentos de sintaxe', node: 'js' },
  { delay: 2200, kind: 'artifact', label: 'Sinal forte: Git e GitHub',
    detail: 'versionamento OK \u00b7 pr\u00e9-validado pela evid\u00eancia anterior', node: 'git' },
  { delay: 3000, kind: 'decision', label: 'Princ\u00edpio: maestria > velocidade',
    detail: 'Alpha School \u00b7 progress\u00e3o por evid\u00eancia, n\u00e3o por checkbox' },
  { delay: 3700, kind: 'artifact', label: 'Lacuna cr\u00edtica: HTTP b\u00e1sico',
    detail: 'priorizando como pr\u00f3ximo n\u00f3 da cadeia', node: 'http' },
  { delay: 4400, kind: 'thought',  label: 'Mapeando depend\u00eancias',
    detail: 'HTTP \u2192 REST \u2192 Auth \u00b7 cadeia n\u00e3o-paraleliz\u00e1vel' },
  { delay: 5100, kind: 'artifact', label: 'Adicionando: APIs REST',
    detail: 'desbloqueia 60% dos roles backend pleiteados', node: 'rest' },
  { delay: 5800, kind: 'artifact', label: 'Adicionando: Autentica\u00e7\u00e3o JWT',
    detail: 'pr\u00e9-requisito de qualquer API com usu\u00e1rios', node: 'auth' },
  { delay: 6500, kind: 'thought',  label: 'Persist\u00eancia pode rodar em paralelo',
    detail: 'banco relacional n\u00e3o bloqueia o caminho cr\u00edtico HTTP\u2192REST' },
  { delay: 7200, kind: 'artifact', label: 'Adicionando: Banco relacional',
    detail: 'paralela a HTTP \u00b7 destrava antes do projeto final', node: 'db' },
  { delay: 8000, kind: 'decision', label: 'Calibrando para space tech',
    detail: 'projeto final orientado a APIs robustas com testes' },
  { delay: 8700, kind: 'artifact', label: 'Projeto final: API CRUD',
    detail: 'integra Git \u00b7 HTTP \u00b7 REST \u00b7 Auth \u00b7 Banco', node: 'final' },
  { delay: 9500, kind: 'complete', label: 'Trilha personalizada pronta',
    detail: '7 dom\u00ednios \u00b7 1 pr\u00e9-validado \u00b7 estimativa: 6\u20138 meses' },
];

const KIND_GLYPH = {
  thought:  '~',
  query:    '$',
  artifact: '+',
  decision: '\u00a7',
  complete: '\u2713',
};
const KIND_LABEL = {
  thought:  'pensando',
  query:    'consulta',
  artifact: 'adicionado',
  decision: 'decis\u00e3o',
  complete: 'pronto',
};

const fmtElapsed = (ms) => {
  const s = (ms / 1000).toFixed(1);
  return `+${s}s`;
};

// === Forge Screen (streaming) ===
const ForgeScreen = ({ onReveal }) => {
  const [phase, setPhase] = React.useState('forge'); // 'forge' | 'reveal'
  const [tick, setTick] = React.useState(0);
  const [items, setItems] = React.useState([]);
  const [revealed, setRevealed] = React.useState(new Set());
  const [done, setDone] = React.useState(false);
  const [skipping, setSkipping] = React.useState(false);
  const streamRef = React.useRef(null);

  // Elapsed counter (tabular)
  React.useEffect(() => {
    if (done) return;
    const id = setInterval(() => setTick(t => t + 1), 100);
    return () => clearInterval(id);
  }, [done]);

  // Drive the script
  React.useEffect(() => {
    const timers = [];
    FORGE_SCRIPT.forEach((step, idx) => {
      timers.push(setTimeout(() => {
        setItems(prev => [...prev, { ...step, idx, time: step.delay }]);
        if (step.node) {
          setRevealed(prev => {
            const next = new Set(prev);
            next.add(step.node);
            return next;
          });
        }
        if (idx === FORGE_SCRIPT.length - 1) {
          setTimeout(() => setDone(true), 300);
        }
      }, step.delay + 350));
    });
    return () => timers.forEach(clearTimeout);
  }, []);

  // Auto-scroll timeline
  React.useEffect(() => {
    if (streamRef.current) {
      streamRef.current.scrollTop = streamRef.current.scrollHeight;
    }
  }, [items.length]);

  const skip = () => {
    setSkipping(true);
    setItems(FORGE_SCRIPT.map((s, idx) => ({ ...s, idx, time: s.delay })));
    setRevealed(new Set(SKILL_NODES_BASE.map(n => n.id)));
    setTimeout(() => { setDone(true); }, 200);
  };

  const goReveal = () => setPhase('reveal');

  if (phase === 'reveal') {
    return <RevealFrame onEnter={onReveal} onReplay={() => {
      setItems([]); setRevealed(new Set()); setDone(false); setTick(0); setPhase('forge');
    }} />;
  }

  const elapsed = skipping ? 9800 : Math.min(tick * 100, done ? items[items.length - 1]?.time + 800 : 99000);
  const nodesDone = revealed.size;
  const totalNodes = SKILL_NODES_BASE.length;
  const tokensAnalyzed = 1200 + items.length * 380 + (tick % 7);

  return (
    <div className="forge-layout" data-screen="forge">
      <div className="forge-banner">
        <div className="forge-banner-left">
          <div className="forge-bolt"><Icon name="sparkles" size={18} /></div>
          <div>
            <div className="forge-banner-eyebrow">Forge \u00b7 agente em execu\u00e7\u00e3o</div>
            <div className="forge-banner-title">Forjando sua trilha personalizada</div>
          </div>
        </div>
        <div className="forge-banner-meta">
          <span>elapsed <b><span className="forge-counter-num">{(elapsed / 1000).toFixed(1)}s</span></b></span>
          <span className="sep">\u00b7</span>
          <span>dom\u00ednios <b><span className="forge-counter-num">{nodesDone}</span>/{totalNodes}</b></span>
          <span className="sep">\u00b7</span>
          <span>tokens <b><span className="forge-counter-num">{tokensAnalyzed.toLocaleString('pt-BR')}</span></b></span>
        </div>
      </div>

      {/* LEFT: streaming reasoning timeline */}
      <div className="forge-panel">
        <div className="forge-panel-head">
          <div className="forge-panel-title">
            <Icon name="sparkles" size={12} className="ic" />
            Racioc\u00ednio do agente
          </div>
          <div className="forge-panel-meta">{items.length} de {FORGE_SCRIPT.length} passos</div>
        </div>
        <div className="forge-stream" ref={streamRef}>
          {items.map((it, i) => {
            const isLast = i === items.length - 1;
            return (
              <div key={i} className={`forge-item ${it.kind} ${isLast && !done ? 'active' : ''} ${!isLast && i < items.length - 3 ? 'dim' : ''}`}>
                <div className="forge-item-glyph">{KIND_GLYPH[it.kind]}</div>
                <div className="forge-item-body">
                  <div className="forge-item-head">
                    <span className="forge-item-kind">{KIND_LABEL[it.kind]}</span>
                    <span className="forge-item-elapsed">{fmtElapsed(it.time)}</span>
                  </div>
                  <div className="forge-item-label">{it.label}</div>
                  <div className="forge-item-detail">&gt; {it.detail}</div>
                </div>
              </div>
            );
          })}
          {!done && (
            <div className="forge-stream-tail">
              <span className="forge-cursor"></span>
              <span>analisando depend\u00eancias\u2026</span>
            </div>
          )}
          {done && !skipping && (
            <div className="forge-stream-tail" style={{ color: 'var(--success)' }}>
              <Icon name="check" size={12} stroke={3} />
              <span>execu\u00e7\u00e3o conclu\u00edda \u00b7 trilha pronta para revelar</span>
            </div>
          )}
        </div>
      </div>

      {/* RIGHT: graph filling in */}
      <div className="forge-panel">
        <div className="forge-panel-head">
          <div className="forge-panel-title">
            <Icon name="boxes" size={12} className="ic" />
            Skill graph em constru\u00e7\u00e3o
          </div>
          <div className="forge-panel-meta">backend developer \u00b7 v1</div>
        </div>
        <div className="forge-graph-wrap">
          {!done && <><div className="forge-scan"></div><div className="forge-scan-line"></div></>}
          <ForgeGraph nodes={SKILL_NODES_BASE} edges={SKILL_EDGES_BASE} revealed={revealed} />
        </div>
        <div className="forge-graph-footer">
          <div className="forge-graph-footer-meta">
            <span>n\u00f3s <b>{nodesDone}/{totalNodes}</b></span>
            <span>arestas <b>{SKILL_EDGES_BASE.filter(e => revealed.has(e.from) && revealed.has(e.to)).length}/{SKILL_EDGES_BASE.length}</b></span>
            <span>checkpoint <b>{done ? 'final' : 'streaming'}</b></span>
          </div>
          <div className="forge-actions">
            {!done ? (
              <button className="forge-skip" onClick={skip}>pular \u00bb</button>
            ) : (
              <button className="btn btn-primary" onClick={goReveal}>
                Revelar trilha completa <Icon name="arrowRight" size={14} />
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// === Reveal Frame ===
const RevealFrame = ({ onEnter, onReplay }) => {
  const allRevealed = React.useMemo(() => new Set(SKILL_NODES_BASE.map(n => n.id)), []);
  return (
    <div className="reveal-frame" data-screen="forge-reveal">
      <div className="reveal-head">
        <div className="reveal-eyebrow">
          <span className="dot"></span>
          Trilha gerada \u00b7 9.8s \u00b7 v1
        </div>
        <h1 className="reveal-h1">
          Sua trilha viva est\u00e1 <span className="accent">pronta</span>.
        </h1>
        <p className="reveal-sub">
          7 dom\u00ednios mapeados, conectados por evid\u00eancia. Ela vai recalibrar a cada valida\u00e7\u00e3o.
        </p>
      </div>

      <div className="reveal-stats">
        <div className="reveal-stat">
          <div className="reveal-stat-num accent">7</div>
          <div className="reveal-stat-label">dom\u00ednios</div>
        </div>
        <div className="reveal-stat">
          <div className="reveal-stat-num success">1</div>
          <div className="reveal-stat-label">pr\u00e9-validado</div>
        </div>
        <div className="reveal-stat">
          <div className="reveal-stat-num">2</div>
          <div className="reveal-stat-label">recomendados</div>
        </div>
        <div className="reveal-stat">
          <div className="reveal-stat-num">6\u20138</div>
          <div className="reveal-stat-label">meses estimados</div>
        </div>
        <div className="reveal-stat">
          <div className="reveal-stat-num">21</div>
          <div className="reveal-stat-label">evid\u00eancias exigidas</div>
        </div>
      </div>

      <div className="reveal-graph-wrap">
        <div className="reveal-sweep"></div>
        <ForgeGraph
          nodes={SKILL_NODES_BASE}
          edges={SKILL_EDGES_BASE}
          revealed={allRevealed}
          revealClass="reveal-glow"
        />
      </div>

      <div className="reveal-foot">
        <div className="reveal-foot-note">
          <Icon name="sparkles" size={12} style={{ verticalAlign: '-2px', marginRight: 6 }} />
          Toque em qualquer n\u00f3 na pr\u00f3xima tela para ver outcomes e iniciar a valida\u00e7\u00e3o.
        </div>
        <div className="reveal-foot-actions">
          <button className="btn btn-soft" onClick={onReplay}>
            <Icon name="refresh" size={14} /> Replay
          </button>
          <button className="btn btn-primary btn-lg" onClick={onEnter}>
            Entrar na trilha <Icon name="arrowRight" size={14} />
          </button>
        </div>
      </div>
    </div>
  );
};

Object.assign(window, { ForgeScreen, RevealFrame });
