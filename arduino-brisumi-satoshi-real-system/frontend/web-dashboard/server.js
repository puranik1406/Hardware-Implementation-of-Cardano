import express from 'express';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
app.use(express.static(path.join(__dirname, 'static')));

app.get('/health', (_req, res) => res.json({ ok: true }));

const PORT = process.env.PORT || 8090;
app.listen(PORT, () => console.log(`Dashboard on :${PORT}`));
