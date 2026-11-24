#!/usr/bin/env python3
"""Export a post's reveal.js presentation (layouts/_default/single.reveal.html) to PDF.

reveal.js's own print-pdf mode only captures the title slide, because this
layout builds the slides with JavaScript after the page loads. Instead, each
slide is screenshotted with headless Chromium, and clickable link areas are
added on top of the images:

- web and mailto links open the live site's address, not the local server's;
- links to anchors on other slides (footnotes and their back-references)
  jump to the page that holds the anchor.

The deck is built from a small Hugo site kept in this repository
(presentation/site): the post's markdown, the reveal layout and the images
it uses. Refresh that copy from the full blog whenever the deck changes:

    python scripts/reveal_to_pdf.py --update-from PATH/TO/BLOG -o presentation/slides.pdf

and to rebuild the PDF from the copy already in the repository:

    python scripts/reveal_to_pdf.py -o presentation/slides.pdf

Needs Hugo, Pillow and Chromium or Chrome. The browser is looked up on PATH,
then among Flatpak apps; set CHROME to override, e.g. CHROME="chromium".
"""
import argparse, base64, html, io, json, os, re, shlex, shutil, socket
import subprocess, sys, tempfile, time, tomllib, urllib.error, urllib.parse, urllib.request
from pathlib import Path

from PIL import Image

BROWSERS = ('chromium', 'chromium-browser', 'google-chrome', 'google-chrome-stable')
FLATPAK_BROWSERS = ('org.chromium.Chromium', 'io.github.ungoogled_software.ungoogled_chromium',
                    'com.google.Chrome')
REPO = Path(__file__).resolve().parent.parent

# Records the viewport, every slide's (h, v) index, and the current slide's
# links and anchor ids into a hidden <pre>, once the deck has settled.
PROBE = '''<script>
window.addEventListener('load', function () {
  setTimeout(function () {
    var slide = Reveal.getCurrentSlide(), links = [], ids = [];
    slide.querySelectorAll('a[href]').forEach(function (a) {
      Array.prototype.forEach.call(a.getClientRects(), function (r) {
        if (r.width > 0 && r.height > 0)
          links.push({href: a.getAttribute('href'), x: r.left, y: r.top, w: r.width, h: r.height});
      });
    });
    slide.querySelectorAll('[id]').forEach(function (e) { ids.push(e.id); });
    var slides = Reveal.getSlides().map(function (s) {
      var i = Reveal.getIndices(s); return [i.h, i.v || 0];
    });
    var pre = document.createElement('pre');
    pre.id = 'reveal-to-pdf'; pre.style.display = 'none';
    pre.textContent = JSON.stringify({iw: innerWidth, ih: innerHeight, slides: slides,
                                      links: links, ids: ids});
    document.body.appendChild(pre);
  }, %(delay)d);
});
</script>'''


def chrome_command():
    if os.environ.get('CHROME'):
        return shlex.split(os.environ['CHROME'])
    for name in BROWSERS:
        if shutil.which(name):
            return [name]
    if shutil.which('flatpak'):
        for app in FLATPAK_BROWSERS:
            if subprocess.run(['flatpak', 'info', app], capture_output=True).returncode == 0:
                return ['flatpak', 'run', app]
    sys.exit('No Chromium or Chrome found; set CHROME to the browser command')


class Browser:
    def __init__(self, workdir, width, budget):
        self.cmd = chrome_command()
        if self.cmd[:2] == ['flatpak', 'run']:
            # The sandbox needs to read the working directory.
            self.cmd = self.cmd[:2] + [f'--filesystem={workdir}'] + self.cmd[2:]
        self.width, self.budget = width, budget

    def run(self, height, *args):
        cmd = self.cmd + ['--headless=new', '--disable-gpu', '--hide-scrollbars',
                          f'--window-size={self.width},{height}',
                          f'--virtual-time-budget={self.budget}', *args]
        return subprocess.run(cmd, capture_output=True, text=True, timeout=120).stdout

    def probe(self, url, height):
        m = re.search(r'<pre id="reveal-to-pdf"[^>]*>([^<]*)</pre>', self.run(height, '--dump-dom', url))
        if not m:
            sys.exit(f'No slide data from {url}; did the deck load?')
        return json.loads(html.unescape(m.group(1)))

    def screenshot(self, url, height, dest):
        self.run(height, f'--screenshot={dest}', url)
        if not Path(dest).exists():
            sys.exit(f'Screenshot failed for {url}')


