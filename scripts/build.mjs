import { copyFile, cp, mkdir, readFile, rm, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const projectRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const outputDirectory = resolve(projectRoot, "dist");
const localUrl = `http://127.0.0.1:${process.env.PORT || 8000}`;
const siteUrl = (process.env.URL || process.env.SITE_URL || localUrl).replace(/\/$/, "");

if (!/^https?:\/\//.test(siteUrl)) {
  throw new Error(`URL de site invalide : ${siteUrl}`);
}

await rm(outputDirectory, { recursive: true, force: true });
await mkdir(outputDirectory, { recursive: true });

for (const file of ["app.js", "favicon.svg", "site.webmanifest"]) {
  await copyFile(resolve(projectRoot, file), resolve(outputDirectory, file));
}

await cp(resolve(projectRoot, "data"), resolve(outputDirectory, "data"), { recursive: true });

const sourceHtml = await readFile(resolve(projectRoot, "index.html"), "utf8");
await writeFile(
  resolve(outputDirectory, "index.html"),
  sourceHtml.replaceAll("__SITE_URL__", siteUrl),
  "utf8",
);

await writeFile(
  resolve(outputDirectory, "robots.txt"),
  `User-agent: *\nAllow: /\n\nSitemap: ${siteUrl}/sitemap.xml\n`,
  "utf8",
);

await writeFile(
  resolve(outputDirectory, "sitemap.xml"),
  `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n  <url>\n    <loc>${siteUrl}/</loc>\n  </url>\n</urlset>\n`,
  "utf8",
);

console.log(`Site construit dans dist/ pour ${siteUrl}`);
