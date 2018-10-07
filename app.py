from flask import Flask , g, jsonify,json,request
from flask_restful import Resource, Api,reqparse, abort
import urllib2
import sqlite3
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BackgroundScheduler
import datetime

app = Flask(__name__)
api = Api(app)
application = app
scheduler = BackgroundScheduler()

DATABASE='baza.db'


class ClearDb(Resource):   
     def get(self):
        conn = sqlite3.connect('baza.db')
        c=conn.cursor()
        c.execute("DELETE from job")
        c.execute("Vacuum")
        conn.commit()  
        conn.close()
        return "db clear"
      
        
def get_db():
    db=getattr(g,'_databse',None)
    if db is None:
        db=g._database=sqlite3.connect(DATABASE)
    return db
    
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
        
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return rv       

def BackParse():
    conn = sqlite3.connect('baza.db')
    c=conn.cursor()
    c.execute("DELETE from job")
    c.execute("Vacuum")
    
   
    url="http://sczg.unizg.hr/student-servis/ponuda-poslova/"
    page=urllib2.urlopen(url).read().decode('utf-8')
    soup=BeautifulSoup(page,'html.parser')
    names=soup.find_all('div',attrs={'class':'jobBox'})
    for name in names:
        baseurl="http://sczg.unizg.hr"
        newurl= baseurl+name.find('a',attrs={'class':'bLink'}).get('href')
        newpage=urllib2.urlopen(newurl).read().decode('utf-8')
        soup=BeautifulSoup(newpage,'html.parser')
        jobs=soup.find('div',attrs={'class':'newsItem'})
        now=datetime.datetime.now()
        c.execute('''INSERT INTO job (Ime, Naslov, vrijeme)VALUES(?,?,?)''', (jobs.h1.get_text(),jobs.div.get_text(),now))       
                           
    urls=["http://sczg.unizg.hr/student-servis/vijest/2015-04-14-poslovi-u-ugostiteljstvu/",
            "http://sczg.unizg.hr/student-servis/vijest/2015-04-14-fizicki-poslovi/",
            "http://sczg.unizg.hr/student-servis/vijest/2015-04-14-razni-poslovi/",
            "http://sczg.unizg.hr/student-servis/vijest/2015-04-14-rad-u-skladistima/",
            "http://sczg.unizg.hr/student-servis/vijest/2015-04-14-poslovi-promidzbe/",
            "http://sczg.unizg.hr/student-servis/vijest/2015-04-14-poslovi-u-proizvodnji/",
            "http://sczg.unizg.hr/student-servis/vijest/2015-04-14-poslovi-u-turizmu/",
            "http://sczg.unizg.hr/student-servis/vijest/2015-04-14-poslovi-u-administraciji/",
            "http://sczg.unizg.hr/student-servis/vijest/2015-04-14-poslovi-u-trgovini/",
            "http://sczg.unizg.hr/student-servis/vijest/2015-04-14-poslovi-ciscenja/"]
    for url in urls:
        
        page=urllib2.urlopen(url).read().decode('utf-8')
        soup=BeautifulSoup(page,'html.parser')
        poslovi=soup.find('div',attrs={'class':'newsItem'})         
        posao=poslovi.find_all('p')
        for p in posao:
            if len(p.get_text().encode('utf-8'))>15:
                now=datetime.datetime.now()
                c.execute('''INSERT INTO job (Ime, Naslov, vrijeme)VALUES(?,?,?)''', (p.get_text()[5:],p.get_text()[5:],now))  
    conn.commit()  
    conn.close()    
    pass
          

class JobBox(Resource):
    def get(self):
        data=[]
        conn = sqlite3.connect('baza.db')
        c=conn.cursor()
        c.execute("SELECT * FROM jobbox")
        result=c.fetchall()
        for x in result:
            data.append({"id":x[0],
            "Naslov":x[1],
            "Opis":x[2],
            "Timestamp":x[3]})
        return jsonify(data)
        
    def post(self):
        indata=request.get_json(force=True)
        Ime=indata['Naslov']
        Opis=indata['Opis']
        now=datetime.datetime.now()
        conn = sqlite3.connect('baza.db')
        c=conn.cursor()
        c.execute('''INSERT INTO jobbox (Ime, Naslov, vrijeme)
                  VALUES(?,?,?)''', (Ime,Opis,now))
        conn.commit()
        conn.close()
        return jsonify({'Write':"ok"})

