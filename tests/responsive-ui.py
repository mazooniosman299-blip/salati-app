"""Evaluate real stylesheet selector specificity against the app DOM; no browser/fidelity claim."""
from pathlib import Path
import re,sys,unittest
import tinycss2,cssselect2
from lxml import html
ROOT=Path(__file__).resolve().parents[1]
class Cascade:
 def __init__(self,width,dark=False,native=False):
  self.root=html.fromstring((ROOT/'dist/index.html').read_text());body=self.root.find('body');body.set('class',('dark ' if dark else '')+('native-android' if native else ''))
  self.wrapper=cssselect2.ElementWrapper.from_html_root(self.root);self.elements=list(self.wrapper.iter_subtree());self.by_element={e.etree_element:e for e in self.elements};self.matcher=cssselect2.Matcher();self.order=0
  def add(rules):
   for r in rules:
    if r.type=='at-rule' and r.lower_at_keyword=='media':
     q=tinycss2.serialize(r.prelude)
     low=re.findall(r'min-width:\s*([\d.]+)px',q);high=re.findall(r'max-width:\s*([\d.]+)px',q)
     if any(width<float(x) for x in low) or any(width>float(x) for x in high) or 'prefers-reduced-motion' in q:continue
     add(tinycss2.parse_rule_list(r.content,skip_whitespace=True,skip_comments=True))
    elif r.type=='qualified-rule':
     self.order+=1
     declarations=[(d.lower_name,tinycss2.serialize(d.value).strip(),d.important) for d in tinycss2.parse_declaration_list(r.content,skip_whitespace=True,skip_comments=True) if d.type=='declaration']
     try:
      for selector in cssselect2.compile_selector_list(tinycss2.serialize(r.prelude)):self.matcher.add_selector(selector,(self.order,declarations))
     except cssselect2.SelectorError:pass
  for link in self.root.xpath('//link[@rel="stylesheet"]'):
   path=ROOT/'dist'/link.get('href').lstrip('/')
   add(tinycss2.parse_stylesheet(path.read_text(),skip_whitespace=True,skip_comments=True))
  self.cache={}
 def element(self,xpath):return self.by_element[self.root.xpath(xpath)[0]]
 def style(self,e):
  if e in self.cache:return self.cache[e]
  parent=self.style(e.parent) if e.parent else {};out={k:v for k,v in parent.items() if k.startswith('--') or k in ['color','font-size','font-family','font-weight','direction','line-height']};winners={}
  for specificity,_,pseudo,(order,declarations) in self.matcher.match(e):
   if pseudo:continue
   for name,value,important in declarations:
    rank=(important,specificity,order)
    if name not in winners or rank>=winners[name][0]:winners[name]=(rank,value)
  out.update({k:v[1] for k,v in winners.items()})
  for k,v in list(out.items()):
   if not k.startswith('--'):
    for _ in range(5):v=re.sub(r'var\((--[\w-]+)\)',lambda m:out.get(m[1],m[0]),v)
    out[k]=parent.get(k,'') if v=='inherit' else v
  self.cache[e]=out;return out
 def pixels(self,e,name):
  value=self.style(e).get(name,'')
  if value.endswith('px'):return float(value[:-2])
  if value.endswith('em'):
   font=self.style(e).get('font-size','16px');return float(value[:-2])*float(font[:-2])
  return value
