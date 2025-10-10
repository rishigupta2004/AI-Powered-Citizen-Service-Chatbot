import { apiFetch } from '../../../lib/api';

export default async function ServiceDetailPage({ params }: { params: { slug: string } }) {
  const endpoints = await apiFetch<any[]>(`/api/service-endpoints/${params.slug}`);
  return (
    <main className="mx-auto max-w-5xl p-6">
      <h1 className="text-2xl font-semibold">{params.slug}</h1>
      <div className="mt-4 space-y-2">
        {endpoints.map((e, i) => (
          <div key={i} className="rounded border p-3">
            <div className="font-medium">{e.endpoint_name || 'Endpoint'}</div>
            <div className="text-sm text-muted-foreground">{e.api_service}</div>
          </div>
        ))}
      </div>
    </main>
  );
}

