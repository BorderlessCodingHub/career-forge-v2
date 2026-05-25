// Career OS — SkillGraph hero component
const { useState: useStateG } = React;

const SKILL_NODES_BASE = [
  { id: 'git',    title: 'Git e GitHub',           icon: 'git',      pct: 78, status: 'approved',    x: 120, y: 90,  desc: 'Versionamento e fluxo colaborativo' },
  { id: 'http',   title: 'HTTP básico',            icon: 'server',   pct: 42, status: 'recommended', x: 380, y: 90,  desc: 'Métodos, status codes, headers', current: true },
  { id: 'rest',   title: 'APIs REST',              icon: 'code',     pct: 0,  status: 'locked',      x: 640, y: 90,  desc: 'Design de endpoints, JSON' },
  { id: 'auth',   title: 'Autenticação JWT',       icon: 'key',      pct: 0,  status: 'locked',      x: 900, y: 90,  desc: 'Tokens, sessões, OAuth' },
  { id: 'js',     title: 'JavaScript base',        icon: 'code',     pct: 65, status: 'approved',    x: 120, y: 280, desc: 'Sintaxe, tipos, assincronia' },
  { id: 'db',     title: 'Banco relacional',       icon: 'database', pct: 35, status: 'recommended', x: 380, y: 280, desc: 'SQL, modelagem, joins' },
  { id: 'final',  title: 'Projeto: API CRUD',      icon: 'boxes',    pct: 0,  status: 'locked',      x: 770, y: 280, desc: 'Aplicação final integrando tudo' },
];

const SKILL_EDGES_BASE = [
  { from: 'git', to: 'http', state: 'done' },
  { from: 'http', to: 'rest', state: 'active' },
  { from: 'rest', to: 'auth', state: 'pending' },
  { from: 'js', to: 'http', state: 'done' },
  { from: 'js', to: 'db', state: 'active' },
  { from: 'db', to: 'final', state: 'pending' },
  { from: 'rest', to: 'final', state: 'pending' },
  { from: 'auth', to: 'final', state: 'pending' },
];

const NODE_W = 200, NODE_H = 110;

const SkillNode = ({ node, selected, onClick, extraClass = '' }) => {
  const sel = selected === node.id ? 'selected' : '';
  const curr = node.current ? 'active-current' : '';
  return (
    <g
      className={`skill-node ${node.status} ${sel} ${curr} ${extraClass}`}
      transform={`translate(${node.x},${node.y})`}
      onClick={() => onClick && onClick(node.id)}
      style={{ cursor: onClick ? 'pointer' : 'default' }}
    >
      <rect className="skill-node-bg" width={NODE_W} height={NODE_H} rx="10" />
      {/* status accent stripe */}
      <rect
        x={0} y={0} width={3} height={NODE_H}
        fill={
          node.status === 'approved' ? 'var(--success)' :
          node.status === 'recommended' ? 'var(--accent)' :
          node.status === 'review' ? 'var(--warning)' :
          'var(--locked)'
        }
        opacity={node.status === 'locked' ? 0.3 : 0.9}
      />
      {/* icon box */}
      <foreignObject x={14} y={14} width={32} height={32}>
        <div style={{
          width: 32, height: 32, borderRadius: 8,
          background: 'var(--bg)', border: '1px solid var(--border)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: node.status === 'locked' ? 'var(--text-3)' :
                 node.status === 'approved' ? 'var(--success)' :
                 node.status === 'review' ? 'var(--warning)' : 'var(--accent-2)'
        }}>
          <Icon name={node.icon} size={16} />
        </div>
      </foreignObject>
      {/* title */}
      <text x={56} y={28} fill="var(--text)" fontSize="13" fontWeight="600" fontFamily="Inter">
        {node.title}
      </text>
      <text x={56} y={44} fill="var(--text-3)" fontSize="11" fontFamily="Inter">
        {node.desc}
      </text>
      {/* status pill via foreignObject */}
      <foreignObject x={12} y={64} width={NODE_W - 24} height={36}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 8 }}>
          <StatusPill status={node.status} />
          {node.status !== 'locked' && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, flex: 1, maxWidth: 100 }}>
              <div style={{ flex: 1, height: 3, background: 'var(--surface-3)', borderRadius: 999, overflow: 'hidden' }}>
                <div style={{
                  height: '100%',
                  width: `${node.pct}%`,
                  background: node.status === 'approved' ? 'var(--success)' :
                              node.status === 'review' ? 'var(--warning)' : 'var(--accent)',
                  borderRadius: 999
                }} />
              </div>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--text-3)' }}>{node.pct}%</span>
            </div>
          )}
        </div>
      </foreignObject>
    </g>
  );
};

