/* Busuanzi JSONP adapter: preserve the original provider and referrer semantics.
 * Failed requests are not retried automatically: retries can count a visit twice.
 */
(() => {
  'use strict'
  const initialize = () => {
    const fields = ['site_uv', 'site_pv', 'page_pv']
    const nodes = fields.map(key => [key, document.getElementById(`busuanzi_value_${key}`)])
      .filter(([, node]) => node)
    if (!nodes.length || window.__billyVisitCounterRequested) return
    window.__billyVisitCounterRequested = true

    const callback = `BusuanziCallback_${Date.now()}_${Math.floor(Math.random() * 1000000)}`
    const script = document.createElement('script')
    let settled = false
    let timer
    const finish = data => {
      if (settled) return
      settled = true
      clearTimeout(timer)
      for (const [key, node] of nodes) {
        const value = data && data[key]
        const valid = typeof value === 'number' && Number.isSafeInteger(value) && value >= 0
        node.textContent = valid ? String(value) : '暂不可用'
        node.dataset.counterState = valid ? 'ready' : 'unavailable'
        node.title = valid ? '不蒜子实时统计' : '统计服务暂时不可用，不代表访问量为零；下次打开页面时重新获取。'
        node.setAttribute('aria-busy', 'false')
      }
      // A response already in flight may still execute after timeout.
      window[callback] = () => {}
      script.remove()
    }
    for (const [, node] of nodes) {
      node.setAttribute('aria-live', 'polite')
      node.setAttribute('aria-busy', 'true')
    }
    window[callback] = data => finish(data)
    script.async = true
    script.referrerPolicy = 'no-referrer-when-downgrade'
    script.src = `https://busuanzi.ibruce.info/busuanzi?jsonpCallback=${callback}`
    script.onerror = () => finish(null)
    script.onload = () => { if (!settled) finish(null) }
    timer = setTimeout(() => finish(null), 8000)
    document.head.appendChild(script)
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize, { once: true })
  } else {
    initialize()
  }
})()
