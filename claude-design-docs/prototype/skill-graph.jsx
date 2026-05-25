// Career Forge — SkillGraph (vertical roadmap.sh-style spine)

const SPINE_X = 520;
const NODE_W = 220;
const NODE_H = 96;
const ROW_H = 130;

const SKILL_CATEGORIES = [
  { id: 'fundamentos', label: 'Fundamentos', y: 48 },
  { id: 'backend', label: 'Backend Core', y: 318 },
  { id: 'integracao', label: 'Integração', y: 748 },
];

const SKILL_NODES_BASE = [
  { id: 'js',     title: 'JavaScript base',   icon: 'code',     pct: 65, status: 'approved',    side: 'left',  y: 90,  category: 'fundamentos', desc: 'Sintaxe, tipos, assincronia' },
  { id: 'git',    title: 'Git e GitHub',      icon: 'git',      pct: 78, status: 'approved',    side: 'right', y: 210, category: 'fundamentos', desc: 'Versionamento colaborativo' },
  { id: 'http',   title: 'HTTP básico',       icon: 'server',   pct: 42, status: 'recommended', side: 'left',  y: 360, category: 'backend',     desc: 'Métodos, status codes', current: true },
  { id: 'db',     title: 'Banco relacional',  icon: 'database', pct: 35, status: 'recommended', side: 'right', y: 480, category: 'backend',     desc: 'SQL, modelagem, joins' },
  { id: 'rest',   title: 'APIs REST',         icon: 'code',     pct: 0,  status: 'locked',      side: 'left',  y: 600, category: 'backend',     desc: 'Endpoints, JSON' },
  { id: 'auth',   title: 'Autenticação JWT',  icon: 'key',      pct: 0,  status: 'locked',      side: 'right', y: 720, category: 'backend',     desc: 'Tokens, OAuth' },
  { id: 'final',  title: 'Projeto: API CRUD', icon: 'boxes',    pct: 0,  status: 'locked',      side: 'left',  y: 860, category: 'integracao',  desc: 'Aplicação final integrada' },
];

const SKILL_EDGES_BASE = [
  { from: 'js', to: 'git' },
  { from: 'git', to: 'http' },
  { from: 'http', to: 'db' },
  { from: 'db', to: 'rest' },
  { from: 'rest', to: 'auth' },
  { from: 'auth', to: 'final' },
];

const nodeX = (node) => node.side === 'left' ? SPINE_X - NODE_W - 48 : SPINE_X + 48;

const nodeCenter = (node) => ({
  x: nodeX(node) + (node.side === 'left' ? NODE_W : 0),
  y: node.y + NODE_H / 2,
});

const edgeState = (fromId, toId, edges) => {
  const e = edges.find(x => x.from === fromId && x.to === toId);
  return e?.state || 'pending';
};

const SkillNode = ({ node, selected, onClick, extraClass = '', uniform = false }) => {
  const x = nodeX(node);
  const sel = selected === node.id ? 'selected' : '';
  const curr = !uniform && node.current ? 'active-current' : '';
  const statusClass = uniform ? 'uniform' : node.status;
  return (
    <g
      className={`skill-node ${statusClass} ${sel} ${curr} ${extraClass}`}
      transform={`translate(${x},${node.y})`}
      onClick={() => onClick && onClick(node.id)}
      style={{ cursor: onClick ? 'pointer' : 'default' }}
    >
      <rect className="skill-node-bg" width={NODE_W} height={NODE_H} rx="12" />
      {!uniform && (
        <rect
          x={node.side === 'left' ? NODE_W - 3 : 0} y={0} width={3} height={NODE_H}
          fill={
            node.status === 'approved' ? 'var(--success)' :
            node.status === 'recommended' ? 'var(--accent)' :
            node.status === 'review' ? 'var(--warning)' :
            'var(--locked)'
          }
          opacity={node.status === 'locked' ? 0.3 : 0.9}
        />
      )}
      {uniform && (
        <rect
          x={node.side === 'left' ? NODE_W - 3 : 0} y={0} width={3} height={NODE_H}
          fill="var(--accent)" opacity={0.55}
        />
      )}
      <foreignObject x={14} y={12} width={32} height={32}>
        <div className={uniform ? 'skill-node-icon uniform' : 'skill-node-icon'} style={{
          width: 32, height: 32, borderRadius: 8,
          background: uniform ? 'rgba(107,76,230,0.12)' : 'var(--bg)',
          border: uniform ? '1px solid rgba(107,76,230,0.35)' : '1px solid var(--border)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: uniform ? 'var(--accent-2)' :
                 node.status === 'locked' ? 'var(--text-3)' :
                 node.status === 'approved' ? 'var(--success)' :
                 node.status === 'review' ? 'var(--warning)' : 'var(--accent-2)'
        }}>
          <Icon name={node.icon} size={16} />
        </div>
      </foreignObject>
      <text x={56} y={26} fill="var(--text)" fontSize="13" fontWeight="600" fontFamily="Inter">
        {node.title}
      </text>
      <text x={56} y={42} fill="var(--text-3)" fontSize="11" fontFamily="Inter">
        {node.desc}
      </text>
      {!uniform && (
        <foreignObject x={12} y={58} width={NODE_W - 24} height={36}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 8 }}>
            <StatusPill status={node.status} />
            {node.status !== 'locked' && (
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, flex: 1, maxWidth: 100 }}>
                <div style={{ flex: 1, height: 3, background: 'var(--surface-3)', borderRadius: 999, overflow: 'hidden' }}>
                  <div style={{
                    height: '100%', width: `${node.pct}%`,
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
      )}
    </g>
  );
};

