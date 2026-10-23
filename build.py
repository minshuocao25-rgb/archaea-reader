from pathlib import Path
r=Path(__file__).parent
base=(r/'base.html').read_text(encoding='utf8')
css=(r/'style.css').read_text(encoding='utf8')
js=(r/'app.js').read_text(encoding='utf8')
data=(r/'data'/'archive.json').read_text(encoding='utf8')
lexicon=(r/'data'/'lexicon.json').read_text(encoding='utf8')
html=(base
      .replace('/*CSS_INJECT*/',css)
      .replace('/*LEXICON_INJECT*/','window.ARCHAEA_LEXICON='+lexicon+';')
      .replace('/*DATA_INJECT*/','window.ARCHAEA_DATA='+data+';')
      .replace('/*JS_INJECT*/',js))
(r/'index.html').write_text(html,encoding='utf8')
print('Built:',r/'index.html')
