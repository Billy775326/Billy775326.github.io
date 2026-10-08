from pathlib import Path
from urllib.parse import urlsplit,parse_qs
from playwright.sync_api import sync_playwright
js=(Path(__file__).resolve().parents[1] / 'themes/butterfly/source/js/visit-counter.js').read_text(encoding='utf8')
with sync_playwright() as p:
 b=p.chromium.launch(headless=True)
 for case in ['success','502','malformed','timeout']:
  page=b.new_page();page.clock.install();requests=[];pending=[];errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  def route(r):
   requests.append(r.request.url);cb=parse_qs(urlsplit(r.request.url).query)['jsonpCallback'][0]
   if case=='success':r.fulfill(status=200,content_type='application/javascript',body=cb+'({"site_uv":0,"site_pv":123,"page_pv":7});')
   elif case=='502':r.fulfill(status=502,content_type='text/html',body='<h1>Bad Gateway</h1>')
   elif case=='malformed':r.fulfill(status=200,content_type='application/javascript',body=cb+'({"site_uv":"bad","site_pv":-1});')
   else:pending.append(r)
  page.route('https://busuanzi.ibruce.info/**',route)
  page.set_content('<span id="busuanzi_value_site_uv">loading</span><span id="busuanzi_value_site_pv">loading</span><span id="busuanzi_value_page_pv">loading</span>')
  page.add_script_tag(content=js)
  page.wait_for_function('!!document.querySelector("script[src*=jsonpCallback]") || !!document.querySelector("[data-counter-state]")')
  if case=='timeout':page.clock.fast_forward(8001)
  page.wait_for_function('document.querySelectorAll("[data-counter-state]").length===3')
  values=page.locator('[id^=busuanzi_value]').all_text_contents();assert values==(['0','123','7'] if case=='success' else ['暂不可用']*3),(case,values)
  page.add_script_tag(content=js);assert len(requests)==1
  if case=='timeout':
   cb=parse_qs(urlsplit(requests[0]).query)['jsonpCallback'][0];page.evaluate('(cb)=>window[cb]({site_uv:99,site_pv:99,page_pv:99})',cb);assert page.locator('[id^=busuanzi_value]').all_text_contents()==['暂不可用']*3
  for r in pending:r.abort()
  assert not errors,errors
  print('PASS',case,'single request, no perpetual spinner')
  page.close()
 b.close()
