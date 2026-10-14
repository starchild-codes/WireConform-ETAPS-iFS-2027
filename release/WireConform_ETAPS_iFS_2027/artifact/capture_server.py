"""Local, deterministic HTTP request capture server (stdlib only)."""
from http.server import HTTPServer,BaseHTTPRequestHandler
from pathlib import Path
from datetime import datetime,timezone
import json,sys, threading
from urllib.parse import urlsplit

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        raw_path=self.path
        fragments=urlsplit(raw_path).path.split('/')
        case_id=fragments[2] if len(fragments)>2 and fragments[1]=='cases' else 'unknown'
        row={'case_id':case_id,'url':raw_path,'headers':dict(self.headers),
             'received_utc':datetime.now(timezone.utc).isoformat()}
        # Append under lock to avoid multiple-client interleaving.
        with self.server.lock:
            with open(self.server.output,'a',encoding='utf-8') as f:
                f.write(json.dumps(row)+'\n')
        self.send_response(204)
        self.send_header('Content-Length','0')
        self.end_headers()
    def log_message(self,*args):pass

if __name__=='__main__':
    output=Path(sys.argv[1] if len(sys.argv)>1 else 'observations.jsonl')
    output.parent.mkdir(parents=True,exist_ok=True)
    srv=HTTPServer(('127.0.0.1',8765),Handler)
    srv.lock=threading.Lock();srv.output=output
    print(f'Listening on 127.0.0.1:8765; logging to {output}',flush=True)
    srv.serve_forever()
