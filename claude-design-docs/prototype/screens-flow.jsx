// Career Forge — Screens 1, 2, 3, 5

// === Screen 1: Goal Picker (minimal) ===
const GoalPickerScreen = ({ onNext }) => {
  const [selected, setSelected] = React.useState('backend');
  const [motivation, setMotivation] = React.useState('Quero trabalhar com APIs para space tech — sonho em escrever os sistemas que orquestram lançamentos de foguetes.');
  const [touched, setTouched] = React.useState(false);

  const goals = [
    { id: 'backend', title: 'Backend Developer', active: true },
    { id: 'data', title: 'Data Engineer', active: false },
    { id: 'frontend', title: 'Frontend Developer', active: false },
  ];

  const valid = selected && motivation.trim().length >= 20;

  return (
    <div className="container goal-minimal" data-screen="goal-picker">
      <header className="goal-minimal-head">
        <span className="goal-minimal-step">Passo 1 de 3</span>
        <h1 className="goal-minimal-title">Para onde você quer ir?</h1>
      </header>

      <div className="goal-minimal-grid">
        {goals.map(g => (
          <button
            key={g.id}
            type="button"
            className={`goal-minimal-card ${selected === g.id ? 'selected' : ''} ${!g.active ? 'disabled' : ''}`}
            onClick={() => g.active && setSelected(g.id)}
            disabled={!g.active}
          >
            <span className="goal-minimal-card-title">{g.title}</span>
            {!g.active && <span className="goal-minimal-lock">Em breve</span>}
          </button>
        ))}
      </div>

      <div className="goal-minimal-motivation">
        <label className="goal-minimal-label" htmlFor="motivation">
          Por que esse caminho?
          <span className="field-hint">{motivation.length}/280</span>
        </label>
        <textarea
          id="motivation"
          className="textarea goal-minimal-textarea"
          placeholder="Quero trabalhar com APIs para space tech..."
          value={motivation}
          onChange={(e) => { setMotivation(e.target.value.slice(0, 280)); setTouched(true); }}
        />
        {touched && motivation.trim().length < 20 && (
          <p className="goal-minimal-hint">Mínimo 20 caracteres para personalizar sua trilha.</p>
        )}
      </div>

      <div className="goal-minimal-actions">
        <button className="btn btn-primary" disabled={!valid} onClick={onNext}>
          Começar diagnóstico <Icon name="arrowRight" size={14} />
        </button>
      </div>
    </div>
  );
};

// === Screen 2: Diagnostic — pill rounds (batch questions) ===
const DIAG_ROUNDS = [
  {
    id: 'seniority',
    title: 'Nível e contexto',
    intro: 'Sem certo ou errado — quanto mais honesto, mais útil sua trilha.',
    maps: ['Senioridade', 'Experiência prévia'],
    questions: [
      {
        id: 'level',
        tag: 'Senioridade',
        prompt: 'Qual seu nível hoje com programação?',
        placeholder: 'Ex.: estou começando, já sei JS básico, estudo há 6 meses…',
        defaultValue: 'Já programo em JavaScript há alguns meses, mas ainda me sinto iniciante em backend.',
      },
      {
        id: 'prior',
        tag: 'Contexto',
        prompt: 'Já estudou ou trabalhou com desenvolvimento antes?',
        placeholder: 'Cursos, bootcamp, projetos pessoais, estágio…',
        defaultValue: 'Fiz um curso online de JS e subi um projeto no GitHub.',
      },
    ],
  },
  {
    id: 'stack',
    title: 'Stack e domínios',
    intro: 'Mapeamos familiaridade com conceitos que aparecem na trilha backend.',
    maps: ['Git', 'Cliente/servidor'],
    questions: [
      {
        id: 'git',
        tag: 'Git',
        prompt: 'Você já usou Git em algum projeto?',
        placeholder: 'Clone, commit, push, branches…',
        defaultValue: 'Sim, subi um projeto no GitHub mas não domino branches.',
      },
      {
        id: 'client_server',
        tag: 'Domínio',
        prompt: 'Consegue explicar a diferença entre frontend e backend?',
        placeholder: 'Com suas palavras — o que cada um faz?',
        defaultValue: 'Frontend é o que o usuário vê. Backend processa dados no servidor.',
      },
    ],
  },
  {
    id: 'gaps',
    title: 'Lacunas técnicas',
    intro: 'Última rodada — HTTP, APIs e persistência.',
    maps: ['HTTP & APIs', 'Banco de dados'],
    questions: [
      {
        id: 'http',
        tag: 'HTTP',
        prompt: 'Você já fez alguma requisição HTTP ou chamou uma API?',
        placeholder: 'GET, POST, status codes, JSON…',
        defaultValue: 'Acho que sim, mas nunca prestei atenção em métodos ou status codes.',
      },
      {
        id: 'db',
        tag: 'DB',
        prompt: 'Ao pensar em "criar um usuário", o que vem primeiro — tela, banco ou requisição?',
        placeholder: 'Descreva seu modelo mental…',
        defaultValue: 'Acho que uma tela com formulário… mas o backend salva no banco.',
      },
    ],
  },
];