const SkillGraph = ({ nodes, edges, selected, onSelect }) => {
  // Bezier path between two nodes (right edge of A -> left edge of B)
  const path = (from, to) => {
    const fx = from.x + NODE_W;
    const fy = from.y + NODE_H / 2;
    const tx = to.x;
    const ty = to.y + NODE_H / 2;
    const dx = (tx - fx) / 2;
    // If on same row use simple curve, else use S curve
    if (from.y === to.y) {
      return `M ${fx} ${fy} C ${fx + dx} ${fy}, ${tx - dx} ${ty}, ${tx} ${ty}`;
    }
    // Cross-row: route through a vertical segment near middle
    const midX = fx + (tx - fx) / 2;
    return `M ${fx} ${fy} C ${midX} ${fy}, ${midX} ${ty}, ${tx} ${ty}`;
  };
  const nodeMap = Object.fromEntries(nodes.map(n => [n.id, n]));
  return (
    <svg className="graph-svg" viewBox="0 0 1100 440" preserveAspectRatio="xMidYMid meet">
      <defs>
        <marker id="arrow-default" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--border)" />
        </marker>
        <marker id="arrow-done" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--success)" opacity="0.5" />
        </marker>
        <marker id="arrow-active" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent)" opacity="0.7" />
        </marker>
      </defs>
      {edges.map((e, i) => {
        const from = nodeMap[e.from];
        const to = nodeMap[e.to];
        if (!from || !to) return null;
        return (
          <path
            key={i}
            className={`skill-link ${e.state === 'done' ? 'done' : ''} ${e.state === 'active' ? 'active' : ''}`}
            d={path(from, to)}
            markerEnd={`url(#arrow-${e.state === 'done' ? 'done' : e.state === 'active' ? 'active' : 'default'})`}
          />
        );
      })}
      {nodes.map(n => (
        <SkillNode key={n.id} node={n} selected={selected} onClick={onSelect} />
      ))}
    </svg>
  );
};

