// Copy the web app's static files into www/, which Capacitor bundles into the
// native app. The web app (../subtitle-player) stays the single source of
// truth; run `npm run sync` after changing it to refresh the bundle.
import { cpSync, mkdirSync, rmSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, "..");
const src = process.env.WEB_SRC || join(root, "..", "subtitle-player");
const dest = join(root, "www");

// Files the app actually loads. The service worker and PWA manifest are
// redundant inside the native WebView but harmless, and keeping them means the
// bundled files match the hosted site exactly.
const files = [
  "index.html",
  "manifest.json",
  "sw.js",
  "icon-192.png",
  "icon-512.png",
  "icon-maskable-512.png",
  "apple-touch-icon.png",
];

rmSync(dest, { recursive: true, force: true });
mkdirSync(dest, { recursive: true });
for (const f of files) {
  cpSync(join(src, f), join(dest, f));
}
console.log(`Synced ${files.length} files from ${src} -> www/`);
