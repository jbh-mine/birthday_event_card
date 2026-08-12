import { access, copyFile, writeFile } from "node:fs/promises";

const outputDirectory = new URL("../dist/client/", import.meta.url);
const workerUrl = new URL("../dist/server/index.js", import.meta.url);
workerUrl.searchParams.set("github-pages-export", `${Date.now()}`);

const { default: worker } = await import(workerUrl.href);
const response = await worker.fetch(
  new Request("https://jbh-mine.github.io/", {
    headers: { accept: "text/html" },
  }),
  { ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) } },
  { waitUntil() {}, passThroughOnException() {} },
);

if (!response.ok) {
  throw new Error(`Static page render failed with ${response.status}`);
}

let html = await response.text();
html = html
  .replaceAll('"/_next/', '"./_next/')
  .replaceAll("'/_next/", "'./_next/")
  .replaceAll("/favicon.svg", "./favicon.svg");

if (!html.includes("당신의 마흔 번째 계절") || html.includes('="/_next/')) {
  throw new Error("Exported HTML did not pass the GitHub Pages path check");
}

await access(new URL("./_next/", outputDirectory));
await writeFile(new URL("./index.html", outputDirectory), html, "utf8");
await copyFile(new URL("./index.html", outputDirectory), new URL("./404.html", outputDirectory));
await writeFile(new URL("./.nojekyll", outputDirectory), "", "utf8");

console.log("GitHub Pages export created in dist/client");