def free_port():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


def start_hugo(site, port):
    log = tempfile.TemporaryFile(mode='w+')
    proc = subprocess.Popen(['hugo', 'server', '--bind', '127.0.0.1', '--port', str(port),
                             '--renderToMemory', '--buildFuture', '--buildDrafts'],
                            cwd=site, stdout=subprocess.DEVNULL, stderr=log)
    # The first start converts every image, which can take a few minutes.
    for _ in range(600):
        if proc.poll() is not None:
            log.seek(0)
            sys.exit('hugo server failed:\n' + log.read())
        try:
            urllib.request.urlopen(f'http://127.0.0.1:{port}/', timeout=2)
            return proc
        except urllib.error.HTTPError:
            return proc          # any HTTP answer, even a 404, means it is up
        except OSError:
            time.sleep(0.5)
    proc.terminate()
    sys.exit('hugo server did not start within 5 minutes')


def prepare(deck_html, server, delay):
    """Make the deck work from a local file and add the probe."""
    def inline(m):
        path = m.group(1)
        data = urllib.request.urlopen(urllib.parse.urljoin(server, path)).read()
        mime = 'image/svg+xml' if path.endswith('.svg') else 'image/' + path.rsplit('.', 1)[-1].replace('jpg', 'jpeg')
        return f'url(data:{mime};base64,{base64.b64encode(data).decode()})'
    # CSS images (such as the logo mask) are blocked from file://, so embed them.
    deck_html = re.sub(r'url\((/[^)\s]+\.(?:png|jpe?g|svg|gif|webp))\)', inline, deck_html)
    head = (f'<base href="{server}">'
            '<style>.reveal .controls,.reveal .progress{display:none!important}</style>'
            + PROBE % {'delay': delay})
    return deck_html.replace('<head>', '<head>' + head, 1)


def pdf_string(s):
    return '(' + s.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)') + ')'


