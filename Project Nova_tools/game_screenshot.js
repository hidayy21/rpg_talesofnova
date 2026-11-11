// Screenshots from the running game (all plugins and shaders on), without opening RPG Maker:
// serves the project on localhost, runs it in headless Microsoft Edge through the DevTools protocol, starts a new
// game on each map asked for and saves what the screen shows.
//   node game_screenshot.js <shots.json> <out_dir>
// shots.json: [{ "name": "garden", "map": 48, "x": 21, "y": 26, "dir": 2,
//               "override": { "cinematic": 0 },      NovaAtmosphere map-tag overrides (optional)
//               "switches": { "10": true },           (optional)
//               "bars": true, "message": ["Line"] ,   letterbox / a message box (optional)
//               "frames": 120 }]                      frames to wait after arriving (optional)
const fs = require('fs'), path = require('path'), http = require('http'), { spawn } = require('child_process');

const ROOT = path.resolve(__dirname, '..');
const EDGE = ['C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
              'C:/Program Files/Microsoft/Edge/Application/msedge.exe',
              '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
              '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'].find(p => fs.existsSync(p));
const [shotsFile, outDir] = process.argv.slice(2);
const shots = JSON.parse(fs.readFileSync(shotsFile, 'utf8'));
// the game's screen size comes from Community_Basic in js/plugins.js
const plugins = JSON.parse(fs.readFileSync(path.join(ROOT, 'js/plugins.js'), 'utf8').replace(/^[^\[]*/, '').replace(/;\s*$/, ''));
const basic = (plugins.find(p => p.name === 'Community_Basic') || { parameters: {} }).parameters;
const W = Number(basic.screenWidth) || 816, H = Number(basic.screenHeight) || 624, PORT = 8777, DEBUG = 9333;
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.png': 'image/png',
                '.ogg': 'audio/ogg', '.m4a': 'audio/mp4', '.ttf': 'font/ttf', '.woff': 'font/woff', '.css': 'text/css' };

const server = http.createServer((req, res) => {
  const file = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
  if (!file.startsWith(ROOT) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': TYPES[path.extname(file).toLowerCase()] || 'application/octet-stream' });
  fs.createReadStream(file).pipe(res);
}).listen(PORT, '127.0.0.1');

const sleep = ms => new Promise(r => setTimeout(r, ms));

async function main() {
  fs.mkdirSync(outDir, { recursive: true });
  const profile = fs.mkdtempSync(path.join(require('os').tmpdir(), 'nova-shot-'));
  const edge = spawn(EDGE, ['--headless=new', '--remote-debugging-port=' + DEBUG, '--user-data-dir=' + profile,
    '--window-size=' + W + ',' + H, '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--mute-audio',
    '--autoplay-policy=no-user-gesture-required', 'about:blank'], { stdio: 'ignore' });
  let target;
  for (let i = 0; i < 50 && !target; i++) {
    await sleep(200);
    try { target = (await (await fetch('http://127.0.0.1:' + DEBUG + '/json')).json()).find(t => t.type === 'page'); } catch (e) {}
  }
  const ws = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise(r => ws.addEventListener('open', r));
  let id = 0; const wait = {};
  ws.addEventListener('message', ev => { const m = JSON.parse(ev.data); if (m.id && wait[m.id]) { wait[m.id](m); delete wait[m.id]; } });
  const send = (method, params = {}) => new Promise(r => { const n = ++id; wait[n] = r; ws.send(JSON.stringify({ id: n, method, params })); });
  const js = async expr => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true });
    if (r.result.exceptionDetails) throw new Error(r.result.exceptionDetails.exception.description);
    return r.result.result.value;
  };
  const until = async (expr, ms = 30000) => {
    for (let t = 0; t < ms; t += 250) { if (await js(expr)) return; await sleep(250); }
    const why = await js("String(SceneManager._scene && SceneManager._scene.constructor.name) + ' | ' + (window.__novaErr || 'no error')").catch(e => String(e));
    throw new Error('timeout: ' + expr + ' -- scene / last error: ' + why);
  };

  await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: false });
  await send('Page.navigate', { url: 'http://127.0.0.1:' + PORT + '/index.html' });
  await until("typeof DataManager !== 'undefined' && DataManager.isDatabaseLoaded() && SceneManager._scene && /Title|Map/.test(SceneManager._scene.constructor.name)", 60000);
  await js("document.body.style.overflow = 'hidden'");
  await js("window.addEventListener('error', function(e) { window.__novaErr = e.message + ' ' + (e.error && e.error.stack || ''); }); 1");
  console.log('renderer:', await js('Graphics.isWebGL() ? "WebGL" : "canvas"'));
  const boot = async () => {
    await send('Page.navigate', { url: 'http://127.0.0.1:' + PORT + '/index.html' });
    await until("typeof DataManager !== 'undefined' && DataManager.isDatabaseLoaded() && SceneManager._scene && /Title|Map/.test(SceneManager._scene.constructor.name)", 60000);
  };
  for (const s of shots) {
   for (let attempt = 0; ; attempt++) {
   try {
    await js(`(function(){
      NovaAtmosphere.override = ${JSON.stringify(s.override || {})};
      DataManager.setupNewGame();
      ${Object.entries(s.switches || {}).map(([k, v]) => `$gameSwitches.setValue(${k}, ${!!v});`).join('')}
      $gameSystem._novaBars = ${s.bars ? "'on'" : "'off'"};
      $gamePlayer.reserveTransfer(${s.map}, ${s.x}, ${s.y}, ${s.dir || 2}, 2);
      SceneManager.goto(Scene_Map);
    })()`);
    await until("SceneManager._scene instanceof Scene_Map && SceneManager._scene.isReady() && !$gamePlayer.isTransferring() && ImageManager.isReady()");
    if (s.message) await js(`$gameMessage.add(${JSON.stringify(s.message.join('\n'))})`);
    await js(`new Promise(r => { var n = ${s.frames || 120}; (function f(){ if (--n <= 0) r(1); else requestAnimationFrame(f); })(); })`);
    const shot = await send('Page.captureScreenshot', { format: 'png' });
    const file = path.join(outDir, s.name + '.png');
    fs.writeFileSync(file, Buffer.from(shot.result.data, 'base64'));
    console.log('saved', file);
    break;
   } catch (e) {
    if (attempt) throw e;
    console.log('retrying', s.name, '(' + e.message.slice(0, 80) + ')');
    await boot();
   }
   }
  }
  ws.close(); edge.kill(); server.close();
}
main().catch(e => { console.error(e); process.exit(1); }).then(() => process.exit(0));
