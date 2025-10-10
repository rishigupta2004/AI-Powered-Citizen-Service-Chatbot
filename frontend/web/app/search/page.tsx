"use client";
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { apiFetch } from '../../lib/api';

export default function SearchPage() {
  const { t, i18n } = useTranslation();
  const [q, setQ] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const data = await apiFetch('/search', { method: 'POST', body: { query: q, limit: 10 } });
      setResults(data.results || []);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto max-w-5xl p-6" aria-label="Search Results">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">{t('services')}</h1>
        <label className="text-sm">
          {t('language')}: 
          <select className="ml-2 border rounded px-2 py-1" value={i18n.language} onChange={(e)=>i18n.changeLanguage(e.target.value)} aria-label="Language">
            <option value="en">English</option>
            <option value="hi">हिन्दी</option>
          </select>
        </label>
      </div>
      <form onSubmit={onSubmit} className="mt-4 flex gap-2" role="search" aria-label="Search form">
        <input value={q} onChange={(e)=>setQ(e.target.value)} placeholder={t('search_placeholder') as string} className="flex-1 rounded-md border px-3 py-2" aria-label="Query" />
        <button className="rounded-md bg-black text-white px-4 py-2" aria-label="Search Button">{t('search')}</button>
      </form>
      <section className="mt-6" aria-live="polite">
        {loading ? <p>Loading…</p> : (
          <ul className="space-y-3">
            {results.map((r, idx) => (
              <li key={idx} className="rounded border p-3" role="article">
                <h2 className="font-medium">{r.title || 'Result'}</h2>
                <p className="text-sm text-muted-foreground">{r.snippet}</p>
                {r.category ? <span className="text-xs">{r.category}</span> : null}
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}

