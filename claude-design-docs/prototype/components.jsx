// Career Forge — shared icons & components
const { useState, useEffect, useRef, useMemo } = React;

// === Icons (minimal stroke set) ===
const Icon = ({ name, size = 16, stroke = 1.75, className = '' }) => {
  const s = { width: size, height: size, strokeWidth: stroke };
  const props = { fill: 'none', stroke: 'currentColor', strokeLinecap: 'round', strokeLinejoin: 'round', viewBox: '0 0 24 24', ...s, className };
  const paths = {
    check: <polyline points="20 6 9 17 4 12" />,
    arrowRight: <><line x1="5" y1="12" x2="19" y2="12" /><polyline points="12 5 19 12 12 19" /></>,
    arrowLeft: <><line x1="19" y1="12" x2="5" y2="12" /><polyline points="12 19 5 12 12 5" /></>,
    sparkles: <><path d="M12 3l1.6 4.4L18 9l-4.4 1.6L12 15l-1.6-4.4L6 9l4.4-1.6L12 3z" /><path d="M19 14l.7 1.9 1.9.7-1.9.7L19 19l-.7-1.7-1.9-.7 1.9-.7L19 14z" /></>,
    lock: <><rect x="4" y="11" width="16" height="10" rx="2" /><path d="M8 11V7a4 4 0 0 1 8 0v4" /></>,
    send: <><line x1="22" y1="2" x2="11" y2="13" /><polygon points="22 2 15 22 11 13 2 9 22 2" /></>,
    x: <><line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" /></>,
    git: <><circle cx="6" cy="6" r="2.5" /><circle cx="6" cy="18" r="2.5" /><circle cx="18" cy="9" r="2.5" /><path d="M6 8.5V15.5" /><path d="M6 11A6 6 0 0 0 18 11" /></>,
    server: <><rect x="3" y="4" width="18" height="6" rx="2" /><rect x="3" y="14" width="18" height="6" rx="2" /><line x1="7" y1="7" x2="7" y2="7" /><line x1="7" y1="17" x2="7" y2="17" /></>,
    code: <><polyline points="16 18 22 12 16 6" /><polyline points="8 6 2 12 8 18" /></>,
    key: <><circle cx="8" cy="15" r="4" /><path d="M11 12L20 3" /><path d="M16 7L19 10" /></>,
    database: <><ellipse cx="12" cy="5" rx="9" ry="3" /><path d="M3 5v6c0 1.7 4 3 9 3s9-1.3 9-3V5" /><path d="M3 11v6c0 1.7 4 3 9 3s9-1.3 9-3v-6" /></>,
    boxes: <><path d="M3 7l9-4 9 4-9 4-9-4z" /><path d="M3 7v10l9 4 9-4V7" /><path d="M12 11v10" /></>,
    target: <><circle cx="12" cy="12" r="9" /><circle cx="12" cy="12" r="5" /><circle cx="12" cy="12" r="1.5" /></>,
    sun: <><circle cx="12" cy="12" r="4" /><line x1="12" y1="2" x2="12" y2="4" /><line x1="12" y1="20" x2="12" y2="22" /><line x1="2" y1="12" x2="4" y2="12" /><line x1="20" y1="12" x2="22" y2="12" /><line x1="4.9" y1="4.9" x2="6.3" y2="6.3" /><line x1="17.7" y1="17.7" x2="19.1" y2="19.1" /><line x1="4.9" y1="19.1" x2="6.3" y2="17.7" /><line x1="17.7" y1="6.3" x2="19.1" y2="4.9" /></>,
    alert: <><path d="M12 9v4" /><path d="M12 17h.01" /><path d="M10.3 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" /></>,
    plus: <><line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" /></>,
    chevron: <polyline points="9 18 15 12 9 6" />,
    refresh: <><polyline points="23 4 23 10 17 10" /><polyline points="1 20 1 14 7 14" /><path d="M3.5 9a9 9 0 0 1 14.85-3.36L23 10" /><path d="M20.5 15a9 9 0 0 1-14.85 3.36L1 14" /></>,
    clock: <><circle cx="12" cy="12" r="9" /><polyline points="12 7 12 12 15 14" /></>,
    file: <><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" /></>,
    sprout: <><path d="M12 20v-8" /><path d="M12 12a5 5 0 0 0-5-5H5v2a5 5 0 0 0 5 5h2" /><path d="M12 14a5 5 0 0 1 5-5h2v1a5 5 0 0 1-5 5h-2" /></>,
    flag: <><path d="M4 22V4" /><path d="M4 4h14l-3 5 3 5H4" /></>,
    quote: <><path d="M7 7h4v4H7c0 2 1 4 4 4" /><path d="M13 7h4v4h-4c0 2 1 4 4 4" /></>
  };
  return <svg {...props}>{paths[name]}</svg>;
};

