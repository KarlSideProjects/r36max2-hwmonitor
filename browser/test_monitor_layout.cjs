// Run with Playwright available: node browser/test_monitor_layout.cjs
const {chromium}=require('playwright');
const fs=require('node:fs'), path=require('node:path'), http=require('node:http'), assert=require('node:assert/strict');
const root=__dirname;
const actual=process.env.MONITOR_SAMPLE?JSON.parse(fs.readFileSync(process.env.MONITOR_SAMPLE,'utf8')):null;
const host={host:'DB795i',metrics:{cpu:42,gpu:75,ram:65,cpu_temp:66,gpu_temp:62,
 cores:Array.from({length:32},(_,i)=>i*3),ram_used:21*2**30,ram_total:32*2**30,swap:3,
 gpus:[{name:'GPU 1',usage_percent:75,temperature_celsius:62,memory_used_mb:11348,memory_total_mb:16380,memory_percent:69.3},{name:'GPU 2',usage_percent:20,temperature_celsius:58,memory_total_mb:0}],
 network:{per_nic:{eth0:{rate:{rx_bytes_per_s:4e6,tx_bytes_per_s:1e6}},wlan0:{rate:{rx_bytes_per_s:2e5,tx_bytes_per_s:1e5}}}},
 disks:{nvme0n1:{rate:{read_bytes_per_s:3e6,write_bytes_per_s:1e6,read_iops:42,write_iops:20}},sda:{rate:{read_bytes_per_s:1e6,write_bytes_per_s:0,read_iops:4,write_iops:0}}},
 temperatures:{cpu:[{label:'CPU',current:66},{label:'Package',current:64},{label:'NVMe',current:45}]},rx:4.2e6,tx:1.1e6,read:4e6,write:1e6},history:Array.from({length:60},(_,i)=>({cpu:i,gpu:i+10,ram:60,rx:2e6+i*1e4,tx:1e6,read:3e6,write:1e6}))};
const primaryGpu=structuredClone(host.metrics.gpus[0]);
let state={connection:'Connected',count:3,page:1,pages:1,paused:true,detail:'DB795i',selected:'DB795i',hosts:[host]};
const listeners=new Set();
const server=http.createServer((req,res)=>{
 if(req.url==='/control'&&req.method==='POST'){let body='';req.on('data',chunk=>body+=chunk);req.on('end',()=>{const action=JSON.parse(body).action;if(action.startsWith('focus:')){state.focus=action.slice(6);state.panel=state.focus}else if(action==='back'){if(state.focus)state.focus=null;else state.detail=null}res.setHeader('Content-Type','application/json');res.end('{}');for(const stream of listeners)stream.write('data: '+JSON.stringify(state)+'\n\n')})}
 else if(req.url==='/status'){res.setHeader('Content-Type','application/json');res.end(JSON.stringify(state))}
 else if(req.url==='/events'){res.writeHead(200,{'Content-Type':'text/event-stream'});res.write('data: '+JSON.stringify(state)+'\n\n');listeners.add(res);req.on('close',()=>{listeners.delete(res);res.end()})}
 else if(req.url==='/assets/hardware-buddy.svg'){res.setHeader('Content-Type','image/svg+xml');res.end(fs.readFileSync(path.join(root,'assets/hardware-buddy.svg')))}
 else res.end(fs.readFileSync(path.join(root,'monitor.html')))
});
(async()=>{
 await new Promise(r=>server.listen(0,'127.0.0.1',r));
 const browser=await chromium.launch({headless:true,args:['--disable-gpu']});
 try{
  const page=await browser.newPage({viewport:{width:1024,height:768}});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto('http://127.0.0.1:'+server.address().port);await page.locator('.cores .core').first().waitFor();
  async function fits(){const overflow=await page.evaluate(()=>[...document.querySelectorAll('main,.panel,.item-card,footer,body')].filter(e=>e.scrollHeight>e.clientHeight+2||e.scrollWidth>e.clientWidth+2).map(e=>({tag:e.tagName,cls:e.className,h:e.clientHeight,sh:e.scrollHeight,w:e.clientWidth,sw:e.scrollWidth})));assert.deepEqual(overflow,[],'Screen content overflow: '+state.detail+' / '+state.focus)}
  await fits();assert.equal(await page.locator('.cores .core').count(),4);
  await page.locator('[data-section=cpu]').click();await page.locator('.focus-grid').waitFor();assert.equal(state.focus,'cpu');await fits();await page.keyboard.press('Escape');await page.locator('.detail-grid').waitFor();await page.locator('[data-section=gpu]').click();await page.locator('.focus-gpus').waitFor();assert.equal(state.focus,'gpu');await fits();await page.keyboard.press('Escape');await page.locator('.detail-grid').waitFor();
  await page.screenshot({path:path.join(root,'comic-detail-preview.png')});
  // All actual categories must fit for hosts with no GPU, two GPUs, and four GPUs.
  for(const count of [0,4]){state.hosts[0].metrics.gpus=Array.from({length:count},(_,i)=>({...primaryGpu,name:'GPU '+(i+1)}));await page.reload();await page.locator('.detail-grid').waitFor();await fits()}
  for(const section of ['cpu','gpu','memory','network','disks','temperatures','history']){state.focus=section;await page.reload();await page.locator('main').waitFor();await page.waitForFunction(()=>document.getElementById('main').innerHTML.length>0);await fits();if(section==='cpu')await page.screenshot({path:path.join(root,'comic-cpu-preview.png')})}
  state.focus=null;
  state.hosts[0].metrics.gpus=[{usage_percent:75,temperature_celsius:62,memory_used_mb:11348,memory_total_mb:16380,memory_percent:69.3}];state.detail=null;state.hosts=Array.from({length:3},(_,i)=>({...host,host:['pve','n100pve','DB795i'][i]}));state.selected='n100pve';await page.reload();await page.locator('article').first().waitFor();await fits();
  await page.screenshot({path:path.join(root,'comic-overview-preview.png')});
  if(actual){for(const item of actual.hosts){state.detail=item.host;state.hosts=[item];state.selected=item.host;await page.reload();await page.locator('.detail-grid').waitFor();await fits();for(const section of ['cpu','gpu','memory','network','disks','temperatures','history']){state.focus=section;await page.reload();await page.waitForFunction(()=>document.getElementById('main').innerHTML.length>0);await fits()}state.focus=null}}
  assert.deepEqual(errors,[]);console.log('PASS: 1024×768, no scrolling or clipping, top four cores, 0/2/4 GPUs, three-host overview');
 }finally{await browser.close();server.closeAllConnections();server.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
