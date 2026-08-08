/** Minimal static HTML fallback rendered when SSR itself fails to produce a page. */
export function renderErrorPage(): string {
  return `<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Something went wrong</title>
    <style>
      * { box-sizing: border-box; }
      body {
        margin: 0;
        min-height: 100vh;
        display: grid;
        place-items: center;
        background: #0f172a;
        color: #f8fafc;
        font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
      }
      .card { text-align: center; padding: 2rem; }
      h1 { font-size: 1.5rem; margin: 0 0 0.5rem; }
      p { color: #94a3b8; margin: 0.25rem 0; }
    </style>
  </head>
  <body>
    <div class="card">
      <h1>Something went wrong</h1>
      <p>The server encountered an error while rendering this page.</p>
      <p>Please try again shortly.</p>
    </div>
  </body>
</html>`;
}
