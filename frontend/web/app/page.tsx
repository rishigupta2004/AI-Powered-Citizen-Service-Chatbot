export default function HomePage() {
  return (
    <main className="mx-auto max-w-5xl p-6">
      <h1 className="text-2xl font-semibold">Government Services Portal</h1>
      <p className="text-sm text-muted-foreground mt-2">
        Multilingual search and service discovery powered by the data warehouse.
      </p>
      <div className="mt-6">
        <form action="/search" method="get" className="flex gap-2">
          <input
            name="q"
            placeholder="Search services, documents, procedures..."
            className="flex-1 rounded-md border px-3 py-2"
          />
          <button className="rounded-md bg-black text-white px-4 py-2">Search</button>
        </form>
      </div>
    </main>
  );
}

