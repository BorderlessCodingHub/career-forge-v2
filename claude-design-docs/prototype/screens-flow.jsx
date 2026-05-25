// Career Forge — Screens 1, 2, 3, 5

// === Screen 1: Goal Picker ===
const GoalPickerScreen = ({ onNext }) => {
  const [selected, setSelected] = React.useState('backend');
  const [motivation, setMotivation] = React.useState('Quero trabalhar com APIs para space tech — sonho em escrever os sistemas que orquestram lançamentos de foguetes.');
  const [touched, setTouched] = React.useState(false);

  const goals = [
    {
      id: 'backend', title: 'Backend Developer', icon: 'server', active: true,
      desc: 'Construir APIs, bancos e a lógica que move produtos.',
      meta: '~9 domínios · 6–8 meses',
    },
    {
      id: 'data', title: 'Data Engineer', icon: 'database', active: false,
      desc: 'Pipelines, modelagem e infraestrutura de dados.',
      meta: 'Em breve',
    },
    {
      id: 'frontend', title: 'Frontend Developer', icon: 'code', active: false,
      desc: 'Interfaces, performance e experiência do usuário.',
      meta: 'Em breve',
    },
  ];

  const valid = selected && motivation.trim().length >= 20;

  return (
    <div className="container" data-screen="goal-picker">
      <div className="goal-hero">
        <div className="goal-eyebrow"><span className="dot"></span>Passo 1 de 3 · Sonho profissional</div>
        <h1 className="goal-title">Para onde você quer ir?</h1>
        <p className="goal-subtitle">Antes de te dar um plano, precisamos entender seu sonho. Cada trilha é viva e se adapta ao seu ponto de partida.</p>
      </div>

      <div className="goal-grid">
        {goals.map(g => (
          <button
            key={g.id}
            className={`goal-card ${selected === g.id ? 'selected' : ''} ${!g.active ? 'disabled' : ''}`}
            onClick={() => g.active && setSelected(g.id)}
            disabled={!g.active}
          >
            <div className="goal-check"><Icon name="check" size={12} stroke={3} /></div>
            <div className="goal-card-icon">
              <Icon name={g.icon} size={18} />
            </div>
            <div>
              <h3 className="goal-card-title">{g.title}</h3>
              <p className="goal-card-desc">{g.desc}</p>
            </div>
            <div className="goal-card-meta">
              {g.active ? (
                <>
                  <Icon name="sprout" size={11} /> {g.meta}
                </>
              ) : (
                <><Icon name="lock" size={11} /> {g.meta}</>
              )}
            </div>
          </button>
        ))}
      </div>

      <div className="goal-motivation">
        <div className="field-label">
          <span>Por que esse caminho?</span>
          <span className="field-hint">{motivation.length}/280 · mín. 20 caracteres</span>
        </div>
        <textarea
          className="textarea"
          placeholder="Quero trabalhar com APIs para space tech..."
          value={motivation}
          onChange={(e) => { setMotivation(e.target.value.slice(0, 280)); setTouched(true); }}
        />
        {touched && motivation.trim().length < 20 && (
          <div style={{ fontSize: 12, color: 'var(--warning)', marginTop: 8, display: 'flex', alignItems: 'center', gap: 6 }}>
            <Icon name="alert" size={12} /> Conte um pouco mais — isso ajuda a IA a personalizar sua trilha.
          </div>
        )}
      </div>

      <div className="goal-footer">
        <div className="goal-footer-note">
          <Icon name="sparkles" size={14} />
          A IA usa sua motivação para personalizar exemplos e projetos.
        </div>
        <button className="btn btn-primary btn-lg" disabled={!valid} onClick={onNext}>
          Começar diagnóstico <Icon name="arrowRight" size={14} />
        </button>
      </div>
    </div>
  );
};

