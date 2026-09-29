from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
import sqlite3, json, os, datetime, mimetypes

BASE=os.path.dirname(os.path.abspath(__file__))
DB=os.path.join(BASE,'alnafay.db')
HOST=os.environ.get('HOST','0.0.0.0')
PORT=int(os.environ.get('PORT','5000'))

def db():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c

def init_db():
    c=db(); c.executescript('''
    CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,code TEXT DEFAULT '',fabric TEXT DEFAULT '',color TEXT DEFAULT '',thaan REAL DEFAULT 0,suit REAL DEFAULT 0,sale_thaan REAL DEFAULT 0,sale_suit REAL DEFAULT 0,image TEXT DEFAULT '',description TEXT DEFAULT '',sale_on INTEGER DEFAULT 0,new_arrival INTEGER DEFAULT 0,stock INTEGER DEFAULT 1);
    CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY AUTOINCREMENT,created_at TEXT NOT NULL,product_id INTEGER DEFAULT 0,product TEXT DEFAULT '',tone TEXT DEFAULT '',option TEXT DEFAULT '',unit_price REAL DEFAULT 0,quantity INTEGER DEFAULT 1,total REAL DEFAULT 0,name TEXT DEFAULT '',email TEXT DEFAULT '',phone TEXT DEFAULT '',city TEXT DEFAULT '',address TEXT DEFAULT '',note TEXT DEFAULT '',status TEXT DEFAULT 'Pending');
    CREATE TABLE IF NOT EXISTS settings(id INTEGER PRIMARY KEY CHECK(id=1),name TEXT,tagline TEXT,wa TEXT,phone TEXT,ig TEXT);
    ''')
    if c.execute('SELECT COUNT(*) FROM products').fetchone()[0]==0:
        imgs=json.dumps(['/media/fabric_1.png','/media/fabric_2.png','/media/fabric_3.png','/media/fabric_4.png'])
        c.execute('''INSERT INTO products(name,code,fabric,color,thaan,suit,sale_thaan,sale_suit,image,description,sale_on,new_arrival,stock) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)''',('Premium Black','AN-SC-BLK-001','Premium Gents Unstitched','Black',3843,5243,0,0,imgs,'Premium black fabric. Four product views are shown on the card and product page.',0,1,1))
    if c.execute('SELECT COUNT(*) FROM settings').fetchone()[0]==0:c.execute('INSERT INTO settings(id,name,tagline) VALUES(1,?,?)',('AL NAFAY','Quality · Comfort · Style'))
    c.commit(); c.close()

def product_dict(r):
    d=dict(r); d['sale_on']=bool(d['sale_on']); d['new_arrival']=bool(d['new_arrival']); d['stock']=bool(d['stock']); return d

def send_json(h,obj,status=200):
    raw=json.dumps(obj,ensure_ascii=False).encode(); h.send_response(status); h.send_header('Content-Type','application/json; charset=utf-8'); h.send_header('Content-Length',str(len(raw))); h.send_header('Access-Control-Allow-Origin','*'); h.end_headers(); h.wfile.write(raw)

