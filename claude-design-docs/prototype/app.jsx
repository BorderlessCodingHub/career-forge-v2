// Career Forge — App shell with navigation
const App = () => {
  const [screen, setScreen] = React.useState('goal');
  const [mentorOpen, setMentorOpen] = React.useState(false);

  // Allow URL hash for deep-linking individual screens during review
  React.useEffect(() => {
    const fromHash = () => {
      const h = window.location.hash.replace('#', '');
      if (['goal', 'diag', 'result', 'forge', 'roadmap', 'validate', 'adaptive'].includes(h)) setScreen(h);
    };
    fromHash();
    window.addEventListener('hashchange', fromHash);
    return () => window.removeEventListener('hashchange', fromHash);
  }, []);

  const nav = (id) => {
    setScreen(id);
    window.location.hash = id;
    setMentorOpen(false);
    window.scrollTo({ top: 0, behavior: 'instant' });
  };

  return (
    <div className="app">
      <TopNav current={screen} onNav={nav} />

      <div className={`screen ${screen === 'goal' ? 'active' : ''}`}>
        <GoalPickerScreen onNext={() => nav('diag')} />
      </div>

      <div className={`screen ${screen === 'diag' ? 'active' : ''}`}>
        {screen === 'diag' && <DiagnosticScreen onNext={() => nav('result')} />}
      </div>

      <div className={`screen ${screen === 'result' ? 'active' : ''}`}>
        <DiagnosisResultScreen onNext={() => nav('forge')} />
      </div>

      <div className={`screen ${screen === 'forge' ? 'active' : ''}`}>
        {screen === 'forge' && <ForgeScreen onReveal={() => nav('roadmap')} />}
      </div>

      <div className={`screen ${screen === 'roadmap' ? 'active' : ''}`}>
        {screen === 'roadmap' && (
          <RoadmapScreen
            adaptive={false}
            onValidate={() => nav('validate')}
            onMentor={() => setMentorOpen(true)}
            mentorOpen={mentorOpen}
            onCloseMentor={() => setMentorOpen(false)}
          />
        )}
      </div>

      <div className={`screen ${screen === 'validate' ? 'active' : ''}`}>
        {screen === 'validate' && (
          <ValidationScreen
            onPass={() => nav('roadmap')}
            onFail={() => nav('adaptive')}
            onBack={() => nav('roadmap')}
          />
        )}
      </div>

      <div className={`screen ${screen === 'adaptive' ? 'active' : ''}`}>
        {screen === 'adaptive' && (
          <RoadmapScreen
            adaptive={true}
            onValidate={() => nav('validate')}
            onMentor={() => setMentorOpen(true)}
            mentorOpen={mentorOpen}
            onCloseMentor={() => setMentorOpen(false)}
          />
        )}
      </div>
    </div>
  );
};

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
