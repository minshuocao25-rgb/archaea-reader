"""将每日自动任务导出的 JSON 写入静态站点归档（不覆盖既有期次）。

用法：python import_issues.py /path/to/adna-bioarch-YYYY-MM-DD.json [...]
会更新 data/archive.json，再运行 build.py 重新构建 index.html。
这是手动/CI 入口，不负责 ChatGPT 任务或自动抓取 DOI。
"""
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).parent
archive_path=ROOT/'data'/'archive.json'

def first(p,*keys):
    for k in keys:
        v=p.get(k)
        if v not in ('',None): return v
    return ''

def as_text(x):
    if isinstance(x,list): return '、'.join(str(v) for v in x)
    if isinstance(x,dict):return '；'.join(f'{a}: {b}' for a,b in x.items())
    return str(x or '')

def normalize(d):
    issue_id=d.get('issue_id') or 'adna-bioarch-'+d.get('date','undated')
    papers=[]
    for j,p in enumerate(d['papers']):
        doi=str(p.get('doi','')).lower().replace('https://doi.org/','').strip()
        g=lambda *keys:as_text(first(p,*keys))
        rawcat=first(p,'categories','category','topic','focus')
        papers.append({'id':doi or f'{issue_id}-{j}','doi':doi,'title':g('title'),
          'authors':p.get('authors',[]),'journal':g('journal','venue'),
          'date':g('first_published','publication_date'),'kind':g('publication_type','type'),
          'priority':g('priority','learning_priority') or 'A','url':g('publisher_url','url') or ('https://doi.org/'+doi),
          'reading_status':g('reading_status'),'topic':rawcat if isinstance(rawcat,list) else [rawcat] if rawcat else [],
          'question':g('research_question','question'),'materials':g('materials'),
          'design':g('study_design','design_methods','design'),'methods':g('methods'),
          'results':g('key_findings','findings','results'),'innovation':g('methodological_innovation','innovation'),
          'limitations':g('limitations'),'future':g('future_value','future'),
          'learning':g('learning','learning_priority'),'verification':g('verification','metadata_verified_via'),
          'notice':'来自每日导入的档案；请核对出版社原始书目与 DOI，未自动复核。',
          'source_issue':issue_id})
    return {'issue_id':issue_id,'date':d.get('date',''), 'issue_number':d.get('issue_number'),
            'papers':papers,'origin':'cli_import'}

def fingerprint(x):
    return hashlib.sha256(json.dumps(x.get('papers',[]),ensure_ascii=False,sort_keys=True).encode()).hexdigest()

def main():
    if len(sys.argv)<2:sys.exit(__doc__)
    data=json.loads(archive_path.read_text(encoding='utf8'))
    existing=data['issues']
    for name in sys.argv[1:]:
        raw=json.loads(Path(name).read_text(encoding='utf8'))
        if 'papers' not in raw:print('Skip: missing papers',name);continue
        new=normalize(raw);origin=new['issue_id']
        same=[x for x in existing if x['issue_id']==origin or x.get('version_of')==origin]
        if any(fingerprint(x)==fingerprint(new) for x in same):print('Unchanged',origin);continue
        if same:
            version=len(same)+1;new['issue_id']=f'{origin}-v{version}';new['version_of']=origin;new['version']=version
        existing.append(new);print('Added',new['issue_id'],'papers',len(new['papers']))
    archive_path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    import subprocess
    subprocess.run([sys.executable,str(ROOT/'build.py')],check=True)
if __name__=='__main__':main()