class Job(Resource):
    def get(self):
        data=[]
        conn = sqlite3.connect('baza.db')
        c=conn.cursor()
        c.execute("SELECT * FROM job")
        result=c.fetchall()
        for x in result:
            data.append({"id":x[0],
            "Naslov":x[1],
            "Opis":x[2],
            "Timestamp":x[3]})
        return jsonify(data)
        
    
   
class JobParser(Resource):
    def get(self):
        conn = sqlite3.connect('baza.db')
        c=conn.cursor()
        c.execute("DELETE from job")
        c.execute("Vacuum")
        
        url="http://sczg.unizg.hr/student-servis/ponuda-poslova/"
        page=urllib2.urlopen(url).read().decode('utf-8')
        soup=BeautifulSoup(page,'html.parser')
        names=soup.find_all('div',attrs={'class':'jobBox'})
        for name in names:
            baseurl="http://sczg.unizg.hr"
            newurl= baseurl+name.find('a',attrs={'class':'bLink'}).get('href')
            newpage=urllib2.urlopen(newurl).read().decode('utf-8')
            soup=BeautifulSoup(newpage,'html.parser')
            jobs=soup.find('div',attrs={'class':'newsItem'})
            now=datetime.datetime.now()
               
            c.execute('''INSERT INTO job (Ime, Naslov, vrijeme)
                        VALUES(?,?,?)''', (jobs.h1.get_text(),jobs.div.get_text(),now))
                                          
                               
                               
        urls=["http://sczg.unizg.hr/student-servis/vijest/2015-04-14-poslovi-u-ugostiteljstvu/",
                "http://sczg.unizg.hr/student-servis/vijest/2015-04-14-fizicki-poslovi/",
                "http://sczg.unizg.hr/student-servis/vijest/2015-04-14-razni-poslovi/",
                "http://sczg.unizg.hr/student-servis/vijest/2015-04-14-rad-u-skladistima/",
                "http://sczg.unizg.hr/student-servis/vijest/2015-04-14-poslovi-promidzbe/",
                "http://sczg.unizg.hr/student-servis/vijest/2015-04-14-poslovi-u-proizvodnji/",
                "http://sczg.unizg.hr/student-servis/vijest/2015-04-14-poslovi-u-turizmu/",
                "http://sczg.unizg.hr/student-servis/vijest/2015-04-14-poslovi-u-administraciji/",
                "http://sczg.unizg.hr/student-servis/vijest/2015-04-14-poslovi-u-trgovini/",
                "http://sczg.unizg.hr/student-servis/vijest/2015-04-14-poslovi-ciscenja/"]
        for url in urls:
         
            page=urllib2.urlopen(url).read().decode('utf-8')
            soup=BeautifulSoup(page,'html.parser')
            poslovi=soup.find('div',attrs={'class':'newsItem'})         
            posao=poslovi.find_all('p')
            for p in posao:
                if len(p.get_text().encode('utf-8'))>15:
                    now=datetime.datetime.now()
                    c.execute('''INSERT INTO job (Ime, Naslov, vrijeme)
                    VALUES(?,?,?)''', (p.get_text()[5:],p.get_text()[5:],now))
                               
        conn.commit()  
        conn.close()   
        return "update complete"

    
    
class HelloWorld(Resource):
    def get(self):
        now=datetime.datetime.now()
        return jsonify({'hello': 'Hello cruel world , latest version:',
                        'time':now})
 

scheduler.add_job(BackParse, 'interval', hours=48)
scheduler.start()


api.add_resource(HelloWorld,'/')
api.add_resource(Job,'/job')
api.add_resource(JobBox,'/jobbox')
api.add_resource(ClearDb,'/kill')
api.add_resource(JobParser,'/update')


if __name__ == '__main__':
    app.run()