def write_pdf(pages, dest, width, height, site_url, scale=0.5):
    """pages: [(png_path, links, ids)]. Writes JPEG pages with /Link annotations."""
    W, H = width * scale, height * scale
    page_of = {}
    for n, (_, _, ids) in enumerate(pages):
        for i in ids:
            page_of.setdefault(i, n)
    page_ids = [3 + 3 * n for n in range(len(pages))]
    objs, next_id, stats = {}, 3 + 3 * len(pages), {'web': 0, 'internal': 0, 'skipped': 0}

    def resolve(href):
        # Links to the local server become links to the live site.
        href = re.sub(r'^https?://(localhost|127\.0\.0\.1)(:\d+)?/', '/', href)
        if href.startswith('#'):
            target = page_of.get(urllib.parse.unquote(href[1:]))
            return ('page', target) if target is not None else None
        if href.startswith('/'):
            return ('uri', site_url.rstrip('/') + href)
        if re.match(r'(https?|mailto):', href):
            return ('uri', href)
        return None

    for n, (png, links, _) in enumerate(pages):
        pid = page_ids[n]
        buf = io.BytesIO()
        Image.open(png).convert('RGB').save(buf, 'JPEG', quality=88, optimize=True)
        jpg = buf.getvalue()
        objs[pid + 2] = (b'<< /Type /XObject /Subtype /Image /Width %d /Height %d /ColorSpace /DeviceRGB '
                         b'/BitsPerComponent 8 /Filter /DCTDecode /Length %d >>\nstream\n' % (width, height, len(jpg))
                         + jpg + b'\nendstream')
        content = b'q %.2f 0 0 %.2f 0 0 cm /Im0 Do Q' % (W, H)
        objs[pid + 1] = b'<< /Length %d >>\nstream\n' % len(content) + content + b'\nendstream'
        annots = []
        for link in links:
            target = resolve(link['href'])
            if not target or target == ('page', n):
                stats['skipped'] += 1
                continue
            rect = '[%.2f %.2f %.2f %.2f]' % (link['x'] * scale, H - (link['y'] + link['h']) * scale,
                                              (link['x'] + link['w']) * scale, H - link['y'] * scale)
            if target[0] == 'uri':
                action, kind = '/A << /S /URI /URI %s >>' % pdf_string(target[1]), 'web'
            else:
                action, kind = '/Dest [%d 0 R /Fit]' % page_ids[target[1]], 'internal'
            stats[kind] += 1
            objs[next_id] = ('<< /Type /Annot /Subtype /Link /Rect %s /Border [0 0 0] %s >>'
                             % (rect, action)).encode()
            annots.append(next_id)
            next_id += 1
        annot_ref = ' /Annots [%s]' % ' '.join('%d 0 R' % a for a in annots) if annots else ''
        objs[pid] = ('<< /Type /Page /Parent 2 0 R /MediaBox [0 0 %.2f %.2f] /Contents %d 0 R '
                     '/Resources << /XObject << /Im0 %d 0 R >> >>%s >>'
                     % (W, H, pid + 1, pid + 2, annot_ref)).encode()
    objs[1] = b'<< /Type /Catalog /Pages 2 0 R >>'
    objs[2] = ('<< /Type /Pages /Kids [%s] /Count %d >>'
               % (' '.join('%d 0 R' % p for p in page_ids), len(pages))).encode()

    out = io.BytesIO()
    out.write(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n')
    offsets = {}
    for num in sorted(objs):
        offsets[num] = out.tell()
        out.write(b'%d 0 obj\n' % num + objs[num] + b'\nendobj\n')
    xref, size = out.tell(), max(objs) + 1
    out.write(b'xref\n0 %d\n0000000000 65535 f \n' % size)
    for num in range(1, size):
        out.write(b'%010d 00000 n \n' % offsets[num])
    out.write(b'trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n' % (size, xref))
    Path(dest).write_bytes(out.getvalue())
    return stats


HUGO_CONFIG = """baseURL = '%(base)s'
disableKinds = ['taxonomy', 'term', 'RSS', 'sitemap', 'robotsTXT', '404']

[markup.goldmark.renderer]
  unsafe = true

[outputFormats.reveal]
  mediaType = 'text/html'
  baseName = 'presentation'
  isHTML = true

[outputs]
  page = ['reveal']

# The reveal layout converts images with resources.Get, so static/ is
# mounted as assets/ too.
[[module.mounts]]
  source = 'content'
  target = 'content'
[[module.mounts]]
  source = 'layouts'
  target = 'layouts'
[[module.mounts]]
  source = 'static'
  target = 'static'
[[module.mounts]]
  source = 'static'
  target = 'assets'
"""
LAYOUT = Path('layouts/_default/single.reveal.html')
ASSET = re.compile(r"""(?<=["'(])(/[^"'()\s]+\.(?:png|jpe?g|gif|svg|webp))""")
RELREF = re.compile(r'\{\{<\s*relref\s+"([^"#]+?)(?:\.md)?(#[^"]*)?"\s*>\}\}')


def update_from(blog, site, section, slug):
    """Copy the latest post, the reveal layout and the images they use from
    the full blog into the self-contained site, replacing what was there."""
    base = tomllib.loads((blog / 'hugo.toml').read_text())['baseURL'].rstrip('/')
    md = (blog / 'content' / section / f'{slug}.md').read_text(encoding='utf-8')
    layout = (blog / LAYOUT).read_text(encoding='utf-8')
    # Links to other posts only resolve in the full blog: point them at the live site.
    md = RELREF.sub(lambda m: f'{base}/{section}/{Path(m.group(1)).name}/{m.group(2) or ""}', md)
    for sub in ('content', 'layouts', 'static'):
        shutil.rmtree(site / sub, ignore_errors=True)
    (site / 'content' / section).mkdir(parents=True)
    (site / LAYOUT).parent.mkdir(parents=True)
    (site / 'content' / section / f'{slug}.md').write_text(md, encoding='utf-8')
    (site / LAYOUT).write_text(layout, encoding='utf-8')
    (site / 'hugo.toml').write_text(HUGO_CONFIG % {'base': base + '/'}, encoding='utf-8')
    missing = []
    for asset in sorted(set(ASSET.findall(md + layout))):
        src = blog / 'static' / asset.lstrip('/')
        if src.is_file():
            (site / 'static' / asset.lstrip('/')).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, site / 'static' / asset.lstrip('/'))
        else:
            missing.append(asset)
    if missing:
        print("Not found in the blog's static/:", ', '.join(missing), file=sys.stderr)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('-o', '--output', required=True, help='PDF to write')
    ap.add_argument('--site', default=REPO / 'presentation' / 'site', type=Path,
                    help='Hugo site to build from (default: presentation/site)')
    ap.add_argument('--update-from', type=Path, metavar='BLOG',
                    help='first refresh --site from this Hugo blog')
    ap.add_argument('--post', help='post file name without .md (default: the only post in --site)')
    ap.add_argument('--section', default='posts')
    ap.add_argument('--url', help='use a running server instead of starting hugo')
    ap.add_argument('--width', type=int, default=1920)
    ap.add_argument('--height', type=int, default=1080)
    ap.add_argument('--delay', type=int, default=2500, help='ms to let the deck settle')
    args = ap.parse_args()

    posts_dir = args.site / 'content' / args.section
    if args.update_from:
        post = args.post
        if not post:
            current = sorted(posts_dir.glob('*.md'))
            if len(current) != 1:
                sys.exit('Pass --post to say which post to copy from the blog')
            post = current[0].stem
        update_from(args.update_from, args.site, args.section, post)
    posts = sorted(posts_dir.glob('*.md'))
    slug = args.post or (posts[0].stem if len(posts) == 1 else None)
    if not slug:
        sys.exit(f'Pass --post; {posts_dir} has {len(posts)} posts')

    site_url = tomllib.loads((args.site / 'hugo.toml').read_text())['baseURL']
    hugo = None
    if args.url:
        server = args.url.rstrip('/') + '/'
    else:
        port = free_port()
        hugo = start_hugo(args.site, port)
        server = f'http://127.0.0.1:{port}/'
    try:
        deck_url = urllib.parse.urljoin(server, f'{args.section}/{slug}/presentation.html')
        deck = urllib.request.urlopen(deck_url).read().decode('utf-8')
        work = Path(tempfile.mkdtemp(prefix='reveal-to-pdf-'))
        (work / 'deck.html').write_text(prepare(deck, server, args.delay), encoding='utf-8')
        page = (work / 'deck.html').as_uri()
        browser = Browser(work, args.width, args.delay + 5500)

        # The window frame takes some height, which changes how reveal.js
        # scales the slides. Size the probe window so its viewport matches
        # the screenshots exactly.
        frame = args.height - browser.probe(page, args.height)['ih']
        probe_height = args.height + frame
        first = browser.probe(page, probe_height)
        if (first['iw'], first['ih']) != (args.width, args.height):
            sys.exit(f"Viewport is {first['iw']}x{first['ih']}, expected {args.width}x{args.height}")

        pages = []
        for n, (h, v) in enumerate(first['slides'], 1):
            png = work / f'{n:03d}.png'
            browser.screenshot(f'{page}#/{h}/{v}', args.height, png)
            info = browser.probe(f'{page}#/{h}/{v}', probe_height)
            pages.append((png, info['links'], info['ids']))
            print(f'\rslide {n}/{len(first["slides"])}', end='', file=sys.stderr, flush=True)
        print(file=sys.stderr)

        stats = write_pdf(pages, args.output, args.width, args.height, site_url)
        print(f'{args.output}: {len(pages)} pages, {stats["web"]} web links, '
              f'{stats["internal"]} internal links, {stats["skipped"]} skipped')
        shutil.rmtree(work)
    finally:
        if hugo:
            hugo.terminate()
            hugo.wait()


if __name__ == '__main__':
    main()
