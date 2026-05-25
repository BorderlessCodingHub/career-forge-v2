// Career Forge — Screens 4 (Skill Graph dashboard) and 6 (Adaptive + Mentor)

// === Screen 4: Skill Graph Dashboard ===
const RoadmapScreen = ({ adaptive = false, onValidate, onMentor, mentorOpen, onCloseMentor }) => {
  const [selectedNode, setSelectedNode] = React.useState(null);

  // Build node/edge state from base, applying adaptive overrides
  const { nodes, edges } = React.useMemo(() => {
    let nodes = SKILL_NODES_BASE.map(n => ({ ...n }));
    let edges = SKILL_EDGES_BASE.map(e => ({ ...e }));
    if (adaptive) {
      // After failed REST validation:
      const rest = nodes.find(n => n.id === 'rest');
      if (rest) { rest.status = 'review'; rest.pct = 48; rest.current = false; }
      const http = nodes.find(n => n.id === 'http');
      if (http) { http.current = true; http.pct = 58; }
      // Make REST→HTTP a review loop (active dashed)
      edges = edges.map(e => {
        if (e.from === 'http' && e.to === 'rest') return { ...e, state: 'active' };
        return e;
      });
    }
    return { nodes, edges };
  }, [adaptive]);

  const summary = adaptive
    ? { eyebrow: 'Trilha recalibrada', title: 'Foque em HTTP — sua validação em REST mostrou gaps', meta: '20 min · revisão guiada', variant: 'warning' }
    : { eyebrow: 'Próxima missão', title: 'HTTP básico — métodos e status codes', meta: '30 min · seção 1 de 3', variant: 'default' };

  const validated = nodes.filter(n => n.status === 'approved').length;
  const total = nodes.length;

  return (
    <div className="dash-layout" data-screen={adaptive ? 'adaptive-state' : 'skill-graph'}>
      <div className="dash-main">
        <MissionBanner
          eyebrow={summary.eyebrow}
          title={summary.title}
          meta={summary.meta}
          variant={summary.variant}
          action={
            <button className="btn btn-primary" onClick={() => onValidate('rest')}>
              {adaptive ? 'Revisar HTTP' : 'Começar missão'} <Icon name="arrowRight" size={14} />
            </button>
          }
        />

        <div className="graph-wrap">
          <div className="graph-header">
            <div className="graph-title">
              Sua trilha · Backend Developer
              <span className="meta">{validated} validado · {total - validated} pendentes</span>
            </div>
            <div className="graph-legend">
              <div className="legend-item"><span className="legend-dot" style={{ background: 'var(--success)' }}></span>aprovado</div>
              <div className="legend-item"><span className="legend-dot" style={{ background: 'var(--accent)' }}></span>recomendado</div>
              {adaptive && <div className="legend-item"><span className="legend-dot" style={{ background: 'var(--warning)' }}></span>revisar</div>}
              <div className="legend-item"><span className="legend-dot" style={{ background: 'var(--locked)' }}></span>bloqueado</div>
            </div>
          </div>
          <SkillGraph nodes={nodes} edges={edges} selected={selectedNode} onSelect={setSelectedNode} />
        </div>
      </div>

      <aside className="dash-side">
        <div className="card side-card">
          <div className="side-card-head">
            <span className="side-card-title">Progresso</span>
            <span className="side-card-meta">backend</span>
          </div>
          <div className="progress-summary">
            <span className="progress-big">{validated}</span>
            <span className="progress-total">/{total}</span>
            <span style={{ marginLeft: 'auto', fontSize: 12, color: 'var(--success)', fontFamily: 'var(--font-mono)' }}>+1 esta semana</span>
          </div>
          <div className="progress-label-row">domínios validados pela IA</div>
          <div className="mini-bars">
            {nodes.map((n, i) => (
              <div key={i} className={`mini-bar ${n.status === 'approved' ? 'done' : n.status === 'review' ? 'warn' : n.status === 'recommended' ? 'partial' : ''}`}></div>
            ))}
          </div>
        </div>

        <div className="card side-card">
          <div className="side-card-head">
            <span className="side-card-title">Evidências recentes</span>
            <span className="side-card-meta">últimos 7 dias</span>
          </div>
          <div className="evidence-list">
            {adaptive && (
              <div className="evidence-item">
                <div className="ic" style={{ background: 'var(--warning-soft)', color: 'var(--warning)' }}>
                  <Icon name="alert" size={13} />
                </div>
                <div className="evidence-item-body">
                  <div className="evidence-item-title">APIs REST · score 48</div>
                  <div className="evidence-item-meta">marcou revisar · há 2 min</div>
                </div>
              </div>
            )}
            <div className="evidence-item success">
              <div className="ic"><Icon name="check" size={13} stroke={3} /></div>
              <div className="evidence-item-body">
                <div className="evidence-item-title">Git e GitHub · score 82</div>
                <div className="evidence-item-meta">validado · ontem · 18:42</div>
              </div>
            </div>
            <div className="evidence-item">
              <div className="ic"><Icon name="file" size={13} /></div>
              <div className="evidence-item-body">
                <div className="evidence-item-title">JavaScript base · score 71</div>
                <div className="evidence-item-meta">validado · 3 dias atrás</div>
              </div>
            </div>
          </div>
        </div>

        <button className="card mentor-cta" onClick={onMentor}>
          <div className="avatar">RT</div>
          <div className="mentor-cta-body">
            <div className="mentor-cta-name">Rafael · Mentor Borderless</div>
            <div className="mentor-cta-meta">Falar com mentor agora</div>
          </div>
          <div className="mentor-status"></div>
        </button>

        <div className="card side-card" style={{ background: 'transparent', borderStyle: 'dashed' }}>
          <div className="row" style={{ gap: 10, marginBottom: 8, color: 'var(--accent-2)' }}>
            <Icon name="sparkles" size={14} />
            <span style={{ fontSize: 12, fontWeight: 600 }}>Por que ainda não destravou?</span>
          </div>
          <div style={{ fontSize: 12, color: 'var(--text-2)', lineHeight: 1.55 }}>
            Career Forge não progride por tempo gasto. Cada domínio só vira <b style={{ color: 'var(--text)' }}>aprovado</b> depois que você prova entendimento em uma entrevista curta com a IA.
          </div>
        </div>
      </aside>

      {/* Node detail slide-over */}
      <div className={`slideover-backdrop ${selectedNode ? 'open' : ''}`} onClick={() => setSelectedNode(null)}></div>
      <div className={`slideover ${selectedNode ? 'open' : ''}`}>
        <NodeDetail
          nodeId={selectedNode}
          nodes={nodes}
          onClose={() => setSelectedNode(null)}
          onValidate={(id) => { setSelectedNode(null); onValidate(id); }}
        />
      </div>

      {/* Mentor drawer */}
      <div className={`slideover-backdrop ${mentorOpen ? 'open' : ''}`} onClick={onCloseMentor}></div>
      <div className={`slideover ${mentorOpen ? 'open' : ''}`}>
        <MentorDrawer onClose={onCloseMentor} adaptive={adaptive} />
      </div>
    </div>
  );
};

