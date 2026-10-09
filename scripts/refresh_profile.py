"""Generate profile SVGs from public GitHub data; standard library only."""
from pathlib import Path
from html.parser import HTMLParser
from html import escape
from datetime import date,datetime,timezone
from collections import Counter
import json,os,re,urllib.request
ROOT=Path(__file__).resolve().parents[1]
USER=os.environ.get('PROFILE_USER','Rocdna')
TOKEN=os.environ.get('GITHUB_TOKEN','')
HEADERS={'User-Agent':'Rocdna-profile','Accept':'application/vnd.github+json'}

def request(url,payload=None,auth=True):
    headers=HEADERS.copy()
    if auth and TOKEN:headers['Authorization']='Bearer '+TOKEN
    data=json.dumps(payload).encode() if payload is not None else None
    req=urllib.request.Request(url,data=data,headers=headers)
    with urllib.request.urlopen(req,timeout=30) as r:return r.read().decode()

def calendar():
    if TOKEN:
        q='query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{date contributionCount contributionLevel}}}}}}'
        d=json.loads(request('https://api.github.com/graphql',{'query':q,'variables':{'login':USER}}))
        if d.get('errors'):raise RuntimeError('GitHub contribution query failed')
        c=d['data']['user']['contributionsCollection']['contributionCalendar']
        levels={'NONE':0,'FIRST_QUARTILE':1,'SECOND_QUARTILE':2,'THIRD_QUARTILE':3,'FOURTH_QUARTILE':4}
        days=[{'date':p['date'],'level':levels[p['contributionLevel']],'count':p['contributionCount']} for w in c['weeks'] for p in w['contributionDays']]
        return days,c['totalContributions']
    class Parser(HTMLParser):
        def __init__(self):super().__init__();self.cells={};self.tips={};self.tip=None;self.buf=[]
        def handle_starttag(self,t,attrs):
            a=dict(attrs)
            if t=='td' and a.get('data-date'):
                self.cells[a['id']]={'date':a['data-date'],'level':int(a['data-level'])}
            if t=='tool-tip':self.tip=a.get('for');self.buf=[]
        def handle_data(self,d):
            if self.tip:self.buf.append(d)
        def handle_endtag(self,t):
            if t=='tool-tip' and self.tip:self.tips[self.tip]=''.join(self.buf);self.tip=None
    p=Parser();p.feed(request('https://github.com/users/'+USER+'/contributions',auth=False))
    days=[]
    for k,v in p.cells.items():
        text=p.tips.get(k,'');m=re.match(r'([\d,]+) contributions?\b',text)
        if not m and not text.startswith('No contributions'):raise RuntimeError('Contribution count could not be parsed')
        v['count']=int(m.group(1).replace(',','')) if m else 0;days.append(v)
    if len(days)<350:raise RuntimeError('Contribution calendar was incomplete')
    days.sort(key=lambda d:d['date'])
    return days,sum(d['count'] for d in days)