// === Screen 2: Diagnostic Chat ===
const DiagnosticScreen = ({ onNext }) => {
  const initial = [
    { from: 'ai',   t: '14:02', text: 'Oi! Sou o Career Forge. Vou te fazer algumas perguntas para entender de onde você está partindo. Sem certo ou errado — quanto mais honesto, mais útil sua trilha.' },
    { from: 'ai',   t: '14:02', text: 'Você já usou Git em algum projeto?' },
    { from: 'user', t: '14:03', text: 'Sim, subi um projeto no GitHub mas não domino branches.' },
    { from: 'ai',   t: '14:03', text: 'Beleza. Consegue explicar com suas palavras a diferença entre frontend e backend?' },
    { from: 'user', t: '14:04', text: 'Frontend é o que o usuário vê (botões, telas). Backend é o que processa os dados e fica no servidor.' },
    { from: 'ai',   t: '14:04', text: 'Perfeito. Você já fez alguma requisição HTTP — chamou uma API, mesmo que pelo navegador?' },
    { from: 'user', t: '14:05', text: 'Acho que sim, mas nunca prestei atenção em métodos ou status codes.' },
    { from: 'ai',   t: '14:06', text: 'Última: quando você pensa em "criar um usuário", o que vem primeiro à sua mente — uma tela, um banco de dados, ou uma requisição?' },
  ];
  const [messages, setMessages] = React.useState(initial);
  const [draft, setDraft] = React.useState('Acho que uma tela com formulário... mas o backend salva no banco.');
  const [isTyping, setIsTyping] = React.useState(false);
  const [generating, setGenerating] = React.useState(false);
  const streamRef = React.useRef(null);

  React.useEffect(() => {
    if (streamRef.current) streamRef.current.scrollTop = streamRef.current.scrollHeight;
  }, [messages, isTyping, generating]);

  const send = () => {
    if (!draft.trim()) return;
    setMessages(m => [...m, { from: 'user', t: '14:07', text: draft.trim() }]);
    setDraft('');
    setIsTyping(true);
    setTimeout(() => {
      setIsTyping(false);
      setMessages(m => [...m, { from: 'ai', t: '14:07', text: 'Ótimo. Tenho contexto suficiente para gerar seu diagnóstico inicial.' }]);
      setTimeout(() => setGenerating(true), 600);
      setTimeout(() => onNext(), 2400);
    }, 1400);
  };

  const answered = messages.filter(m => m.from === 'user').length;
  const total = 4;
  const pct = Math.min(100, Math.round((answered / total) * 100));

  return (
    <div className="diag-layout" data-screen="diagnostic">
      <aside className="diag-recap">
        <div className="card recap-card">
          <div className="recap-eyebrow">Seu sonho</div>
          <div className="recap-goal">
            <Icon name="server" size={14} />
            Backend Developer
          </div>
          <div className="recap-motiv">
            <Icon name="quote" size={10} /> Quero trabalhar com APIs para space tech — sonho em escrever os sistemas que orquestram lançamentos de foguetes.
          </div>
          <div className="recap-progress">
            <div className="progress-label">
              <span>Diagnóstico</span>
              <span>{answered}/{total}</span>
            </div>
            <div className="progress-rail"><div className="progress-fill" style={{ width: `${pct}%` }}></div></div>
          </div>

          <div style={{ marginTop: 18, paddingTop: 18, borderTop: '1px solid var(--border-soft)' }}>
            <div className="recap-eyebrow">O que a IA está mapeando</div>
            <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: 8, fontSize: 12, color: 'var(--text-2)' }}>
              <li style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                <span style={{ width: 6, height: 6, borderRadius: 999, background: 'var(--success)' }}></span>
                Familiaridade com Git
              </li>
              <li style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                <span style={{ width: 6, height: 6, borderRadius: 999, background: 'var(--success)' }}></span>
                Modelo mental cliente/servidor
              </li>
              <li style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                <span style={{ width: 6, height: 6, borderRadius: 999, background: 'var(--warning)' }}></span>
                Camada HTTP e APIs
              </li>
              <li style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                <span style={{ width: 6, height: 6, borderRadius: 999, background: 'var(--text-3)' }}></span>
                Persistência (em análise)
              </li>
            </ul>
          </div>
        </div>
      </aside>

      <div className="card chat-panel">
        <div className="chat-header">
          <div className="chat-step">Passo <b>2/3</b> · Diagnóstico inicial</div>
          <div className="row" style={{ gap: 6, fontSize: 11, color: 'var(--text-3)', fontFamily: 'var(--font-mono)' }}>
            <span className="pill-dot" style={{ background: 'var(--success)' }}></span>
            IA conectada
          </div>
        </div>
        <div className="chat-stream" ref={streamRef}>
          {messages.map((m, i) => (
            <Bubble key={i} from={m.from} time={m.t}>{m.text}</Bubble>
          ))}
          {isTyping && (
            <Bubble from="ai" time="14:07">
              <div className="typing"><span></span><span></span><span></span></div>
            </Bubble>
          )}
          {generating && (
            <div className="gen-skeleton">
              <div className="spinner"></div>
              <div className="gen-skeleton-text">
                <b>Gerando diagnóstico…</b> mapeando 4 sinais nas suas respostas.
              </div>
            </div>
          )}
        </div>
        <div className="chat-input-row">
          <input
            className="chat-input"
            placeholder="Escreva sua resposta..."
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter') send(); }}
            disabled={generating}
          />
          <button className="send-btn" onClick={send} disabled={!draft.trim() || generating}>
            <Icon name="send" size={16} />
          </button>
        </div>
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