const VerticalSpine = ({ nodes, edges, uniform = false }) => {
  const sorted = [...nodes].sort((a, b) => a.y - b.y);
  const topY = sorted[0]?.y - 20 || 40;
  const bottomY = sorted[sorted.length - 1]?.y + NODE_H + 20 || 900;

  return (
    <>
      {/* Main vertical spine */}
      <line
        className="roadmap-spine"
        x1={SPINE_X} y1={topY} x2={SPINE_X} y2={bottomY}
      />
      {/* Category labels on spine */}
      {SKILL_CATEGORIES.map(cat => (
        <g key={cat.id} className="roadmap-category">
          <rect
            x={SPINE_X - 52} y={cat.y - 12} width={104} height={24} rx={12}
            fill="var(--surface-2)" stroke="var(--border-soft)" strokeWidth="1"
          />
          <text
            x={SPINE_X} y={cat.y + 4} textAnchor="middle"
            fill="var(--text-3)" fontSize="10" fontWeight="600"
            fontFamily="var(--font-mono)" letterSpacing="0.08em"
          >
            {cat.label.toUpperCase()}
          </text>
        </g>
      ))}
      {/* Spine segments between nodes + branch connectors */}
      {sorted.map((node, i) => {
        const cx = nodeCenter(node);
        const branchClass = uniform ? '' :
          node.status === 'approved' ? 'done' :
          node.current ? 'active' : node.status === 'review' ? 'active' : '';
        const next = sorted[i + 1];
        const spineY = node.y + NODE_H / 2;
        const nextSpineY = next ? next.y + NODE_H / 2 : null;
        const state = i < sorted.length - 1
          ? edgeState(node.id, next.id, edges)
          : 'pending';
        const segClass = uniform ? '' : state === 'done' ? 'done' : state === 'active' ? 'active' : '';
        return (
          <g key={node.id}>
            <line
              className={`roadmap-branch ${branchClass}`}
              x1={cx.x} y1={cx.y} x2={SPINE_X} y2={cx.y}
            />
            {nextSpineY && (
              <line
                className={`roadmap-spine-seg ${segClass}`}
                x1={SPINE_X} y1={spineY + NODE_H / 2 - 10}
                x2={SPINE_X} y2={nextSpineY - NODE_H / 2 + 10}
              />
            )}
          </g>
        );
      })}
    </>
  );
};

const SkillGraph = ({ nodes, edges, selected, onSelect, uniform = false }) => {
  const viewH = Math.max(980, ...nodes.map(n => n.y + NODE_H + 60));
  return (
    <svg className={`graph-svg graph-svg-vertical ${uniform ? 'graph-uniform' : ''}`} viewBox={`0 0 1040 ${viewH}`} preserveAspectRatio="xMidYMid meet">
      <VerticalSpine nodes={nodes} edges={edges} uniform={uniform} />
      {nodes.map(n => (
        <SkillNode key={n.id} node={n} selected={selected} onClick={onSelect} uniform={uniform} />
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

const SkeletonNode = ({ node, idx }) => {
  const x = nodeX(node);
  return (
    <g transform={`translate(${x},${node.y})`} style={{ opacity: 0.6 }}>
      <rect className="skel-node-bg" width={NODE_W} height={NODE_H} rx="12" />
      <rect className="skel-icon-box" x="14" y="12" width="32" height="32" rx="8" />
      <text x={56} y={26} fill="var(--text-3)" fontSize="10" fontFamily="var(--font-mono)" opacity="0.7">
        slot · {String(idx + 1).padStart(2, '0')}
      </text>
      <text x={56} y={42} fill="var(--text-3)" fontSize="9" fontFamily="var(--font-mono)" opacity="0.5">
        aguardando análise…
      </text>
      <rect className="skel-bar" x="14" y="74" width="60" height="6" rx="3" />
    </g>
  );
};

const ForgeGraph = ({ nodes, edges, revealed, revealClass = '', uniform = true }) => {
  const viewH = Math.max(980, ...nodes.map(n => n.y + NODE_H + 60));
  const visibleNodes = nodes.filter(n => revealed.has(n.id));
  const visibleEdges = edges.filter(e => revealed.has(e.from) && revealed.has(e.to));

  return (
    <svg className="graph-svg graph-svg-vertical forge-graph-svg graph-uniform" viewBox={`0 0 1040 ${viewH}`} preserveAspectRatio="xMidYMid meet">
      {visibleNodes.length > 0 && <VerticalSpine nodes={visibleNodes} edges={visibleEdges} uniform={uniform} />}
      {nodes.map((n, i) => !revealed.has(n.id) && (
        <SkeletonNode key={`s-${n.id}`} node={n} idx={i} />
      ))}
      {nodes.map((n, i) => revealed.has(n.id) && (
        <g key={n.id} className="node-materialize">
          <SkillNode node={n} selected={null} onClick={null} uniform={uniform} extraClass={revealClass ? `${revealClass}-${i}` : ''} />
        </g>
      ))}
    </svg>
  );
};

Object.assign(window, { SKILL_NODES_BASE, SKILL_EDGES_BASE, SkillGraph, SkillNode, NodeDetail, ForgeGraph, SkeletonNode });