// === Mentor Drawer ===
const MentorDrawer = ({ onClose, adaptive }) => {
  const [draft, setDraft] = React.useState('');
  const [messages, setMessages] = React.useState([
    { from: 'user', t: 'agora', text: 'Tenho 40 minutos hoje. O que estudo?' },
    {
      from: 'ai', t: 'agora',
      plan: true,
      intro: 'Considerando sua validação em APIs REST (score 48 · marcou revisar), seu maior gap é distinguir método HTTP de rota. Plano de 40 minutos:',
      callout: { tag: 'Por quê?', text: 'Você escreveu "POST /users = criar usuário" como se método e rota fossem a mesma coisa. Sem isso firme, REST vai falhar de novo.' },
      steps: [
        { title: 'Métodos HTTP — GET, POST, PUT, PATCH, DELETE', meta: '15 min · leitura + 3 exemplos práticos' },
        { title: 'Status codes — 2xx, 4xx, 5xx', meta: '10 min · vídeo curto + quiz auto-corrigido' },
        { title: 'Mini-exercício no terminal: 4 requests com curl', meta: '15 min · você executa, IA confere' },
      ],
    },
  ]);

  const send = () => {
    if (!draft.trim()) return;
    setMessages(m => [...m, { from: 'user', t: 'agora', text: draft }]);
    setDraft('');
    setTimeout(() => {
      setMessages(m => [...m, { from: 'ai', t: 'agora', text: 'Anotado. Posso ajustar o plano se você quiser focar só nos métodos, ou se preferir começar pelo exercício prático e revisar a teoria depois.' }]);
    }, 900);
  };

  return (
    <div className="mentor-drawer">
      <div className="mentor-drawer-head">
        <div className="mentor-drawer-title-wrap">
          <div className="mentor-drawer-avatar">RT</div>
          <div>
            <div className="mentor-drawer-title">Mentor contextual</div>
            <div className="mentor-drawer-sub">conhece sua trilha · respondendo</div>
          </div>
        </div>
        <button className="slideover-close" onClick={onClose}><Icon name="x" size={18} /></button>
      </div>

      <div className="mentor-stream">
        {messages.map((m, i) => {
          if (m.plan) {
            return (
              <Bubble key={i} from="ai" time={m.t}>
                <div>{m.intro}</div>
                <ol className="plan-list">
                  {m.steps.map((s, j) => (
                    <li key={j}>
                      <div className="step-num">{j + 1}</div>
                      <div className="step-body">
                        <div className="step-title">{s.title}</div>
                        <div className="step-meta">{s.meta}</div>
                      </div>
                    </li>
                  ))}
                </ol>
                <div className="ref-callout">
                  <b>{m.callout.tag}</b> {m.callout.text}
                </div>
              </Bubble>
            );
          }
          return <Bubble key={i} from={m.from} time={m.t}>{m.text}</Bubble>;
        })}
      </div>

      <div className="mentor-input-row">
        <input
          className="chat-input"
          placeholder="Pergunte algo sobre sua trilha..."
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => { if (e.key === 'Enter') send(); }}
        />
        <button className="send-btn" onClick={send} disabled={!draft.trim()}><Icon name="send" size={16} /></button>
      </div>
    </div>
  );
};

Object.assign(window, { RoadmapScreen, MentorDrawer });
