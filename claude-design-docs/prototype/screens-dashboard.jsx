// Career Forge — Artifact mode roadmap (steady state) + adaptive variant

const RoadmapScreen = ({ mode = 'artifact', adaptive = false, onValidate, onMentor, mentorOpen, onCloseMentor }) => {
  const [selectedNode, setSelectedNode] = React.useState(null);

  const { nodes, edges } = React.useMemo(() => {
    let nodes = SKILL_NODES_BASE.map(n => ({ ...n }));
    let edges = SKILL_EDGES_BASE.map(e => ({ ...e }));
    if (adaptive) {
      const rest = nodes.find(n => n.id === 'rest');
      if (rest) { rest.status = 'review'; rest.pct = 48; rest.current = false; }
      const http = nodes.find(n => n.id === 'http');
      if (http) { http.current = true; http.pct = 58; }
      edges = edges.map(e => {
        if (e.from === 'http' && e.to === 'rest') return { ...e, state: 'active' };
        if (e.from === 'js' && e.to === 'git') return { ...e, state: 'done' };
        if (e.from === 'git' && e.to === 'http') return { ...e, state: 'done' };
        return { ...e, state: e.state || 'pending' };
      });
    } else {
      edges = edges.map((e, i) => ({
        ...e,
        state: i < 2 ? 'done' : i === 2 ? 'active' : 'pending',
      }));
    }
    return { nodes, edges };
  }, [adaptive]);

  const isArtifact = mode === 'artifact';

  if (isArtifact) {
    return (
      <div className="artifact-layout" data-screen={adaptive ? 'adaptive-state' : 'vertical-roadmap'} data-mode="artifact">
        <div className="artifact-canvas">
          <div className="artifact-canvas-head">
            <h1 className="artifact-canvas-title">Backend Developer</h1>
            <p className="artifact-canvas-hint">Clique em um domínio para ver referências e falar com a IA</p>
          </div>
          <div className="graph-wrap artifact-graph-wrap">
            <SkillGraph
              nodes={nodes}
              edges={edges}
              selected={selectedNode}
              onSelect={setSelectedNode}
              uniform
            />
          </div>
        </div>

        <div className={`slideover-backdrop ${selectedNode ? 'open' : ''}`} onClick={() => setSelectedNode(null)}></div>
        <div className={`slideover node-detail-slideover ${selectedNode ? 'open' : ''}`}>
          <NodeDetailSidebar
            nodeId={selectedNode}
            nodes={nodes}
            onClose={() => setSelectedNode(null)}
            onValidate={(id) => { setSelectedNode(null); onValidate(id); }}
          />
        </div>

        {/* Mentor drawer — optional, not in default canvas */}
        <div className={`slideover-backdrop ${mentorOpen ? 'open' : ''}`} onClick={onCloseMentor}></div>
        <div className={`slideover ${mentorOpen ? 'open' : ''}`}>
          <MentorDrawer onClose={onCloseMentor} adaptive={adaptive} />
        </div>
      </div>
    );
  }

  // Legacy setup-style dashboard (fallback if mode !== artifact)
  const validated = nodes.filter(n => n.status === 'approved').length;
  const total = nodes.length;
  const summary = adaptive
    ? { eyebrow: 'Trilha recalibrada', title: 'Foque em HTTP — sua validação em REST mostrou gaps', meta: '20 min · revisão guiada', variant: 'warning' }
    : { eyebrow: 'Próxima missão', title: 'HTTP básico — métodos e status codes', meta: '30 min · seção 1 de 3', variant: 'default' };

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
          <SkillGraph nodes={nodes} edges={edges} selected={selectedNode} onSelect={setSelectedNode} />
        </div>
      </div>
      <aside className="dash-side">
        <div className="card side-card">
          <div className="side-card-head">
            <span className="side-card-title">Progresso</span>
            <span className="side-card-meta">{validated}/{total}</span>
          </div>
        </div>
      </aside>
      <div className={`slideover-backdrop ${selectedNode ? 'open' : ''}`} onClick={() => setSelectedNode(null)}></div>
      <div className={`slideover ${selectedNode ? 'open' : ''}`}>
        <NodeDetail nodeId={selectedNode} nodes={nodes} onClose={() => setSelectedNode(null)} onValidate={onValidate} />
      </div>
    </div>
  );
};

// === Mentor Drawer (optional — not default artifact chrome) ===
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
