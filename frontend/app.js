(() => {
  const ROWS = 19, COLS = 31, START = [9, 4], GOAL = [9, 26];
  const gridData = Array.from({ length: ROWS }, () => Array(COLS).fill(0));
  let start = [...START], goal = [...GOAL], algorithm = 'astar', tool = 'wall';
  let drawing = false, dragPoint = '', lastPainted = '', paintValue = 1, busy = false, paused = false, runToken = 0, timer;
  const grid = document.querySelector('#grid');
  const speed = [100, 65, 38, 18, 5];
  const key = ([r,c]) => `${r},${c}`;
  const fromKey = s => s.split(',').map(Number);
  const wait = ms => new Promise(resolve => { timer = setTimeout(resolve, ms); });
  function makeCells() {
    grid.innerHTML = '';
    for (let r=0;r<ROWS;r++) for(let c=0;c<COLS;c++) {
      const cell = document.createElement('div'); cell.className='cell'; cell.dataset.r=r; cell.dataset.c=c;
      cell.setAttribute('role','gridcell'); grid.append(cell);
    }
    draw();
  }
  function draw() {
    for(const cell of grid.children) {
      const r=+cell.dataset.r,c=+cell.dataset.c,k=`${r},${c}`;
      cell.className='cell'; cell.setAttribute('aria-label',`row ${r+1}, column ${c+1}`);
      if(gridData[r][c]===1) cell.classList.add('wall');
      if(gridData[r][c]>1) cell.classList.add('weight');
      if(k===key(start)) {cell.classList.add('start');cell.setAttribute('aria-label','Start');}
      if(k===key(goal)) {cell.classList.add('goal');cell.setAttribute('aria-label','Goal');}
    }
  }
  function resetVisuals() { document.querySelectorAll('.cell.visited,.cell.path').forEach(c=>c.classList.remove('visited','path')); }
  function cellAt(e) { return e.target.closest('.cell'); }
  function paint(cell) {
    if(!cell) return;
    const point=[+cell.dataset.r,+cell.dataset.c], k=key(point);
    if(dragPoint==='start'){if(k===key(goal))return;start=point;draw();return;}
    if(dragPoint==='goal'){if(k===key(start))return;goal=point;draw();return;}
    if(k===key(start)||k===key(goal)||k===lastPainted) return;
    lastPainted=k;
    if(tool==='wall')gridData[point[0]][point[1]]=paintValue;
    else if(tool==='weight')gridData[point[0]][point[1]]=paintValue===0?0:5;
    else gridData[point[0]][point[1]]=0;
    if(gridData[start[0]][start[1]]===1)gridData[start[0]][start[1]]=0;
    if(gridData[goal[0]][goal[1]]===1)gridData[goal[0]][goal[1]]=0;
    draw();
  }
  grid.addEventListener('pointerdown',e=>{const cell=cellAt(e);if(!cell||busy)return;e.preventDefault();drawing=true;lastPainted='';const p=[+cell.dataset.r,+cell.dataset.c];dragPoint=key(p)===key(start)?'start':key(p)===key(goal)?'goal':'';const current=gridData[p[0]][p[1]];paintValue=tool==='erase'?0:tool==='weight'?(current>1?0:5):(current===1?0:1);if(!dragPoint)paint(cell);grid.setPointerCapture(e.pointerId);});
  grid.addEventListener('pointermove',e=>{if(drawing)paint(cellAt(e));});
  grid.addEventListener('pointerup',()=>{drawing=false;dragPoint='';lastPainted='';});
  document.querySelectorAll('.algorithm').forEach(btn=>btn.onclick=()=>{if(busy)return;algorithm=btn.dataset.algorithm;document.querySelectorAll('.algorithm').forEach(x=>x.classList.toggle('selected',x===btn));});
  document.querySelectorAll('.tool').forEach(btn=>btn.onclick=()=>{tool=btn.dataset.tool;document.querySelectorAll('.tool').forEach(x=>x.classList.toggle('active',x===btn));});
  document.querySelector('#speed').oninput=e=>{document.querySelector('#speedLabel').textContent=['Slow','Steady','Balanced','Fast','Instant'][e.target.value-1];};
  async function search(algo) {
    const response=await fetch('/api/solve',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({maze:gridData,start,goal,algorithm:algo})});
    const data=await response.json();
    if(!response.ok)throw new Error(data.detail||'Search request failed');
    return {algo,visited:data.explored,path:data.path,cost:data.cost,ms:data.execution_time_ms,pathLength:data.path_length};
  }
  function clearStats(){['exploredMetric','lengthMetric','timeMetric','costMetric'].forEach(id=>document.getElementById(id).textContent='—');document.querySelector('#exploredSub').textContent='Waiting for run';}
  function showMetrics(result){document.querySelector('#exploredMetric').textContent=result.visited.length;document.querySelector('#exploredSub').textContent='nodes expanded';document.querySelector('#lengthMetric').textContent=result.pathLength??'No path';document.querySelector('#timeMetric').textContent=`${result.ms.toFixed(2)} ms`;document.querySelector('#costMetric').textContent=result.cost??'—';}
  async function animate(result,token){resetVisuals();const cells=new Map([...grid.children].map(c=>[`${c.dataset.r},${c.dataset.c}`,c]));for(const [i,p] of result.visited.entries()){if(token!==runToken)return;while(paused&&token===runToken)await wait(60);if(token!==runToken)return;if(key(p)!==key(start)&&key(p)!==key(goal))cells.get(key(p)).classList.add('visited');if(i%3===0)await wait(speed[+document.querySelector('#speed').value-1]);}
    for(const p of result.path){if(token!==runToken)return;while(paused&&token===runToken)await wait(60);if(token!==runToken)return;if(key(p)!==key(start)&&key(p)!==key(goal)){cells.get(key(p)).classList.remove('visited');cells.get(key(p)).classList.add('path');}await wait(Math.max(14,speed[+document.querySelector('#speed').value-1]));}
    document.querySelector('#status').textContent=result.path.length?'Path found':'No path available';}
  async function run(algo=algorithm){if(busy)return;busy=true;paused=false;const token=++runToken;document.querySelector('#runBtn').disabled=true;document.querySelector('#status').textContent='Searching…';try{const result=await search(algo);if(token!==runToken)return;showMetrics(result);document.querySelector('#status').textContent='Search complete · animating visualization…';await animate(result,token);}catch(error){if(token===runToken)document.querySelector('#status').textContent=`Search failed: ${error.message}`;}finally{if(token===runToken){busy=false;document.querySelector('#runBtn').disabled=false;}}}
  document.querySelector('#runBtn').onclick=()=>run();document.querySelector('#pauseBtn').onclick=()=>{if(busy){paused=!paused;document.querySelector('#pauseBtn').textContent=paused?'▶':'Ⅱ';document.querySelector('#status').textContent=paused?'Visualization paused':'Search complete · animating visualization…';}};
  document.querySelector('#resetBtn').onclick=()=>{runToken++;paused=false;clearTimeout(timer);busy=false;resetVisuals();clearStats();document.querySelector('#runBtn').disabled=false;document.querySelector('#status').textContent='Ready to explore';document.querySelector('#pauseBtn').textContent='Ⅱ';};
  document.querySelector('#clearBtn').onclick=()=>{if(busy)return;for(const row of gridData)row.fill(0);start=[...START];goal=[...GOAL];resetVisuals();clearStats();draw();document.querySelector('#status').textContent='Board cleared';};
  document.querySelector('#mazeBtn').onclick=async()=>{if(busy)return;try{const response=await fetch('/api/maze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({rows:ROWS,cols:COLS})});if(!response.ok)throw Error();const data=await response.json();data.maze.forEach((row,r)=>row.forEach((v,c)=>gridData[r][c]=v));gridData[start[0]][start[1]]=gridData[goal[0]][goal[1]]=0;resetVisuals();draw();document.querySelector('#status').textContent='New maze generated';}catch{document.querySelector('#status').textContent='Maze API unavailable';}};
  document.querySelector('#compareBtn').onclick=async()=>{if(busy)return;busy=true;document.querySelector('#status').textContent='Comparing strategies…';try{const results=await Promise.all(['astar','dijkstra','bfs'].map(search));const reachable=results.filter(r=>r.path.length);const best=reachable.length?Math.min(...reachable.map(r=>r.visited.length)):-1;document.querySelector('#comparison').innerHTML=`<table class="comparison-table"><thead><tr><th>ALGORITHM</th><th>NODES EXPLORED</th><th>PATH LENGTH</th><th>COST</th><th>TIME</th></tr></thead><tbody>${results.map(r=>`<tr class="${r.visited.length===best?'best':''}"><td class="table-alg">${{astar:'A* Search',dijkstra:'Dijkstra',bfs:'Breadth-first'}[r.algo]}${r.visited.length===best?' ✦':''}</td><td>${r.visited.length}</td><td>${r.pathLength??'No path'}</td><td>${r.cost??'—'}</td><td>${r.ms.toFixed(2)} ms</td></tr>`).join('')}</tbody></table>`;document.querySelector('#status').textContent='Comparison complete';showMetrics(results.find(r=>r.algo===algorithm));}catch(error){document.querySelector('#status').textContent=`Comparison failed: ${error.message}`;}finally{busy=false;}};
  document.addEventListener('keydown',e=>{if(e.target.matches('input,textarea'))return;if(e.code==='Space'){e.preventDefault();if(!busy)run();else paused=!paused;}if(e.key.toLowerCase()==='r')document.querySelector('#resetBtn').click();if(e.key.toLowerCase()==='g')document.querySelector('#mazeBtn').click();});
  makeCells();document.querySelector('#dimensions').textContent=`${COLS} × ${ROWS}`;
})();
