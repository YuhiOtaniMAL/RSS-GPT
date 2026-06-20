"""Daily "Top 10" digest feed.

Runs after main.py. Reads the freshly generated tech.xml and ai.xml, asks the
model to pick and rank the most important items, and writes docs/digest.xml as a
feed with one dated entry per run (older entries preserved as history).

Deliberately defensive: any failure here just skips the digest and leaves the
previous digest.xml untouched, so it can never break the main feed build.
"""
import os
import re
import json
import html
import datetime
import feedparser
from openai import OpenAI

BASE = 'docs/'
DIGEST_NAME = 'digest'
SOURCES = [('tech', 'Tech'), ('ai', 'AI')]  # which feeds feed the digest
CANDIDATES_PER_FEED = 25
TOP_N = 10
MAX_DIGEST_ENTRIES = 30  # how many days of digests to keep

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
OPENAI_BASE_URL = os.environ.get('OPENAI_BASE_URL') or 'https://api.openai.com/v1'
MODEL = os.environ.get('CUSTOM_MODEL') or 'gpt-4o-mini'
U_NAME = os.environ.get('U_NAME')
deployment_url = f'https://{U_NAME}.github.io/RSS-GPT/'


def collect_candidates():
    cands = []
    for fname, label in SOURCES:
        try:
            d = feedparser.parse(open(os.path.join(BASE, fname + '.xml')).read())
        except FileNotFoundError:
            continue
        for e in d.entries[:CANDIDATES_PER_FEED]:
            title = e.get('title', '').strip()
            link = e.get('link', '').strip()
            if not title or not link:
                continue
            snippet = ''
            body = e['content'][0].get('value', '') if e.get('content') else ''
            if 'Summary:' in body:
                snippet = re.sub('<[^>]+>', ' ', body.split('Summary:', 1)[1])
                snippet = ' '.join(snippet.split())[:200]
            cands.append({'source': label, 'title': title, 'link': link, 'snippet': snippet})
    return cands


def rank_top(cands):
    listing = "\n".join(
        f"{i}. [{c['source']}] {c['title']}" + (f" — {c['snippet']}" if c['snippet'] else "")
        for i, c in enumerate(cands)
    )
    prompt = (
        "You are a senior tech/AI news editor. Below is a numbered list of recent tech "
        "and AI items (some with a short summary). Select the "
        f"{TOP_N} MOST IMPORTANT and impactful ones and rank them most-to-least important. "
        "Prioritize substantive developments — major model/product releases, research "
        "breakthroughs, security issues, significant industry news — over minor, "
        "incremental, or promotional items, and avoid near-duplicates.\n\n"
        f"{listing}\n\n"
        f"Respond with ONLY a JSON array of exactly {TOP_N} objects, most important first, "
        'each {"index": <number from the list above>, "why": "<=15 word reason it matters"}. '
        "No prose, no code fence."
    )
    client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
    txt = client.chat.completions.create(
        model=MODEL, messages=[{"role": "user", "content": prompt}]
    ).choices[0].message.content.strip()
    txt = txt[txt.find('['): txt.rfind(']') + 1]  # tolerate code fences / stray prose
    return json.loads(txt)


def build_item_html(cands, picks):
    lis = []
    for p in picks:
        try:
            c = cands[int(p['index'])]
        except (KeyError, IndexError, ValueError, TypeError):
            continue
        title = html.escape(c['title'])
        link = html.escape(c['link'], quote=True)
        src = html.escape(c['source'])
        why = html.escape(str(p.get('why', '')).strip())
        lis.append(f'<li><a href="{link}">{title}</a> <em>[{src}]</em><br>{why}</li>')
    return "<ol>\n" + "\n".join(lis) + "\n</ol>"


def _esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def render_feed(items):
    now = datetime.datetime.now(datetime.timezone.utc).strftime('%a, %d %b %Y %H:%M:%S +0000')
    body = []
    for it in items:
        body.append(
            "<item>\n"
            f"<title>{_esc(it['title'])}</title>\n"
            f"<link>{_esc(it['link'])}</link>\n"
            f"<guid isPermaLink=\"false\">{_esc(it['guid'])}</guid>\n"
            f"<pubDate>{it['pubDate']}</pubDate>\n"
            f"<content:encoded><![CDATA[\n{it['content']}\n]]></content:encoded>\n"
            "</item>"
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/" '
        'xmlns:atom="http://www.w3.org/2005/Atom">\n<channel>\n'
        '<title>Top 10 Tech &amp; AI Digest</title>\n'
        f'<link>{deployment_url}{DIGEST_NAME}.xml</link>\n'
        f'<lastBuildDate>{now}</lastBuildDate>\n'
        + "\n".join(body) +
        '\n</channel>\n</rss>\n'
    )


def read_prior():
    items = []
    try:
        d = feedparser.parse(open(os.path.join(BASE, DIGEST_NAME + '.xml')).read())
    except FileNotFoundError:
        return items
    for e in d.entries:
        content = e['content'][0]['value'] if e.get('content') else e.get('summary', '')
        items.append({
            'title': e.get('title', ''),
            'link': e.get('link', deployment_url + DIGEST_NAME + '.xml'),
            'guid': e.get('id', e.get('title', '')),
            'pubDate': e.get('published', ''),
            'content': content,
        })
    return items


def main():
    if not OPENAI_API_KEY:
        print("digest: no OPENAI_API_KEY, skipping")
        return
    cands = collect_candidates()
    if not cands:
        print("digest: no candidates, skipping")
        return
    try:
        picks = rank_top(cands)
    except Exception as e:
        print(f"digest: ranking failed, keeping previous digest: {e}")
        return
    now = datetime.datetime.now(datetime.timezone.utc)
    date_str = now.strftime('%Y-%m-%d')
    new_item = {
        'title': f'Top 10 Tech & AI — {date_str}',
        'link': deployment_url + DIGEST_NAME + '.xml',
        'guid': f'digest-{date_str}',
        'pubDate': now.strftime('%a, %d %b %Y %H:%M:%S +0000'),
        'content': build_item_html(cands, picks),
    }
    prior = [it for it in read_prior() if it['guid'] != new_item['guid']][:MAX_DIGEST_ENTRIES - 1]
    with open(os.path.join(BASE, DIGEST_NAME + '.xml'), 'w') as f:
        f.write(render_feed([new_item] + prior))
    print(f"digest: wrote {DIGEST_NAME}.xml with {len(picks)} ranked items")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"digest: unexpected error, skipping: {e}")
