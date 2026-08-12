import assert from "node:assert/strict";
import { readFile, readdir, stat } from "node:fs/promises";
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
  assert.match(page, /isOpen && \(/);
  assert.match(page, /className="character-art"/);
  assert.doesNotMatch(css, /\.page\s*\{[^}]*opacity:\s*0/s);
  assert.match(css, /@keyframes pageReveal/);
  assert.match(css, /@keyframes openingForty/);
  assert.match(css, /@keyframes cardSpark/);
  assert.match(css, /rotateY\(180deg\)/);
  assert.match(css, /:focus-visible/);
  assert.match(packageJson, /node scripts\/vinext\.mjs build/);
  assert.doesNotMatch(packageJson, /react-loading-skeleton|drizzle|tailwind/);
});

test("includes the photo-free one-minute birthday film", async () => {
  const [page, css, video, poster] = await Promise.all([
    readFile(new URL("../app/page.tsx", import.meta.url), "utf8"),
    readFile(new URL("../app/globals.css", import.meta.url), "utf8"),
    stat(new URL("../public/birthday-film.mp4", import.meta.url)),
    stat(new URL("../public/birthday-film-poster.jpg", import.meta.url)),
  ]);

  assert.match(page, /src="\.\/birthday-film\.mp4"/);
  assert.match(page, /poster="\.\/birthday-film-poster\.jpg"/);
  assert.match(page, /playsInline/);
  assert.match(page, /1분 영화 시작하기/);
  assert.match(css, /aspect-ratio:\s*9\s*\/\s*16/);
  assert.ok(video.size > 1_000_000 && video.size < 100_000_000);
  assert.ok(poster.size > 10_000);
});

test("evenly distributes forty lightweight character illustrations", async () => {
  const [page, css, files] = await Promise.all([
    readFile(new URL("../app/page.tsx", import.meta.url), "utf8"),
    readFile(new URL("../app/globals.css", import.meta.url), "utf8"),
    readdir(new URL("../public/characters", import.meta.url)),
  ]);
  const artwork = files.filter((file) => file.endsWith(".webp"));

  assert.equal(artwork.length, 40);
  assert.equal(artwork.filter((file) => file.startsWith("playmobil-")).length, 10);
  assert.equal(artwork.filter((file) => file.startsWith("demon-slayer-")).length, 10);
  assert.equal(artwork.filter((file) => file.startsWith("jujutsu-kaisen-")).length, 10);
  assert.equal(artwork.filter((file) => file.startsWith("my-hero-academia-")).length, 10);
  assert.match(page, /index % characterSeries\.length/);
  assert.match(page, /loading="lazy"/);
  assert.match(page, /decoding="async"/);
  assert.match(css, /@keyframes characterReveal/);
  assert.match(css, /\.character-art::after/);
});

test("adds scattered cat photos with optional occasional sounds", async () => {
  const [page, css, cats, sounds] = await Promise.all([
    readFile(new URL("../app/page.tsx", import.meta.url), "utf8"),
    readFile(new URL("../app/globals.css", import.meta.url), "utf8"),
    readdir(new URL("../public/cats", import.meta.url)),
    readdir(new URL("../public/sounds", import.meta.url)),
  ]);

  assert.equal(cats.filter((file) => file.endsWith(".webp")).length, 6);
  assert.equal(sounds.filter((file) => file.endsWith(".wav")).length, 3);
  assert.match(page, /const catSoundCards = new Map/);
  assert.match(page, /cat-sound-toggle/);
  assert.match(page, /aria-pressed=\{catSoundEnabled\}/);
  assert.match(page, /new Audio\(catSoundSources\[soundIndex\]\)/);
  assert.match(page, /sound\.volume = 0\.24/);
  assert.match(page, /filmPlaying\) return/);
  assert.match(css, /\.cat-interlude/);
  assert.match(css, /\.cat-photo-one/);
});

test("exports a relative-path static site for GitHub Pages", async () => {
  const [page, exporter, workflow] = await Promise.all([
    readFile(new URL("../app/page.tsx", import.meta.url), "utf8"),
    readFile(new URL("../scripts/export-github-pages.mjs", import.meta.url), "utf8"),
    readFile(new URL("../.github/workflows/deploy-pages.yml", import.meta.url), "utf8"),
  ]);

  assert.match(page, /src: `\.\/characters\//);
  assert.match(page, /"\.\/cats\//);
  assert.match(page, /"\.\/sounds\//);
  assert.match(exporter, /dist\/client/);
  assert.match(exporter, /\.nojekyll/);
  assert.match(workflow, /actions\/checkout@v6/);
  assert.match(workflow, /actions\/configure-pages@v5/);
  assert.match(workflow, /actions\/upload-pages-artifact@v4/);
  assert.match(workflow, /actions\/deploy-pages@v4/);
});
