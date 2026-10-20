// Finds Playwright wherever this machine has it: PW_PATH, the Claude workspace's copy, or a normal npm install.
const tries = [process.env.PW_PATH, '/opt/npm-tools/node_modules/playwright', 'playwright'].filter(Boolean);
let pw = null;
for (const t of tries) { try { pw = require(t); break; } catch (e) { /* next */ } }
if (!pw) throw new Error('Playwright not found. Run "npm i playwright" or set PW_PATH.');
module.exports = pw;
