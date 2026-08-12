import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

async function render() {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);

  return worker.fetch(
    new Request("http://localhost/", { headers: { accept: "text/html" } }),
    { ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) } },
    { waitUntil() {}, passThroughOnException() {} },
  );
}

test("server-renders the birthday letter without exposing closed messages", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);

  const html = await response.text();
  assert.match(html, /<title>당신의 마흔 번째 계절<\/title>/);
  assert.match(html, /당신의 마흔 번째 계절이/);
  assert.match(html, /마흔 가지 이유/);
  assert.match(html, /마지막 편지 열기/);
  assert.doesNotMatch(html, /당신이 웃으면 집 안의 공기가 달라져요/);
  assert.doesNotMatch(html, /codex-preview|Your site is taking shape/);
});

test("keeps the first screen resilient and the reason cards accessible", async () => {
  const [page, css, packageJson] = await Promise.all([
    readFile(new URL("../app/page.tsx", import.meta.url), "utf8"),
    readFile(new URL("../app/globals.css", import.meta.url), "utf8"),
    readFile(new URL("../package.json", import.meta.url), "utf8"),
  ]);

  assert.doesNotMatch(page, /introDone|setTimeout\(|useEffect/);
  assert.match(page, /aria-expanded=\{isOpen\}/);
  assert.match(page, /isOpen && <span className="reason-text">\{reason\}<\/span>/);
  assert.doesNotMatch(css, /\.page\s*\{[^}]*opacity:\s*0/s);
  assert.match(css, /@keyframes pageReveal/);
  assert.match(css, /@keyframes openingForty/);
  assert.match(css, /@keyframes cardSpark/);
  assert.match(css, /rotateY\(180deg\)/);
  assert.match(css, /:focus-visible/);
  assert.match(packageJson, /node scripts\/vinext\.mjs build/);
  assert.doesNotMatch(packageJson, /react-loading-skeleton|drizzle|tailwind/);
});
