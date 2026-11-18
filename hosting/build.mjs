// Publish only release artifacts and privacy information; no Python runtime on Render or Vercel.
import { createHash } from 'node:crypto';
import { copyFile, mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const version = '1.2.0';
const output = path.join(root, 'hosting', 'public');
const downloads = path.join(output, 'descargas', `v${version}`);
const artifacts = [
  { source: 'app/PNG a PDF.exe', checksum: 'app/SHA256SUMS.txt', name: `PNG-a-PDF-${version}.exe` },
  { source: `instalador/PNG-a-PDF-Setup-${version}.exe`, checksum: 'instalador/SHA256SUMS.txt', name: `PNG-a-PDF-Setup-${version}.exe` },
];
const hash = bytes => createHash('sha256').update(bytes).digest('hex');

// Check the existing release before publishing any bytes.
const appSource = await readFile(path.join(root, 'png_a_pdf.py'), 'utf8');
if (!appSource.includes(`VERSION = "${version}"`)) {
  throw new Error('Actualiza la version y las rutas de hosting/build.mjs antes de publicar otra version.');
}
const sums = [];
for (const artifact of artifacts) {
  const content = await readFile(path.join(root, artifact.source));
  const manifest = await readFile(path.join(root, artifact.checksum), 'utf8');
  const sourceName = path.posix.basename(artifact.source);
  const digest = hash(content);
  const matches = manifest.split(/\r?\n/).some(line => {
    const match = line.trim().match(/^([a-f0-9]{64})\s+\*?(.+)$/i);
    return match && match[1].toLowerCase() === digest && match[2] === sourceName;
  });
  if (!matches) throw new Error(`La suma SHA-256 no coincide: ${artifact.source}`);
  sums.push(`${digest}  ${artifact.name}`);
}

await mkdir(downloads, { recursive: true });
for (let index = 0; index < artifacts.length; index++) {
  const artifact = artifacts[index];
  const destination = path.join(downloads, artifact.name);
  await copyFile(path.join(root, artifact.source), destination);
  if (hash(await readFile(destination)) !== sums[index].slice(0, 64)) {
    throw new Error(`Error de copia: ${artifact.name}`);
  }
}
await writeFile(path.join(downloads, 'SHA256SUMS.txt'), sums.join('\n') + '\n');
await copyFile(path.join(root, 'PRIVACIDAD.md'), path.join(output, 'privacidad.txt'));
await copyFile(path.join(root, 'assets', 'app.png'), path.join(output, 'icono.png'));

const escapeHtml = value => value.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');
const policy = await readFile(path.join(root, 'PRIVACIDAD.md'), 'utf8');
await writeFile(path.join(output, 'privacidad.html'), `<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Privacidad · PNG a PDF</title><body><main><pre style="white-space:pre-wrap;font:16px/1.6 system-ui;max-width:800px;margin:40px auto;padding:16px">${escapeHtml(policy)}</pre></main></body></html>`);
await writeFile(path.join(output, 'index.html'), `<!doctype html>
<html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Descargas · PNG a PDF</title>
<body style="font:16px/1.6 system-ui;max-width:760px;margin:48px auto;padding:24px">
<img src="/icono.png" alt="" width="72" height="72"><h1>PNG a PDF ${version}</h1>
<p>Aplicación de escritorio en español para Windows x64. Convierte carpetas PNG a PDF con vista previa y orden personalizable.</p>
<ul>${artifacts.map(a => `<li><a href="/descargas/v${version}/${a.name}">${a.name.includes('Setup') ? 'Instalador para Windows' : 'Aplicación portátil'}</a></li>`).join('')}<li><a href="/descargas/v${version}/SHA256SUMS.txt">Sumas SHA-256</a></li></ul>
<p>Los archivos todavía no tienen firma digital. Este alojamiento no implica aprobación de Microsoft Store.</p>
<p><a href="/privacidad.html">Política de privacidad</a></p>
</body></html>`);
console.log(`Descargas listas: ${artifacts.map(a => `/descargas/v${version}/${a.name}`).join(', ')}`);