// Node detail panel content
const NodeDetail = ({ nodeId, nodes, onClose, onValidate }) => {
  if (!nodeId) return null;
  const node = nodes.find(n => n.id === nodeId);
  if (!node) return null;

  const outcomes = {
    git:    ['Criar e clonar repositórios', 'Trabalhar com branches e merges', 'Resolver conflitos básicos', 'Subir mudanças para o GitHub'],
    http:   ['Diferenciar GET, POST, PUT, DELETE', 'Interpretar status codes (2xx/4xx/5xx)', 'Entender headers e payloads', 'Usar curl para testar requests'],
    rest:   ['Modelar recursos e endpoints', 'Aplicar princípios REST (stateless, cacheable)', 'Tratar erros de forma consistente', 'Documentar uma API com OpenAPI'],
    auth:   ['Implementar login com JWT', 'Gerenciar refresh tokens', 'Proteger rotas com middleware', 'Reconhecer OAuth 2.0 e flows'],
    js:     ['Trabalhar com tipos e escopo', 'Usar Promises e async/await', 'Manipular arrays e objetos', 'Estruturar módulos'],
    db:     ['Modelar tabelas e relacionamentos', 'Escrever queries SQL com joins', 'Otimizar com índices básicos', 'Migrar schemas com segurança'],
    final:  ['Projetar uma API CRUD completa', 'Integrar banco e autenticação', 'Escrever testes para endpoints', 'Documentar e fazer deploy'],
  }[nodeId] || [];

  const prereqMap = {
    rest: [{ id: 'http', name: 'HTTP básico', pct: 42, status: 'recommended', state: 'current' }, { id: 'js', name: 'JavaScript base', pct: 65, status: 'approved', state: 'done' }],
    auth: [{ id: 'rest', name: 'APIs REST', pct: 0, status: 'locked', state: 'blocked' }],
    final: [{ id: 'rest', name: 'APIs REST', pct: 0, status: 'locked', state: 'blocked' }, { id: 'auth', name: 'Autenticação JWT', pct: 0, status: 'locked', state: 'blocked' }, { id: 'db', name: 'Banco relacional', pct: 35, status: 'recommended', state: 'current' }],
    http: [{ id: 'js', name: 'JavaScript base', pct: 65, status: 'approved', state: 'done' }],
    db:   [{ id: 'js', name: 'JavaScript base', pct: 65, status: 'approved', state: 'done' }],
  }[nodeId] || [];

  const statusText = {
    locked: 'Aguardando pré-requisitos. Conclua os domínios abaixo para destravar.',
    recommended: 'Recomendado para sua próxima sessão. Você está pronto para mergulhar.',
    approved: 'Validado pela IA. Continua disponível para revisão a qualquer momento.',
    review: 'Sua última validação mostrou lacunas. Revise os outcomes marcados.',
  }[node.status];

  return (
    <>
      <div className="slideover-head">
        <div className="row" style={{ gap: 12 }}>
          <div style={{
            width: 36, height: 36, borderRadius: 9,
            background: 'var(--surface-2)', border: '1px solid var(--border)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            color: node.status === 'approved' ? 'var(--success)' :
                   node.status === 'review' ? 'var(--warning)' :
                   node.status === 'locked' ? 'var(--text-3)' : 'var(--accent-2)'
          }}>
            <Icon name={node.icon} size={18} />
          </div>
          <div>
            <div style={{ fontSize: 11, color: 'var(--text-3)', fontFamily: 'var(--font-mono)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Domínio · {nodeId}</div>
            <div style={{ fontSize: 16, fontWeight: 600 }}>{node.title}</div>
          </div>
        </div>
        <button className="slideover-close" onClick={onClose}><Icon name="x" size={18} /></button>
      </div>

      <div className="slideover-body">
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
          <StatusPill status={node.status} />
          {node.status !== 'locked' && (
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-3)' }}>
              progresso · <span style={{ color: 'var(--text)' }}>{node.pct}%</span>
            </span>
          )}
        </div>
        <div className="node-detail-status">{statusText}</div>

        <div className="node-section">
          <div className="node-section-title">Outcomes esperados</div>
          <ol className="outcomes-list">
            {outcomes.map((o, i) => (
              <li key={i}>
                <span className="num">{String(i + 1).padStart(2, '0')}</span>
                <span>{o}</span>
              </li>
            ))}
          </ol>
        </div>

        {prereqMap.length > 0 && (
          <div className="node-section">
            <div className="node-section-title">Pré-requisitos</div>
            <div className="prereq-chain">
              {prereqMap.map(p => (
                <div key={p.id} className={`prereq-row ${p.state}`}>
                  <StatusPill status={p.status} />
                  <span className="prereq-name">{p.name}</span>
                  <span className="prereq-pct">{p.pct}%</span>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="node-section">
          <div className="node-section-title">Evidências exigidas</div>
          <div style={{ fontSize: 13, color: 'var(--text-2)', lineHeight: 1.6 }}>
            A IA fará 3 perguntas situacionais sobre {node.title.toLowerCase()}. Você precisa de score ≥ 70 para liberar o próximo domínio.
          </div>
        </div>
      </div>

      <div className="slideover-foot">
        <button className="btn btn-soft" style={{ flex: 1 }} onClick={onClose}>Fechar</button>
        <button
          className="btn btn-primary"
          style={{ flex: 1 }}
          disabled={node.status === 'locked'}
          onClick={() => onValidate(nodeId)}
        >
          {node.status === 'review' ? 'Refazer validação' : 'Validar com IA'} <Icon name="arrowRight" size={14} />
        </button>
      </div>
    </>
  );
};

// === Skeleton node (forge phase) ===
const SkeletonNode = ({ x, y, idx }) => (
  <g transform={`translate(${x},${y})`} style={{ opacity: 0.6 }}>
    <rect className="skel-node-bg" width={NODE_W} height={NODE_H} rx="10" />
    <rect className="skel-icon-box" x="14" y="14" width="32" height="32" rx="8" />
    <text x={56} y={28} fill="var(--text-3)" fontSize="10" fontFamily="var(--font-mono)" opacity="0.7">
      slot · {String(idx + 1).padStart(2, '0')}
    </text>
    <text x={56} y={44} fill="var(--text-3)" fontSize="9" fontFamily="var(--font-mono)" opacity="0.5">
      aguardando análise…
    </text>
    <rect className="skel-bar" x="14" y="82" width="60" height="6" rx="3" />
    <rect className="skel-bar" x="82" y="82" width="40" height="6" rx="3" opacity="0.5" />
  </g>
);

// === Forge Graph: progressive reveal ===
const ForgeGraph = ({ nodes, edges, revealed, revealClass = '' }) => {
  const path = (from, to) => {
    const fx = from.x + NODE_W;
    const fy = from.y + NODE_H / 2;
    const tx = to.x;
    const ty = to.y + NODE_H / 2;
    const dx = (tx - fx) / 2;
    if (from.y === to.y) {
      return `M ${fx} ${fy} C ${fx + dx} ${fy}, ${tx - dx} ${ty}, ${tx} ${ty}`;
    }
    const midX = fx + (tx - fx) / 2;
    return `M ${fx} ${fy} C ${midX} ${fy}, ${midX} ${ty}, ${tx} ${ty}`;
  };
  const nodeMap = Object.fromEntries(nodes.map(n => [n.id, n]));

  return (
    <svg className="graph-svg forge-graph-svg" viewBox="0 0 1100 440" preserveAspectRatio="xMidYMid meet">
      <defs>
        <marker id="farrow-default" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--border)" />
        </marker>
        <marker id="farrow-done" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--success)" opacity="0.5" />
        </marker>
        <marker id="farrow-active" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent)" opacity="0.7" />
        </marker>
      </defs>
      {/* Skeleton nodes (not yet revealed) */}
      {nodes.map((n, i) => !revealed.has(n.id) && (
        <SkeletonNode key={`s-${n.id}`} x={n.x} y={n.y} idx={i} />
      ))}
      {/* Edges: only when both endpoints are revealed */}
      {edges.map((e, i) => {
        const from = nodeMap[e.from];
        const to = nodeMap[e.to];
        if (!from || !to) return null;
        if (!revealed.has(e.from) || !revealed.has(e.to)) return null;
        return (
          <path
            key={i}
            className={`skill-link edge-materialize ${e.state === 'done' ? 'done' : ''} ${e.state === 'active' ? 'active' : ''}`}
            d={path(from, to)}
            markerEnd={`url(#farrow-${e.state === 'done' ? 'done' : e.state === 'active' ? 'active' : 'default'})`}
          />
        );
      })}
      {/* Revealed nodes */}
      {nodes.map((n, i) => revealed.has(n.id) && (
        <g key={n.id} className="node-materialize">
          <SkillNode node={n} selected={null} extraClass={revealClass ? `${revealClass}-${i}` : ''} />
        </g>
      ))}
    </svg>
  );
};

Object.assign(window, { SKILL_NODES_BASE, SKILL_EDGES_BASE, SkillGraph, SkillNode, NodeDetail, ForgeGraph, SkeletonNode });
