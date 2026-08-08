//#region node_modules/.nitro/vite/services/ssr/index.js
/**
* Lightweight SSR error capture.
*
* TanStack Start's h3 layer swallows in-handler throws into a plain 500 JSON
* response, so try/catch alone can't surface them. This module keeps a reference
* to the last error that passed through console.error so the server entry can
* attribute the swallowed response to the real cause.
*/
var lastError = null;
function reportError(error) {
	lastError = error instanceof Error ? error : new Error(String(error));
}
function consumeLastCapturedError() {
	const error = lastError;
	lastError = null;
	return error;
}
var originalConsoleError = console.error;
console.error = ((...args) => {
	originalConsoleError(...args);
	const error = args.find((arg) => arg instanceof Error);
	if (error) reportError(error);
});
/** Minimal static HTML fallback rendered when SSR itself fails to produce a page. */
function renderErrorPage() {
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
var serverEntryPromise;
async function getServerEntry() {
	if (!serverEntryPromise) serverEntryPromise = import("./server-CLPlQy29.mjs").then((m) => m.default ?? m);
	return serverEntryPromise;
}
async function normalizeCatastrophicSsrResponse(response) {
	if (response.status < 500) return response;
	if (!(response.headers.get("content-type") ?? "").includes("application/json")) return response;
	const body = await response.clone().text();
	if (!isH3SwallowedErrorBody(body)) return response;
	console.error(consumeLastCapturedError() ?? /* @__PURE__ */ new Error(`h3 swallowed SSR error: ${body}`));
	return new Response(renderErrorPage(), {
		status: 500,
		headers: { "content-type": "text/html; charset=utf-8" }
	});
}
function isH3SwallowedErrorBody(body) {
	try {
		const payload = JSON.parse(body);
		return payload.unhandled === true && payload.message === "HTTPError";
	} catch {
		return false;
	}
}
var server_default = { async fetch(request, env, ctx) {
	try {
		return await normalizeCatastrophicSsrResponse(await (await getServerEntry()).fetch(request, env, ctx));
	} catch (error) {
		console.error(error);
		return new Response(renderErrorPage(), {
			status: 500,
			headers: { "content-type": "text/html; charset=utf-8" }
		});
	}
} };
//#endregion
export { server_default as default, renderErrorPage as t };