class Responsive(unittest.TestCase):
 def test_phone_light_dark(self):
  for width in [320,390,600,760]:
   for dark in [False,True]:
    with self.subTest(width=width,dark=dark):
     c=Cascade(width,dark);label=c.element('//div[@class="hero-timer"]/small');self.assertEqual(c.style(label)['color'],'#ffffff' if dark else '#000000')
     for e in [c.element('//div[@class="location-identity"]'),c.element('//div[@class="location-date"]')]:self.assertNotIn('180px',c.style(e).get('flex',''))
     icons=[c.by_element[e] for e in c.root.xpath('//nav/button/*[self::svg or self::img]')];self.assertEqual(len(icons),6);self.assertTrue(all(c.pixels(e,'width')==24 and c.pixels(e,'height')==24 for e in icons),[(c.pixels(e,'width'),c.pixels(e,'height')) for e in icons])
     photo=c.element('//div[@class="hero-picture"]/img');self.assertEqual(c.style(photo)['height'],'auto');self.assertEqual(c.style(photo)['position'],'static');self.assertEqual(c.style(photo)['object-fit'],'contain')
 def test_updated_controls_and_colors(self):
  for width in [320,390,820,1440]:
   for dark in [False,True]:
    c=Cascade(width,dark)
    self.assertEqual(c.style(c.element('//*[@id="countdown"]'))['color'],'#fff' if dark else '#000')
    locate=c.element('//*[@id="locate"]');self.assertEqual(c.style(locate)['background'],'#fff');self.assertEqual(c.style(locate)['color'],'#000')
    for id in ['adhkarCategoryPickerOpen','adhkarSearch']:
     if id=='adhkarCategoryPickerOpen':
      # Generated trigger is created by JS; inspect its equivalent selector in live component checks.
      continue
     self.assertEqual(c.pixels(c.element('//*[@id="'+id+'"]'),'height'),48)
  import xml.etree.ElementTree as ET
  sprite=ET.parse(ROOT/'dist/icons/navigation.svg').getroot();ids={e.get('id') for e in sprite if e.tag.endswith('symbol')}
  self.assertEqual(ids,{'times','mushaf','qibla','dhikr','tasbih','settings'})
  c=Cascade(390);self.assertEqual({node.get('href').split('#')[1] for node in c.root.xpath('//nav/button/*[name()="svg"]/*[name()="use"]')},ids)
 def test_compact_phone_navigation(self):
  for width in [320,390,600,760]:
   for dark in [False,True]:
    with self.subTest(width=width,dark=dark):
     c=Cascade(width,dark);nav=c.element('//nav');style=c.style(nav)
     self.assertEqual(style.get('grid-template-rows'),'56px','Navigation must not use a stretchable auto row')
     self.assertEqual(style.get('min-height'),'0','Reset desktop inherited minimum')
     self.assertEqual(style.get('align-self'),'auto','Fixed nav must not stretch in its header grid')
     self.assertEqual(style.get('height'),'calc(65px + env(safe-area-inset-bottom,0px))')
     for node in c.root.xpath('//nav/button'):
      button=c.by_element[node];self.assertEqual(c.pixels(button,'height'),56);self.assertEqual(c.style(button).get('min-height'),'0')
     c=Cascade(width,dark,native=True);nav=c.element('//nav')
     self.assertEqual(c.style(nav).get('height'),'calc(65px + 0px)','Native root already applies system inset')
 def test_capped_cards_are_centered(self):
  for width in [390,820,1440]:
   for dark in [False,True]:
    c=Cascade(width,dark)
    for xpath in ['//*[@id="tasbih"]/div','//*[@id="qibla"]/div','//*[@id="dhikr"]/div']:
     self.assertEqual(c.style(c.element(xpath)).get('margin-inline'),'auto',xpath)
 def test_audio_switch_geometry(self):
  for width in [320,390,820,1440]:
   for dark in [False,True]:
    for direction in ['rtl','ltr']:
     for checked in [False,True]:
      with self.subTest(width=width,dark=dark,direction=direction,checked=checked):
       c=Cascade(width,dark);c.root.set('dir',direction)
       for id in ['audioEnable','duaToggle','silentAdhanToggle']:
        e=c.element('//*[@id="'+id+'"]');e.etree_element.set('aria-checked',str(checked).lower())
        if id=='audioEnable':e.etree_element.set('class','audio-toggle'+(' is-on' if checked else ''))
       c.cache={}
       for id in ['audioEnable','duaToggle','silentAdhanToggle']:
        e=c.element('//*[@id="'+id+'"]');thumb=c.by_element[e.etree_element[0]];height=max(c.pixels(e,'height'),float(c.style(e).get('min-height','0').replace('px','')))
        self.assertEqual(height,38,id);self.assertEqual(c.pixels(e,'width'),66,id);self.assertEqual(c.pixels(thumb,'top')+c.pixels(thumb,'height')/2,height/2,id)
        left=c.pixels(thumb,'left');transform=c.style(thumb).get('transform','none')
        if transform!='none':left+=float(re.search(r'translateX\((-?[\d.]+)px\)',transform)[1])
        self.assertIn(left,[4,32]);self.assertLessEqual(left+c.pixels(thumb,'width'),66)
       for action in c.root.xpath('//*[@id="previewAdhan" or @id="previewDua" or @id="audioStop"]'):
        self.assertEqual(c.pixels(c.by_element[action],'min-height'),44,'Ordinary action targets stay at least 44px')
 def test_desktop_header_flow(self):
  for width in [820,1024,1440]:
   c=Cascade(width);nav=c.element('//nav');self.assertEqual(nav.etree_element.getparent().tag,'header');self.assertNotIn('-',c.style(nav).get('margin-top','0'));self.assertEqual(c.style(nav).get('position','static'),'static')
 def test_copy_and_counter_order(self):
  c=Cascade(390);timer=c.element('//div[@class="hero-timer"]').etree_element;self.assertEqual(timer[0].tag,'small');self.assertEqual(timer[1].get('id'),'countdown');self.assertNotIn('صلاتي كما تحب',(ROOT/'dist/index.html').read_text())
if __name__=='__main__':unittest.main()
