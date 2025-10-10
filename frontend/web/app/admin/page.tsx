import { apiFetch } from '../../lib/api';

export default async function AdminPage() {
  const health = await apiFetch<{ status: string; timestamp: number }>(`/health`);
  const metrics = await apiFetch<any>(`/metrics`);
  return (
    <main className="mx-auto max-w-5xl p-6">
      <h1 className="text-2xl font-semibold">Admin</h1>
      <section className="mt-4">
        <h2 className="font-medium">System Health</h2>
        <pre className="rounded bg-gray-50 p-3 overflow-auto" aria-label="System health">{JSON.stringify(health, null, 2)}</pre>
      </section>
      <section className="mt-4">
        <h2 className="font-medium">Metrics</h2>
        <pre className="rounded bg-gray-50 p-3 overflow-auto" aria-label="Metrics">{JSON.stringify(metrics, null, 2)}</pre>
      </section>
    </main>
  );
}

