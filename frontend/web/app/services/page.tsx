import { apiFetch } from '../../lib/api';

export default async function ServicesListPage() {
  const services = await apiFetch<any[]>('/api/service-endpoints');
  return (
    <main className="mx-auto max-w-5xl p-6">
      <h1 className="text-2xl font-semibold">Services</h1>
      <ul className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-3" aria-label="Service list">
        {services.map((s: string) => (
          <li key={s} className="rounded border p-3">
            <a href={`/services/${s}`} className="underline" aria-label={`View ${s}`}>{s}</a>
          </li>
        ))}
      </ul>
    </main>
  );
}

