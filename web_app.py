#!/usr/bin/env python3
"""Local browser interface for Arnav Katyal's ShopSmart Memory Agent."""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from memory_agent import TOP_K, answer_from_context, load_or_build_memory, make_client, retrieve

PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ShopSmart Memory Agent</title>
  <style>
    :root { font-family: Georgia, serif; background: #f4efe6; color: #201d1a; }
    * { box-sizing: border-box; }
    body { margin: 0; min-height: 100vh; background: radial-gradient(circle at 15% 10%, #f8d8a8, transparent 30%), #f4efe6; }
    main { width: min(920px, calc(100% - 32px)); margin: 0 auto; padding: 64px 0; }
    .eyebrow { color: #aa4b24; font: 700 12px/1.2 system-ui, sans-serif; letter-spacing: .14em; text-transform: uppercase; }
    h1 { max-width: 680px; margin: 14px 0 12px; font-size: clamp(42px, 8vw, 78px); line-height: .94; }
    .intro { max-width: 580px; margin: 0 0 36px; color: #665b50; font: 17px/1.55 system-ui, sans-serif; }
    form { display: flex; gap: 10px; margin-bottom: 24px; }
    input { min-width: 0; flex: 1; border: 1px solid #c9bba9; border-radius: 5px; background: #fffaf2; padding: 16px; color: inherit; font: 16px system-ui, sans-serif; }
    button { border: 0; border-radius: 5px; background: #aa4b24; padding: 0 22px; color: white; font: 700 15px system-ui, sans-serif; cursor: pointer; }
    button:disabled { opacity: .6; cursor: wait; }
    .panel { border-top: 1px solid #c9bba9; padding-top: 24px; }
    .label { color: #665b50; font: 700 12px system-ui, sans-serif; letter-spacing: .1em; text-transform: uppercase; }
    #answer { min-height: 110px; white-space: pre-wrap; font: 20px/1.5 Georgia, serif; }
    #status { color: #aa4b24; font: 14px system-ui, sans-serif; }
    @media (max-width: 600px) { main { padding: 40px 0; } form { flex-direction: column; } button { min-height: 50px; } }
  </style>
</head>
<body>
  <main>
    <div class="eyebrow">Arnav Katyal / personal AI project</div>
    <h1>Ask ShopSmart anything.</h1>
    <p class="intro">A grounded store assistant that searches its knowledge base before answering. It will say when the available information is not enough.</p>
    <form id="ask-form"><input id="question" autocomplete="off" placeholder="What is the return window for unused items?" required><button id="submit" type="submit">Ask agent</button></form>
    <section class="panel"><div class="label">Grounded answer</div><p id="answer">Your answer will appear here.</p><div id="status"></div></section>
  </main>
  <script>
    const form = document.querySelector('#ask-form'), input = document.querySelector('#question'), answer = document.querySelector('#answer'), status = document.querySelector('#status'), submit = document.querySelector('#submit');
    form.addEventListener('submit', async (event) => {
      event.preventDefault(); submit.disabled = true; answer.textContent = 'Thinking...'; status.textContent = '';
      try { const response = await fetch('/ask', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({question: input.value})}); const data = await response.json(); if (!response.ok) throw new Error(data.error); answer.textContent = data.answer; status.textContent = `Retrieved ${data.matches} relevant chunks.`; }
      catch (error) { answer.textContent = error.message; } finally { submit.disabled = false; }
    });
  </script>
</body>
</html>"""


class AppHandler(BaseHTTPRequestHandler):
    client = None
    memory = None
    top_k = TOP_K

    def do_GET(self):
        if urlparse(self.path).path != '/':
            self.send_error(404)
            return
        body = PAGE.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if urlparse(self.path).path != '/ask':
            self.send_error(404)
            return
        try:
            length = int(self.headers.get('Content-Length', 0))
            question = str(json.loads(self.rfile.read(length)).get('question', '')).strip()
            if not question:
                raise ValueError('Please enter a question.')
            hits = retrieve(self.client, self.memory, question, self.top_k)
            self.send_json(200, {'answer': answer_from_context(self.client, question, hits), 'matches': len(hits)})
        except Exception as exc:
            self.send_json(500, {'error': str(exc)})

    def send_json(self, status, payload):
        body = json.dumps(payload).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        print(f'[web] {self.address_string()} - {format % args}')


def main():
    parser = argparse.ArgumentParser(description='Run the ShopSmart browser interface')
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--reindex', action='store_true')
    args = parser.parse_args()
    client = make_client()
    AppHandler.client = client
    AppHandler.memory = load_or_build_memory(client, args.reindex)
    print(f'ShopSmart Memory Agent running at http://localhost:{args.port}')
    ThreadingHTTPServer(('127.0.0.1', args.port), AppHandler).serve_forever()


if __name__ == '__main__':
    main()