import { useEffect, useState } from 'react';
import { fetchDeals } from './api';
import type { Deal } from './api';
import { Zap, RefreshCcw, ExternalLink, Clock, Radio } from 'lucide-react';

// ── 태그 생성 유틸리티 (백엔드 로직 프론트엔드 재현) ──
const getTags = (title: string) => {
  const watchKeywords = ["위스키", "발베니", "맥캘란", "노트북", "4090", "아이패드", "에어팟", "RTX", "5080", "5090", "M5", "갤럭시", "S26", "울트라", "스팀덱", "상품권", "해피머니", "컬쳐", "깊카", "네페", "포인트", "항공권", "오사카", "도쿄", "비즈니스", "호텔", "다이슨", "히비키", "야마자키", "로렉스", "샤넬"];
  const jackpotKeywords = ["역대가", "가격오류", "오류", "대란", "긴급", "90%", "80%", "70%", "0원", "무료", "선착순", "최저가"];

  const tags = [];
  if (jackpotKeywords.some(k => title.includes(k))) tags.push({ label: '🔥 대박', color: 'bg-mh-red text-white shadow-[0_0_10px_#FF4500]' });
  if (watchKeywords.some(k => title.includes(k))) tags.push({ label: '❤️ 관심', color: 'bg-pink-600 text-white shadow-[0_0_10px_#db2777]' });
  return tags;
};

function App() {
  const [deals, setDeals] = useState<Deal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const loadDeals = async (showLoading = false) => {
    try {
      if (showLoading) setLoading(true);
      const data = await fetchDeals();
      setDeals(data);
      setLastUpdated(new Date());
      setError(null);
    } catch (err) {
      console.error("Fetch error:", err);
      setError("Connection Lost");
    } finally {
      if (showLoading) setLoading(false);
    }
  };

  useEffect(() => {
    loadDeals(true);
    const intervalId = setInterval(() => loadDeals(false), 60000);
    return () => clearInterval(intervalId);
  }, []);

  return (
    <div className="min-h-screen bg-mh-black text-white selection:bg-mh-red selection:text-white pb-20">
      {/* ── Header: Dashboard Control ── */}
      <header className="sticky top-0 z-50 backdrop-blur-md bg-black/80 border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="relative w-8 h-8 flex items-center justify-center bg-slate-800 rounded-full border border-slate-700 overflow-hidden">
              <Zap className="w-4 h-4 text-mh-red" />
              {/* Scan Effect */}
              <div className="absolute inset-0 bg-gradient-to-b from-transparent via-mh-red/50 to-transparent translate-y-[-100%] animate-[scan_2s_linear_infinite]" />
            </div>

            <div className="flex flex-col">
              <h1 className="font-brand text-lg font-black tracking-tighter leading-none">
                MONEY <span className="text-mh-red">HUNTER</span>
              </h1>
              <span className="text-[10px] text-slate-500 font-mono tracking-widest">v0.1.0 SYSTEM ONLINE</span>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-xs font-mono text-slate-400 bg-slate-900 px-3 py-1.5 rounded border border-slate-800">
              <span className={`w-2 h-2 rounded-full ${error ? 'bg-red-500' : 'bg-green-500 animate-pulse'}`}></span>
              {error ? 'OFFLINE' : 'LIVE FEED'}
            </div>
            <button
              onClick={() => loadDeals(true)}
              className="p-2 hover:bg-slate-800 rounded-full transition-colors group"
              title="새로고침"
            >
              <RefreshCcw className={`w-4 h-4 text-slate-400 group-hover:text-mh-red transition-colors ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>
      </header>

      {/* ── Main Content ── */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Status Bar */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold flex items-center gap-2">
            <Radio className="w-5 h-5 text-mh-red animate-pulse" />
            Unknown Signals Detected
            <span className="text-xs bg-slate-800 px-2 py-0.5 rounded text-slate-400 ml-2 font-mono">
              COUNT: {deals.length}
            </span>
          </h2>
          <div className="text-xs text-slate-500 font-mono">
            {lastUpdated ? `LAST SCAN: ${lastUpdated.toLocaleTimeString()}` : 'SCANNING...'}
          </div>
        </div>

        {/* Loading State */}
        {loading && deals.length === 0 && (
          <div className="flex flex-col items-center justify-center py-20 text-slate-500 gap-4">
            <RefreshCcw className="w-8 h-8 animate-spin text-mh-red" />
            <span className="font-mono text-sm animate-pulse">ESTABLISHING CONNECTION...</span>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-900/20 border border-red-900 text-red-400 p-4 rounded-lg mb-6 text-sm font-mono flex items-center gap-3">
            <Zap className="w-5 h-5" />
            SYSTEM ERROR: {error}
          </div>
        )}

        {/* Deal Grid */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {deals.map((deal) => {
            const tags = getTags(deal.title);
            const isJackpot = tags.some(t => t.label.includes('대박'));

            return (
              <div
                key={deal.id}
                className={`
                  group relative bg-[#141414] border border-white/5 rounded-xl overflow-hidden hover:border-mh-red/50 transition-all duration-300 hover:shadow-[0_0_30px_-10px_rgba(255,69,0,0.3)]
                  ${isJackpot ? 'ring-1 ring-mh-red/30' : ''}
                `}
              >
                {/* Site Label Badge */}
                <div className="absolute top-3 left-3 z-10 flex gap-2">
                  <span className={`
                    text-[10px] font-bold px-2 py-0.5 rounded backdrop-blur-md border border-white/10
                    ${deal.site_name.includes('ppomppu') ? 'bg-slate-800 text-slate-300' : 'bg-blue-900/50 text-blue-300 border-blue-500/30'}
                  `}>
                    {deal.site_name.toUpperCase()}
                  </span>

                  {/* Dynamic Tags */}
                  {tags.map((tag, idx) => (
                    <span key={idx} className={`text-[10px] font-bold px-2 py-0.5 rounded ${tag.color} animate-pulse`}>
                      {tag.label}
                    </span>
                  ))}
                </div>

                {/* Content Area */}
                <div className="p-5 pt-10 flex flex-col h-full justify-between">
                  <div>
                    <h3 className="text-base font-bold text-slate-200 group-hover:text-mh-red transition-colors line-clamp-2 leading-snug mb-3">
                      {deal.title}
                    </h3>

                    <div className="flex items-center gap-3 text-xs text-slate-500 font-mono mb-4">
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {new Date(deal.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                      {deal.price && (
                        <span className="text-mh-red font-bold text-sm bg-mh-red/10 px-2 py-0.5 rounded">
                          {deal.price}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Action Footer */}
                  <a
                    href={deal.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="mt-auto pt-3 border-t border-white/5 flex items-center justify-between text-xs text-slate-400 group-hover:text-white transition-colors"
                  >
                    <span className="font-mono">ACCESS TARGET</span>
                    <ExternalLink className="w-3 h-3 group-hover:translate-x-1 transition-transform" />
                  </a>
                </div>

                {/* Active scan line effect on hover */}
                <div className="absolute bottom-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-mh-red to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              </div>
            );
          })}
        </div>

        {!loading && deals.length === 0 && !error && (
          <div className="text-center py-20 opacity-50 font-mono text-sm">
            NO SIGNALS DETECTED. WAITING FOR TARGETS...
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