const DiagnosticScreen = ({ onNext }) => {
  const [roundIdx, setRoundIdx] = React.useState(0);
  const [answers, setAnswers] = React.useState(() => {
    const init = {};
    DIAG_ROUNDS.forEach(r => r.questions.forEach(q => { init[q.id] = q.defaultValue; }));
    return init;
  });
  const [generating, setGenerating] = React.useState(false);

  const round = DIAG_ROUNDS[roundIdx];
  const totalQuestions = DIAG_ROUNDS.reduce((n, r) => n + r.questions.length, 0);
  const answeredCount = roundIdx * 2 + round.questions.filter(q => answers[q.id]?.trim()).length;
  const pct = Math.min(100, Math.round((answeredCount / totalQuestions) * 100));

  const roundComplete = round.questions.every(q => answers[q.id]?.trim().length >= 8);
  const isLastRound = roundIdx === DIAG_ROUNDS.length - 1;

  const mapStatus = (label) => {
    const done = ['Senioridade', 'Experiência prévia', 'Git', 'Cliente/servidor'].includes(label);
    const active = round.maps.includes(label);
    if (done && roundIdx > 0) return 'done';
    if (active) return 'active';
    return 'pending';
  };

  const submitRound = () => {
    if (!roundComplete) return;
    if (isLastRound) {
      setGenerating(true);
      setTimeout(() => onNext(), 2200);
      return;
    }
    setRoundIdx(i => i + 1);
  };

  return (
    <div className="diag-layout diag-pills" data-screen="diagnostic">
      <aside className="diag-recap">
        <div className="card recap-card">
          <div className="recap-eyebrow">Seu sonho</div>
          <div className="recap-goal">
            <Icon name="server" size={14} />
            Backend Developer
          </div>
          <div className="recap-motiv">
            Quero trabalhar com APIs para space tech — sonho em escrever os sistemas que orquestram lançamentos de foguetes.
          </div>
          <div className="recap-progress">
            <div className="progress-label">
              <span>Diagnóstico</span>
              <span>Rodada {roundIdx + 1}/{DIAG_ROUNDS.length}</span>
            </div>
            <div className="progress-rail"><div className="progress-fill" style={{ width: `${pct}%` }}></div></div>
          </div>

          <div className="diag-map-section">
            <div className="recap-eyebrow">O que a IA está mapeando</div>
            <ul className="diag-map-list">
              {['Senioridade', 'Git', 'HTTP & APIs', 'Banco de dados'].map(label => (
                <li key={label} className={`diag-map-item ${mapStatus(label)}`}>
                  <span className="diag-map-dot"></span>
                  {label}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </aside>

      <div className="card diag-pills-panel">
        <div className="diag-pills-header">
          <div className="chat-step">Passo <b>2/3</b> · Diagnóstico · Rodada {roundIdx + 1} de {DIAG_ROUNDS.length}</div>
          <span className="diag-pills-round-tag">{round.title}</span>
        </div>

        <div className="diag-pills-intro">
          <Icon name="sparkles" size={14} />
          {round.intro}
        </div>

        <div className="diag-pills-grid">
          {round.questions.map(q => (
            <div key={q.id} className="diag-pill">
              <div className="diag-pill-head">
                <span className="diag-pill-tag">{q.tag}</span>
                <p className="diag-pill-prompt">{q.prompt}</p>
              </div>
              <textarea
                className="diag-pill-input"
                placeholder={q.placeholder}
                value={answers[q.id] || ''}
                onChange={(e) => setAnswers(a => ({ ...a, [q.id]: e.target.value }))}
                disabled={generating}
                rows={3}
              />
            </div>
          ))}
        </div>

        {generating ? (
          <div className="gen-skeleton diag-pills-generating">
            <div className="spinner"></div>
            <div className="gen-skeleton-text">
              <b>Gerando diagnóstico…</b> mapeando {totalQuestions} sinais nas suas respostas.
            </div>
          </div>
        ) : (
          <div className="diag-pills-footer">
            <span className="diag-pills-hint">
              {round.questions.length} perguntas nesta rodada · responda todas para continuar
            </span>
            <button className="btn btn-primary" disabled={!roundComplete} onClick={submitRound}>
              {isLastRound ? 'Gerar diagnóstico' : 'Próxima rodada'} <Icon name="arrowRight" size={14} />
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

// === Screen 3: Diagnosis Result ===
const DiagnosisResultScreen = ({ onNext }) => {
  return (
    <div className="container" data-screen="diagnosis-result">
      <div className="diag-result">
        <div className="diag-header">
          <div className="diag-badge">
            <span className="swatch"></span>
            Perfil: <b>Iniciante com base em JavaScript</b>
          </div>
          <h1 className="diag-h1">Seu diagnóstico</h1>
          <p className="diag-sub">Mapeamos 4 sinais nas suas respostas. Esta é a foto de hoje — sua trilha vai recalibrar a cada validação.</p>
        </div>

        <div className="diag-grid">
          <div className="card diag-col strengths">
            <div className="diag-col-head">
              <span className="diag-col-title">Pontos fortes</span>
              <span className="diag-col-count">2</span>
            </div>
            <div className="diag-bullet s">
              <span className="icon"><Icon name="check" size={11} stroke={3} /></span>
              <span>Já entende lógica básica e raciocínio cliente/servidor.</span>
            </div>
            <div className="diag-bullet s">
              <span className="icon"><Icon name="check" size={11} stroke={3} /></span>
              <span>Já usou GitHub superficialmente — sabe versionar trabalho.</span>
            </div>
          </div>

          <div className="card diag-col gaps">
            <div className="diag-col-head">
              <span className="diag-col-title">Lacunas</span>
              <span className="diag-col-count">3</span>
            </div>
            <div className="diag-bullet g">
              <span className="icon"><Icon name="alert" size={11} /></span>
              <span>HTTP e APIs REST — métodos, status codes e contrato.</span>
            </div>
            <div className="diag-bullet g">
              <span className="icon"><Icon name="alert" size={11} /></span>
              <span>Autenticação — sessões, tokens, fluxo seguro.</span>
            </div>
            <div className="diag-bullet g">
              <span className="icon"><Icon name="alert" size={11} /></span>
              <span>Banco relacional — modelagem e SQL aplicado.</span>
            </div>
          </div>

          <div className="card diag-col recomm">
            <div className="diag-col-head">
              <span className="diag-col-title">Recomendação</span>
              <span className="diag-col-count">1ª missão</span>
            </div>
            <div className="diag-bullet r">
              <span className="icon"><Icon name="target" size={11} /></span>
              <span><b style={{ color: 'var(--text)' }}>Comece por HTTP</b> antes de APIs REST. Sem HTTP firme, REST vira decoreba.</span>
            </div>
            <div className="diag-bullet r">
              <span className="icon"><Icon name="clock" size={11} /></span>
              <span>Estimativa: <b style={{ color: 'var(--text)' }}>30 min</b> para a primeira sessão.</span>
            </div>
          </div>
        </div>

        <div className="diag-evidence">
          <div className="evidence-icon"><Icon name="file" size={16} /></div>
          <div className="diag-evidence-text">
            <b>Avaliação por evidência.</b> Career Forge não te deixa marcar tópicos como "concluído". Cada domínio só destrava quando você prova entendimento numa entrevista com a IA — e seu mentor da Borderless recebe o histórico das suas evidências.
          </div>
        </div>

        <div className="diag-cta">
          <div className="diag-cta-meta">
            <Icon name="sparkles" size={12} style={{ verticalAlign: 'middle', marginRight: 6 }} />
            Trilha gerada com 7 domínios, 1 já validado e 1 recomendado.
          </div>
          <button className="btn btn-primary btn-lg" onClick={onNext}>
            Ver minha trilha <Icon name="arrowRight" size={14} />
          </button>
        </div>
      </div>
    </div>
  );
};

// === Screen 5: Validation Interview ===
const ValidationScreen = ({ onPass, onFail, onBack }) => {
  // 'question' | 'submitting' | 'result'
  const [phase, setPhase] = React.useState('question');
  const [answer, setAnswer] = React.useState('REST é um jeito de duas aplicações trocarem dados pela internet. Tipo, eu mando um GET pra um endpoint /users e ele retorna os usuários em JSON. Pra criar um usuário acho que seria POST /users com os dados no corpo da requisição.');
  const [accordionOpen, setAccordionOpen] = React.useState(false);

  const submit = () => {
    setPhase('submitting');
    setTimeout(() => setPhase('result'), 1600);
  };

  if (phase === 'result') {
    return (
      <div className="val-layout" data-screen="validation-result">
        <div className="val-topic-bar">
          <div className="val-topic-name">
            <div className="val-topic-icon">/r</div>
            APIs REST
          </div>
          <div className="val-progress-dots">
            <span>Resultado</span>
            <span className="val-dot done"></span>
            <span className="val-dot done"></span>
            <span className="val-dot done"></span>
          </div>
        </div>

        <div className="val-result-grid">
          <div className="card score-card">
            <ScoreRing score={48} status="review" />
            <div>
              <StatusPill status="review" />
            </div>
            <div className="score-label">Você está perto, mas ainda não passou.</div>
          </div>

          <div className="val-feedback">
            <div className="card feedback-block ok">
              <div className="feedback-block-head">
                <Icon name="check" size={14} stroke={2.5} />
                Você acertou
              </div>
              <ul className="feedback-list">
                <li><span className="dot-i"></span><span style={{ color: 'var(--text)' }}>Entendeu comunicação entre sistemas como base do REST.</span></li>
                <li><span className="dot-i"></span><span style={{ color: 'var(--text)' }}>Citou endpoints e JSON corretamente como payload.</span></li>
              </ul>
            </div>

            <div className="card feedback-block warn">
              <div className="feedback-block-head">
                <Icon name="alert" size={14} />
                Precisa melhorar
              </div>
              <ul className="feedback-list">
                <li><span className="dot-i"></span><span style={{ color: 'var(--text)' }}>Confundiu método HTTP com rota. POST não é "criar" — é um verbo independente da URL.</span></li>
                <li><span className="dot-i"></span><span style={{ color: 'var(--text)' }}>Não explicou status codes (201, 400, 404, 500). Sem isso, sua API não dialoga.</span></li>
                <li><span className="dot-i"></span><span style={{ color: 'var(--text)' }}>Não mencionou stateless — propriedade central do REST.</span></li>
              </ul>
            </div>

            <div className="card feedback-block next">
              <div className="feedback-block-head">
                <Icon name="target" size={14} />
                Próximo passo
              </div>
              <p>Revise <b>GET, POST, PUT, PATCH, DELETE</b> e suas semânticas. Depois, volte e tente novamente — sem decoreba.</p>
            </div>

            <div className={`mentor-accordion ${accordionOpen ? 'open' : ''}`}>
              <button className="mentor-accordion-head" onClick={() => setAccordionOpen(o => !o)}>
                <div className="left">
                  <Icon name="file" size={14} />
                  Resumo para o mentor (Borderless)
                </div>
                <Icon name="chevron" size={14} className="chevron" />
              </button>
              <div className="mentor-accordion-body">
                Para o mentor: aluno confunde API com acesso direto ao banco — usa "POST /users" como sinônimo de "criar registro", sem distinguir o verbo HTTP da intenção semântica. Não articula status codes nem statelessness. Recomendo sessão de 20 min focada em métodos HTTP antes de retomar APIs REST. Pontos fortes: comunica-se com clareza e raciocina por exemplo.
              </div>
            </div>
          </div>
        </div>

        <div className="val-actions">
          <button className="btn btn-soft" onClick={onBack}><Icon name="arrowLeft" size={14} /> Voltar à trilha</button>
          <div className="val-actions-right">
            <button className="btn btn-ghost" onClick={onFail}>Ver trilha adaptada <Icon name="arrowRight" size={14} /></button>
            <button className="btn btn-primary" onClick={() => setPhase('question')}>
              <Icon name="refresh" size={14} /> Refazer validação
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="val-layout" data-screen="validation">
      <div className="val-head">
        <h1 className="val-h1">Pronto para validar seu aprendizado?</h1>
        <p className="val-sub">A IA vai te entrevistar antes de liberar o próximo tópico. Pense como se estivesse explicando para um colega.</p>
      </div>

      <div className="val-topic-bar">
        <div className="val-topic-name">
          <div className="val-topic-icon">/r</div>
          APIs REST
        </div>
        <div className="val-progress-dots">
          <span>Pergunta <b style={{ color: 'var(--text)' }}>2</b> de 3</span>
          <span className="val-dot done"></span>
          <span className="val-dot current"></span>
          <span className="val-dot"></span>
        </div>
      </div>

      <div className="card val-question-card">
        <div className="val-q-label">Pergunta 02 · conceito + aplicação</div>
        <p className="val-q-text">Explique com suas palavras o que é uma API REST e dê um exemplo de endpoint para criar um usuário.</p>
        <p className="val-q-hint">Dica: pense em método HTTP, rota, e o que vai no corpo da requisição.</p>
      </div>

      <div className="val-answer-wrap">
        <textarea
          className="textarea val-answer"
          placeholder="Comece pela sua intuição..."
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
          disabled={phase === 'submitting'}
        />
        <div className="val-answer-footer">
          <span>{answer.length} caracteres · sem limite</span>
          <span>⌘+Enter para enviar</span>
        </div>
      </div>

      <div className="val-actions">
        <div className="val-evidence-note">
          <Icon name="sparkles" size={12} />
          Avaliação por evidência — não basta marcar como concluído
        </div>
        <div className="val-actions-right">
          <button className="btn btn-soft" onClick={onBack}>Desistir</button>
          <button className="btn btn-primary" disabled={phase === 'submitting' || answer.trim().length < 10} onClick={submit}>
            {phase === 'submitting' ? (
              <><div className="spinner" style={{ width: 14, height: 14, borderWidth: 2 }}></div> Avaliando…</>
            ) : (
              <>Enviar resposta <Icon name="arrowRight" size={14} /></>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

Object.assign(window, { GoalPickerScreen, DiagnosticScreen, DiagnosisResultScreen, ValidationScreen });
