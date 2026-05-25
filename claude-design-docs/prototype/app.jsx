// Career Forge — App shell with navigation
// Modes: setup (onboarding + forge) vs artifact (finished trail / roadmap.sh view)
const ARTIFACT_SCREENS = ['roadmap', 'adaptive'];
const SETUP_SCREENS = ['goal', 'diag', 'result', 'forge', 'validate'];

const App = () => {
  const [screen, setScreen] = React.useState('goal');
  const [mentorOpen, setMentorOpen] = React.useState(false);

  const appMode = ARTIFACT_SCREENS.includes(screen) ? 'artifact' : 'setup';

  // Allow URL hash for deep-linking individual screens during review
  React.useEffect(() => {
    const fromHash = () => {
      const h = window.location.hash.replace('#', '');
      if ([...SETUP_SCREENS, ...ARTIFACT_SCREENS].includes(h)) setScreen(h);
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
    <div className={`app mode-${appMode}`}>
      <TopNav current={screen} onNav={nav} mode={appMode} trackName="Backend Developer" />

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
            mode="artifact"
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
            mode="artifact"
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
