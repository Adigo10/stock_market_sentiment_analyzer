import { createServer } from 'node:http';
import { createReadStream, promises as fs } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const distDir = path.join(__dirname, 'dist');
const fallbackFile = path.join(distDir, 'index.html');

const mimeTypes = {
  '.html': 'text/html; charset=UTF-8',
  '.js': 'application/javascript',
  '.css': 'text/css',
  '.json': 'application/json',
  '.ico': 'image/x-icon',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
  '.ttf': 'font/ttf'
};

const port = process.env.PORT || 4173;

const server = createServer(async (req, res) => {
  try {
    const url = new URL(req.url ?? '/', `http://${req.headers.host}`);
    let pathname = decodeURIComponent(url.pathname);
    if (pathname.endsWith('/')) {
      pathname = path.join(pathname, 'index.html');
    }

    const filePath = path.join(distDir, pathname);

    if (!filePath.startsWith(distDir)) {
      res.writeHead(403);
      res.end('Forbidden');
      return;
    }

    const stat = await fs.stat(filePath).catch(() => null);
    if (!stat || !stat.isFile()) {
      await streamFile(fallbackFile, res);
      return;
    }

    await streamFile(filePath, res);
  } catch (error) {
    res.writeHead(500);
    res.end('Internal Server Error');
    console.error('Static server error:', error);
  }
});

function streamFile(targetPath, res) {
  return new Promise((resolve, reject) => {
    const ext = path.extname(targetPath).toLowerCase();
    const contentType = mimeTypes[ext] || 'application/octet-stream';
    res.writeHead(200, { 'Content-Type': contentType });
    const stream = createReadStream(targetPath);
    stream.on('error', reject);
    stream.on('end', resolve);
    stream.pipe(res);
  });
}

server.listen(port, '0.0.0.0', () => {
  console.log(`Static frontend listening on ${port}`);
});