def svg(w,h,title,body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img"><title>{escape(title)}</title><defs><linearGradient id="bg" x2="1" y2="1"><stop stop-color="#141727"/><stop offset="1" stop-color="#211b35"/></linearGradient></defs><rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="16" fill="url(#bg)" stroke="#3c3452"/>{body}</svg>'

def text(x,y,s,size=16,color='#e4def7',weight=400):
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{color}" font-family="Segoe UI,Microsoft YaHei,Noto Sans CJK SC,sans-serif">{escape(str(s))}</text>'

def write(name,s):
    p=ROOT/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8')

def city(days,total):
    colors=['#272a40','#64519a','#8e68bd','#bd80cc','#eda2cd']
    start=date.fromisoformat(days[0]['date']);body=text(28,38,'CONTRIBUTION CITY',20,weight=600)+text(28,62,'真实贡献记录 / 过去一年',13,'#aaa3c3')+text(630,39,f'{total} CONTRIBUTIONS',15,'#eda2cd')
    def proj(w,r,z=0):return 61+w*13.5+r*8.4,173+w*2.35-r*6-z
    def pts(v):return ' '.join(f'{x:.2f},{y:.2f}' for x,y in v)
    for d in days:
        dt=date.fromisoformat(d['date']);delta=(dt-start).days;w=delta//7;r=delta%7;x,y=proj(w,r);level=d['level'];h=2+level*8
        top=[proj(w,r,h),proj(w+.8,r,h),proj(w+.8,r+.8,h),proj(w,r+.8,h)]
        left=[proj(w,r,h),proj(w+.8,r,h),proj(w+.8,r),proj(w,r)]
        right=[proj(w+.8,r,h),proj(w+.8,r+.8,h),proj(w+.8,r+.8),proj(w+.8,r)]
        title=f"{d['date']}: {d['count']} contributions"
        body+=f'<g><title>{escape(title)}</title><polygon points="{pts(left)}" fill="{colors[level]}" opacity=".55"/><polygon points="{pts(right)}" fill="{colors[level]}" opacity=".75"/><polygon points="{pts(top)}" fill="{colors[level]}" stroke="#171727" stroke-width=".5"/></g>'
    body+=text(28,335,days[0]['date']+' — '+days[-1]['date'],12,'#aaa3c3')+text(648,335,'LESS',11,'#aaa3c3')
    for i,c in enumerate(colors):body+=f'<rect x="{686+i*17}" y="323" width="12" height="12" rx="2" fill="{c}"/>'
    body+=text(780,335,'MORE',11,'#aaa3c3')
    write('profile-3d-contrib/profile-customize.svg',svg(900,360,'Rocdna 3D GitHub contribution calendar',body))

def stats(repos,days,total):
    values=[('公开仓库',len(repos)),('仓库 Stars',sum(r['stargazers_count'] for r in repos)),('年度贡献',total),('活跃天数',sum(d['count']>0 for d in days))]
    b=text(28,37,'GITHUB / PUBLIC SNAPSHOT',17,weight=600)
    for i,(label,n) in enumerate(values):
        x=28+i*216;b+=text(x,87,n,32,'#eda2cd',600)+text(x,117,label,14,'#aaa3c3')
    b+=text(28,153,'UPDATED '+datetime.now(timezone.utc).strftime('%Y-%m-%d')+' UTC · 仓库数和 Stars 为当前值，贡献与活跃天数为过去一年',12,'#aaa3c3')
    write('assets/stats.svg',svg(900,175,'GitHub public statistics',b))
    counts=Counter(r['language'] for r in repos if r['language'] and not r['fork'])
    b=text(28,36,'PUBLIC REPOS / PRIMARY LANGUAGES',17,weight=600)+text(28,59,'按非 Fork 公开仓库的主语言计数，不代表代码行数或熟练度',12,'#aaa3c3')
    palette=['#a78bfa','#eda2cd','#67d5db','#e2bd76','#99bf99'];x=28
    count=sum(counts.values())
    for i,(lang,n) in enumerate(counts.most_common()):
        width=844*n/count;b+=f'<rect x="{x}" y="77" width="{width}" height="12" fill="{palette[i%len(palette)]}"/>';x+=width
        b+=text(28+i*170,118,f'{lang} · {n}',14,palette[i%len(palette)])
    write('assets/languages.svg',svg(900,145,'Repository primary language distribution',b))

def project_cards():
    entries=[('agent','01 / AGENT SYSTEM','Mini-Agent','工具调用 · RAG · 长期记忆','ReAct 循环与上下文管理','Python / ReAct / Memory'),('rag','02 / KNOWLEDGE ENGINE','RAG Assistant','混合检索 · HyDE · 文档引用','让回答有据可循','Next.js / RRF / Pinecone'),('transformer','03 / MODEL FROM SCRATCH','Transformer Learn','手写注意力 · 训练 · 增量推理','把原理变成能够运行的模型','PyTorch / Attention / KV Cache')]
    for key,label,title,a,b,tags in entries:
        body=text(22,30,label,12,'#a78bfa',600)+text(22,73,title,25,weight=600)+text(22,110,a,14,'#cbc1dc')+text(22,134,b,14,'#cbc1dc')+text(22,181,tags,12,'#eda2cd')
        write(f'assets/project-{key}.svg',svg(410,207,title,body))

if __name__=='__main__':
    days,total=calendar();repos=[]
    for page in range(1,11):
        batch=json.loads(request(f'https://api.github.com/users/{USER}/repos?per_page=100&page={page}'))
        repos+=batch
        if len(batch)<100:break
    city(days,total);stats(repos,days,total);project_cards()
    readme=ROOT/'README.md'
    if readme.exists() and (ROOT/'assets/github-snake.svg').exists():
        s=readme.read_text();s=s.replace('<!-- SNAKE:START -->'+s.split('<!-- SNAKE:START -->')[1].split('<!-- SNAKE:END -->')[0]+'<!-- SNAKE:END -->','<!-- SNAKE:START -->\n<p align="center"><img src="./assets/github-snake.svg" width="900" alt="贪吃蛇贡献动画" /></p>\n<!-- SNAKE:END -->');readme.write_text(s)
    print(f'Generated {len(days)} contribution days; {total} contributions; {len(repos)} public repositories.')
