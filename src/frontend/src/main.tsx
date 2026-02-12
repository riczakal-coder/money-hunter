import { StrictMode, Component } from 'react'
import type { ReactNode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

// 💥 에러 방지턱 (Error Boundary)
// 흰 화면 대신 에러 내용을 화면에 출력해줍니다.
class ErrorBoundary extends Component<{ children: ReactNode }, { hasError: boolean, error: Error | null }> {
  constructor(props: any) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '20px', color: '#ff6b6b', background: '#1e1e1e', height: '100vh', fontFamily: 'monospace' }}>
          <h2 style={{ fontSize: '24px', marginBottom: '10px' }}>💥 Application Error</h2>
          <pre style={{ whiteSpace: 'pre-wrap', backgroundColor: '#000', padding: '10px', borderRadius: '5px' }}>
            {this.state.error?.message || this.state.error?.toString()}
          </pre>
          <div style={{ marginTop: '20px', color: '#aaa' }}>
            <p><strong>[해결 방법]</strong></p>
            <p>1. <code>lucide-react</code> 또는 <code>tailwindcss</code>가 설치되지 않았을 수 있습니다.</p>
            <p>2. 터미널에서 <code>npm install</code>을 다시 실행해주세요.</p>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </StrictMode>,
)