def read_json(h):
    n=int(h.headers.get('Content-Length','0') or 0); return json.loads(h.rfile.read(n) or b'{}')

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*a): pass
    def do_OPTIONS(self):
        self.send_response(204); self.send_header('Access-Control-Allow-Origin','*'); self.send_header('Access-Control-Allow-Methods','GET,POST,PUT,DELETE,OPTIONS'); self.send_header('Access-Control-Allow-Headers','Content-Type'); self.end_headers()
    def do_GET(self):
        path=urlparse(self.path).path
        if path=='/api/products':
            c=db(); rows=c.execute('SELECT * FROM products ORDER BY id').fetchall(); c.close(); return send_json(self,[product_dict(r) for r in rows])
        if path=='/api/orders':
            c=db(); rows=c.execute('SELECT * FROM orders ORDER BY id DESC').fetchall(); c.close(); return send_json(self,[dict(r) for r in rows])
        if path=='/api/customers':
            c=db(); rows=c.execute("SELECT name,phone,email,city,address,COUNT(*) order_count,MAX(created_at) last_order_at FROM orders WHERE name<>'' GROUP BY name,phone,email,city,address ORDER BY last_order_at DESC").fetchall(); c.close(); return send_json(self,[dict(r) for r in rows])
        if path=='/api/settings':
            c=db(); r=c.execute('SELECT * FROM settings WHERE id=1').fetchone(); c.close(); return send_json(self,dict(r) if r else {})
        if path=='/' : return self.serve_file('website.html')
        if path=='/admin': return self.serve_file('admin.html')
        if path.startswith('/media/'): return self.serve_file(path.lstrip('/'))
        if path.endswith('.html') and os.path.isfile(os.path.join(BASE,path.lstrip('/'))): return self.serve_file(path.lstrip('/'))
        return send_json(self,{'error':'Not found'},404)
    def do_POST(self):
        path=urlparse(self.path).path; d=read_json(self)
        if path=='/api/products':
            c=db(); cur=c.execute('''INSERT INTO products(name,code,fabric,color,thaan,suit,sale_thaan,sale_suit,image,description,sale_on,new_arrival,stock) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)''',(d.get('name','Unnamed Product'),d.get('code',''),d.get('fabric',''),d.get('color',''),d.get('thaan',0),d.get('suit',0),d.get('sale_thaan',0),d.get('sale_suit',0),d.get('image',''),d.get('description',''),int(bool(d.get('sale_on'))),int(bool(d.get('new_arrival'))),int(bool(d.get('stock',True))))); c.commit(); r=c.execute('SELECT * FROM products WHERE id=?',(cur.lastrowid,)).fetchone(); c.close(); return send_json(self,product_dict(r),201)
        if path=='/api/orders':
            now=datetime.datetime.now().isoformat(sep=' ',timespec='seconds'); c=db(); cur=c.execute('''INSERT INTO orders(created_at,product_id,product,tone,option,unit_price,quantity,total,name,email,phone,city,address,note,status) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',(now,d.get('product_id',0),d.get('product',''),d.get('tone',''),d.get('option',''),d.get('unit_price',0),d.get('quantity',1),d.get('total',0),d.get('name',''),d.get('email',''),d.get('phone',''),d.get('city',''),d.get('address',''),d.get('note',''),'Pending')); c.commit(); r=c.execute('SELECT * FROM orders WHERE id=?',(cur.lastrowid,)).fetchone(); c.close(); return send_json(self,dict(r),201)
        if path=='/api/settings':
            c=db(); c.execute('INSERT INTO settings(id,name,tagline,wa,phone,ig) VALUES(1,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET name=excluded.name,tagline=excluded.tagline,wa=excluded.wa,phone=excluded.phone,ig=excluded.ig',(d.get('name','AL NAFAY'),d.get('tagline','Quality · Comfort · Style'),d.get('wa',''),d.get('phone',''),d.get('ig',''))); c.commit(); r=c.execute('SELECT * FROM settings WHERE id=1').fetchone(); c.close(); return send_json(self,dict(r))
        return send_json(self,{'error':'Not found'},404)
    def do_PUT(self):
        path=urlparse(self.path).path; d=read_json(self)
        if path.startswith('/api/products/'):
            pid=int(path.rsplit('/',1)[1]); fields=['name','code','fabric','color','thaan','suit','sale_thaan','sale_suit','image','description','sale_on','new_arrival','stock']; vals=[]
            c=db();
            if not c.execute('SELECT 1 FROM products WHERE id=?',(pid,)).fetchone(): c.close(); return send_json(self,{'error':'Product not found'},404)
            for f in fields:
                v=d.get(f); v=int(bool(v)) if f in ('sale_on','new_arrival','stock') else v; vals.append(v)
            c.execute('UPDATE products SET '+','.join(f+'=?' for f in fields)+' WHERE id=?',vals+[pid]); c.commit(); r=c.execute('SELECT * FROM products WHERE id=?',(pid,)).fetchone(); c.close(); return send_json(self,product_dict(r))
        if path.startswith('/api/orders/'):
            oid=int(path.rsplit('/',1)[1]); status=d.get('status','Pending')
            if status not in ('Pending','Confirmed','Completed','Cancelled'): return send_json(self,{'error':'Invalid status'},400)
            c=db(); c.execute('UPDATE orders SET status=? WHERE id=?',(status,oid)); c.commit(); r=c.execute('SELECT * FROM orders WHERE id=?',(oid,)).fetchone(); c.close(); return send_json(self,dict(r) if r else {'error':'Order not found'},200 if r else 404)
        return send_json(self,{'error':'Not found'},404)
    def do_DELETE(self):
        path=urlparse(self.path).path
        if path.startswith('/api/products/'):
            pid=int(path.rsplit('/',1)[1]); c=db(); c.execute('DELETE FROM products WHERE id=?',(pid,)); c.commit(); c.close(); return send_json(self,{'ok':True})
        return send_json(self,{'error':'Not found'},404)
    def serve_file(self,rel):
        path=os.path.normpath(os.path.join(BASE,rel))
        if not path.startswith(BASE) or not os.path.isfile(path): return send_json(self,{'error':'File not found'},404)
        data=open(path,'rb').read(); typ=mimetypes.guess_type(path)[0] or 'application/octet-stream'; self.send_response(200); self.send_header('Content-Type',typ); self.send_header('Content-Length',str(len(data))); self.end_headers(); self.wfile.write(data)

if __name__=='__main__':
    init_db(); print(f'AL NAFAY running at http://localhost:{PORT}'); ThreadingHTTPServer((HOST,PORT),Handler).serve_forever()
