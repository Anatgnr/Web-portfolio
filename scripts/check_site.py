"""Browser acceptance checks. Development-only requirement: pip install playwright.

Uses an installed Chrome and serves the packaged site under /Web-portfolio/.
Optional accessibility checks use .artifacts/axe.min.js when present.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.request import urlopen
import json
import os

from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS = ROOT / ".artifacts"
ARTIFACTS.mkdir(exist_ok=True)
PREFIX = "/Web-portfolio/"


class PagesHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if not self.path.startswith(PREFIX):
            self.send_error(404)
            return
        self.path = "/" + self.path[len(PREFIX):]
        super().do_GET()

    def log_message(self, *args):
        pass


server = ThreadingHTTPServer(("127.0.0.1", 0), partial(PagesHandler, directory=str(ROOT / "_site")))
Thread(target=server.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{server.server_port}{PREFIX}"
report = {"checks": [], "accessibility": [], "errors": [], "failed_requests": []}


def check(label, condition=True):
    assert condition, label
    report["checks"].append(label)


def jump(page, top):
    page.evaluate("top => window.scrollTo({top, behavior: 'instant'})", top)
    page.wait_for_timeout(120)


def accessibility(page, label):
    source = ARTIFACTS / "axe.min.js"
    if not source.exists():
        return
    page.add_script_tag(path=str(source))
    result = page.evaluate("""async () => {
      const result = await axe.run(document, {runOnly: {type:'tag', values:['wcag2a','wcag2aa','wcag21aa']}});
      return result.violations.map(v => ({id:v.id, impact:v.impact, nodes:v.nodes.map(n => ({target:n.target, summary:n.failureSummary}))}));
    }""")
    report["accessibility"].append({"viewport": label, "violations": result})


try:
    with sync_playwright() as p:
        chrome = os.environ.get("CHROME_PATH", "C:/Program Files/Google/Chrome/Application/chrome.exe")
        browser = p.chromium.launch(executable_path=chrome, headless=True)
        context = browser.new_context(viewport={"width":1440,"height":1000}, color_scheme="light", permissions=["clipboard-read","clipboard-write"])
        page = context.new_page()
        page.on("pageerror", lambda error: report["errors"].append(str(error)))
        page.on("response", lambda response: report["failed_requests"].append(response.url) if response.status >= 400 else None)
        page.add_init_script("""window.__metrics={cls:0,lcp:0};
          new PerformanceObserver(l=>l.getEntries().forEach(e=>{if(!e.hadRecentInput)window.__metrics.cls+=e.value})).observe({type:'layout-shift',buffered:true});
          new PerformanceObserver(l=>l.getEntries().forEach(e=>window.__metrics.lcp=e.startTime)).observe({type:'largest-contentful-paint',buffered:true});""")
        page.goto(BASE, wait_until="networkidle")
        check("One primary heading and main landmark", page.locator('h1').count() == 1 and page.locator('main').count() == 1)
        check("Light system preference applied", page.locator('html').get_attribute('data-theme') == 'light')
        data = json.loads(page.locator('script[type="application/ld+json"]').text_content())
        check("Structured profile data valid", data['@type'] == 'ProfilePage' and data['mainEntity']['name'] == 'Anatole Garnier')
        check("Canonical URL matches GitHub Pages", page.locator('link[rel="canonical"]').get_attribute('href') == 'https://anatgnr.github.io/Web-portfolio/')
        report['local_metrics'] = page.evaluate('({...window.__metrics, resource_bytes:performance.getEntriesByType("resource").reduce((n,r)=>n+r.transferSize,0), requests:performance.getEntriesByType("resource").length})')
        page.screenshot(path=str(ARTIFACTS/'desktop-top.png'))

        # Check every same-site href and image, including the GitHub project prefix.
        resources = page.evaluate("""() => [...new Set([...document.querySelectorAll('a[href],link[href],script[src],img[src]')].map(e=>e.href||e.src).filter(s=>s.startsWith(location.origin)&&!s.includes('#')))]""")
        for url in resources:
            with urlopen(url) as response:
                check(f"Public resource responds: {url.split(PREFIX)[-1]}", response.status == 200)
        missing = page.evaluate("""() => [...document.querySelectorAll('a[href^="#"]')].filter(a=>!document.getElementById(a.getAttribute('href').slice(1))).map(a=>a.getAttribute('href'))""")
        check("All navigation fragments resolve", not missing)
        with urlopen(BASE+'assets/Anatole-Garnier-CV.pdf') as response:
            check("Download is a valid PDF", response.read(5) == b'%PDF-')

        # The image zoom must advance and return to exactly its initial state.
        geometry = page.locator('.workspace').evaluate("e=>({top:e.offsetTop, distance:e.offsetHeight-e.firstElementChild.offsetHeight, sticky:parseFloat(getComputedStyle(e.firstElementChild).top)})")
        start = geometry['top'] - geometry['sticky']
        samples = []
        for fraction in [0, .45, 1, .45, 0]:
            jump(page, start + geometry['distance'] * fraction)
            samples.append(page.locator('.workspace').evaluate("e=>({zoom:parseFloat(getComputedStyle(e).getPropertyValue('--zoom')),message:parseFloat(getComputedStyle(e).getPropertyValue('--message-opacity'))})"))
        check("Scroll zoom advances and reverses", samples[1]['zoom'] > samples[0]['zoom'] and abs(samples[4]['zoom']-samples[0]['zoom']) < .01 and abs(samples[3]['zoom']-samples[1]['zoom']) < .02)
        check("Screen-entry message appears at full zoom", samples[2]['message'] > .99)
        jump(page, start + geometry['distance'] * .45)
        page.screenshot(path=str(ARTIFACTS/'desktop-immersion.png'))

        page.locator('[data-filter="vision"]').click()
        check("Vision filter shows two projects", page.locator('.project-card:visible').count() == 2)
        page.locator('[data-filter="generative"]').click()
        check("Generative filter shows one project", page.locator('.project-card:visible').count() == 1)
        expect(page.locator('.project-count')).to_have_text('01 projet')
        page.locator('[data-filter="all"]').click()
        check("All projects restored", page.locator('.project-card:visible').count() == 3)
        for key in ['robotics','rag','archeology']:
            trigger = page.locator(f'[data-project="{key}"]')
            trigger.click()
            expect(page.locator('dialog')).to_be_visible()
            check(f"Project {key} has detailed content", page.locator('#dialog-sections section').count() == 3)
            for _ in range(5):
                page.keyboard.press('Tab')
                check(f"Project {key} blocks background keyboard focus", page.evaluate('document.activeElement === document.body || document.querySelector("dialog").contains(document.activeElement)'))
            page.keyboard.press('Escape')
            expect(page.locator('dialog')).not_to_be_visible()
            expect(trigger).to_be_focused()
        check("Dialog closes with Escape and restores focus")
        page.locator('[data-project="robotics"]').click()
        accessibility(page,'desktop light dialog')
        page.locator('.dialog-close').click()

        second = page.locator('.timeline-item').nth(1)
        second.locator('summary').click()
        check("Experience expands natively", second.get_attribute('open') is not None)
        second.locator('summary').click()
        check("Experience collapses natively", second.get_attribute('open') is None)
        page.locator('.copy-email').click()
        expect(page.locator('.copy-feedback')).to_have_text('Adresse e-mail copiée.')
        check("Email copied to clipboard", page.evaluate('navigator.clipboard.readText()') == 'garnieranatole@gmail.com')
        with page.expect_download() as download_info:
            page.locator('.hero-actions a[download]').click()
        check("CV download works", download_info.value.suggested_filename == 'Anatole-Garnier-CV.pdf')

        # Explicit theme overrides persist, while a fresh context follows the OS.
        page.locator('.theme-toggle').click()
        page.reload(wait_until='networkidle')
        check("Chosen dark theme survives reload", page.locator('html').get_attribute('data-theme') == 'dark')
        page.emulate_media(color_scheme='light')
        check("Explicit theme overrides system preference", page.locator('html').get_attribute('data-theme') == 'dark')
        for theme in ['light','dark']:
            page.evaluate("theme=>{document.documentElement.dataset.theme=theme;localStorage.setItem('portfolio-theme',theme)}",theme)
            for width in [320,375,390,600,768,1024,1440,1920]:
                page.set_viewport_size({'width':width,'height':900})
                jump(page,0)
                overflow = page.evaluate('document.documentElement.scrollWidth > innerWidth')
                check(f"No horizontal overflow at {width}px, {theme}", not overflow)
            page.set_viewport_size({'width':1440,'height':1000})
            jump(page, page.locator('#projets').evaluate('e=>e.offsetTop-100'))
            page.wait_for_timeout(750)
            page.screenshot(path=str(ARTIFACTS/f'desktop-projects-{theme}.png'))
            accessibility(page,f'desktop {theme}')

        page.set_viewport_size({'width':390,'height':844})
        page.evaluate("document.documentElement.dataset.theme='light';localStorage.setItem('portfolio-theme','light')")
        jump(page,0)
        page.wait_for_timeout(300)
        page.screenshot(path=str(ARTIFACTS/'mobile-top.png'))
        page.locator('.menu-toggle').click()
        expect(page.locator('.nav-links')).to_be_visible()
        page.locator('.nav-links a[href="#projets"]').click()
        expect(page.locator('.nav-links')).not_to_be_visible()
        check("Mobile menu navigates and closes")
        page.locator('.menu-toggle').click()
        page.keyboard.press('Escape')
        expect(page.locator('.menu-toggle')).to_be_focused()
        expect(page.locator('.nav-links')).not_to_be_visible()
        check("Mobile menu supports Escape")
        jump(page,page.locator('#projets').evaluate('e=>e.offsetTop-85'))
        page.wait_for_timeout(750)
        page.screenshot(path=str(ARTIFACTS/'mobile-projects.png'))
        accessibility(page,'mobile light')
        page.locator('[data-project="rag"]').click()
        page.screenshot(path=str(ARTIFACTS/'mobile-dialog.png'))
        accessibility(page,'mobile light dialog')
        page.locator('.dialog-close').click()

        for old,target in [('main.html','parcours'),('A-propos.html','apropos'),('contact.html','contact')]:
            page.goto(BASE+'html/'+old,wait_until='networkidle')
            page.wait_for_url('**/index.html#'+target)
            check(f"Legacy URL {old} redirects to correct section")

        system_context = browser.new_context(color_scheme='dark')
        system_page = system_context.new_page()
        system_page.goto(BASE,wait_until='networkidle')
        check("Fresh visitor follows dark OS preference", system_page.locator('html').get_attribute('data-theme') == 'dark')
        system_page.emulate_media(color_scheme='light')
        expect(system_page.locator('html')).to_have_attribute('data-theme','light')
        check("Theme tracks OS changes before an explicit choice")
        reduced = browser.new_context(reduced_motion='reduce',viewport={'width':390,'height':844})
        reduced_page = reduced.new_page()
        reduced_page.goto(BASE,wait_until='networkidle')
        check("Reduced motion removes sticky scene", reduced_page.locator('.workspace-stage').evaluate('e=>getComputedStyle(e).position') == 'relative')
        check("Reduced motion disables smooth scrolling", reduced_page.locator('html').evaluate('e=>getComputedStyle(e).scrollBehavior') == 'auto')
        static = browser.new_context(java_script_enabled=False,viewport={'width':390,'height':844})
        static_page = static.new_page()
        static_page.goto(BASE,wait_until='networkidle')
        check("Content and mobile navigation work without JavaScript", static_page.locator('h1').is_visible() and static_page.locator('.nav-links a').first.is_visible() and static_page.locator('.project-card').count() == 3)
        check("No browser JavaScript errors", not report['errors'])
        check("No missing browser resources", not report['failed_requests'])
        browser.close()
finally:
    server.shutdown()
    (ARTIFACTS/'qa-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({"passed_checks":len(report['checks']),"errors":report['errors'],"failed_requests":report['failed_requests'],"local_metrics":report.get('local_metrics'),"accessibility":[{"viewport":a['viewport'],"violations":len(a['violations'])} for a in report['accessibility']]},ensure_ascii=True,indent=2))

assert not any(a['violations'] for a in report['accessibility']), 'Accessibility issues: inspect .artifacts/qa-report.json'