// === Status Pill ===
const StatusPill = ({ status, size = 'sm' }) => {
  const map = {
    locked:      { cls: 'pill-locked',   label: 'bloqueado', icon: 'lock' },
    recommended: { cls: 'pill-recomm',   label: 'recomendado', icon: null },
    studying:    { cls: 'pill-studying', label: 'em estudo', icon: null },
    validate:    { cls: 'pill-validate', label: 'validar', icon: null },
    approved:    { cls: 'pill-approved', label: 'aprovado', icon: 'check' },
    review:      { cls: 'pill-review',   label: 'revisar', icon: 'alert' },
  };
  const m = map[status] || map.recommended;
  return (
    <span className={`pill ${m.cls}`}>
      {m.icon ? <Icon name={m.icon} size={11} stroke={2.5} /> : <span className="pill-dot" />}
      {m.label}
    </span>
  );
};

// === Top Nav with breadcrumb ===
const TopNav = ({ current, onNav }) => {
  const steps = [
    { id: 'goal',      label: 'Objetivo',    short: '01' },
    { id: 'diag',      label: 'Diagnóstico', short: '02' },
    { id: 'result',    label: 'Resultado',   short: '03' },
    { id: 'forge',     label: 'Forge',       short: '04' },
    { id: 'roadmap',   label: 'Trilha',      short: '05' },
    { id: 'validate',  label: 'Validação',   short: '06' },
    { id: 'adaptive',  label: 'Adaptação',   short: '07' },
  ];
  const currentIdx = steps.findIndex(s => s.id === current);
  return (
    <div className="topnav">
      <div className="brand">
        <div className="brand-mark"><span className="conn"></span></div>
        <div>
          <div className="brand-name">Career Forge</div>
          <div className="brand-tag">Aprender com validação prática</div>
        </div>
      </div>
      <div className="breadcrumb">
        {steps.map((s, i) => (
          <React.Fragment key={s.id}>
            <button
              className={`crumb ${current === s.id ? 'active' : ''} ${i < currentIdx ? 'done' : ''}`}
              onClick={() => onNav(s.id)}
            >
              <span className="crumb-num">{i < currentIdx ? <Icon name="check" size={10} stroke={3} /> : s.short}</span>
              {s.label}
            </button>
            {i < steps.length - 1 && <span className="crumb-sep">·</span>}
          </React.Fragment>
        ))}
      </div>
      <div className="nav-meta">v0.1 · prototype</div>
    </div>
  );
};

// === Score Ring (SVG) ===
const ScoreRing = ({ score, status = 'review', size = 160 }) => {
  const stroke = 10;
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const offset = c * (1 - score / 100);
  const colorMap = { approved: 'var(--success)', review: 'var(--warning)', studying: 'var(--accent)' };
  const color = colorMap[status] || colorMap.review;
  return (
    <div className="score-ring" style={{ width: size, height: size }}>
      <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
        <circle cx={size/2} cy={size/2} r={r} stroke="var(--surface-2)" strokeWidth={stroke} fill="none" />
        <circle
          cx={size/2} cy={size/2} r={r}
          stroke={color} strokeWidth={stroke} fill="none"
          strokeDasharray={c} strokeDashoffset={offset} strokeLinecap="round"
          style={{ transition: 'stroke-dashoffset 1.2s cubic-bezier(.2,.7,.2,1)' }}
        />
      </svg>
      <div className="score-ring-text">
        <div className="score-ring-num" style={{ color }}>{score}</div>
        <div className="score-ring-total">de 100</div>
      </div>
    </div>
  );
};

// === Mission Banner ===
const MissionBanner = ({ eyebrow, title, meta, variant = 'default', action }) => (
  <div className={`mission-banner ${variant === 'warning' ? 'warning' : ''}`}>
    <div className="mission-pulse"></div>
    <div className="mission-text">
      <div className="mission-eyebrow">{eyebrow}</div>
      <div className="mission-title">{title}</div>
    </div>
    {meta && <div className="mission-meta">{meta}</div>}
    {action}
  </div>
);

// === Chat bubble ===
const Bubble = ({ from, time, children }) => (
  <div className={`bubble ${from}`}>
    <div className="bubble-avatar">{from === 'ai' ? <Icon name="sparkles" size={14} /> : 'V'}</div>
    <div className="bubble-body">
      <div className="bubble-meta">{from === 'ai' ? 'Career Forge' : 'Você'} · {time}</div>
      <div className="bubble-content">{children}</div>
    </div>
  </div>
);

Object.assign(window, { Icon, StatusPill, TopNav, ScoreRing, MissionBanner, Bubble });
