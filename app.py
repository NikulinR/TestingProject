import sqlite3
import time
from flask import Flask, render_template,g, request, redirect, url_for
from flask import request


DATABASE = 'Testing.db'
app = Flask(__name__)
db = sqlite3.connect(DATABASE, check_same_thread=False)
cur = db.cursor()
isLogined = False
isFirstTry = True
Collision = False
testName = ''
user = ''
curQID = 0


class DBItem():
    
    tablename = ""
    def __init__(self, tablename):
        self.tablename = tablename
        
    #add saving
    def Delete(self, attribute, value):
        print("delete from %s where %s = '%s'"%(self.tablename, attribute, value))
        cur.execute("delete from %s where %s = '%s';"%(self.tablename, attribute, value))
        db.commit()
        
    def Create(self, args, withID):
        cur.execute('select * from '+self.tablename)
        
    
        
        try:
            if withID:
                print("insert into %s (%s) values (%s);"%(self.tablename,str(list(map(lambda x: x[0], cur.description))).strip('[').strip(']').rstrip(','),str(args).strip('(').strip(')').rstrip(',')))
                cur.execute("insert into %s (%s) values (%s);"%(self.tablename,str(list(map(lambda x: x[0], cur.description))).strip('[').strip(']').rstrip(','),str(args).strip('(').strip(')').rstrip(',')))
            else:
                print("insert into %s (%s) values (%s);"%(self.tablename,str(list(map(lambda x: x[0], cur.description))[1:]).strip('[').strip(']').rstrip(','),str(args).strip('(').strip(')').rstrip(',')))
                cur.execute("insert into %s (%s) values (%s);"%(self.tablename,str(list(map(lambda x: x[0], cur.description))[1:]).strip('[').strip(']').rstrip(','),str(args).strip('(').strip(')').rstrip(',')))
            db.commit()
        
        except:
            global Collision
            Collision=True
        
    def Edit(self, setid, newrow):
        cur.execute('select * from '+self.tablename)
        desc = list(map(lambda x: x[0], cur.description))
        
        requestline = "update "+self.tablename+" set "
        
        for i in range(0, len(desc)-1):
            requestline += " "+desc[i+1]+" = "+"'"+str(newrow[i])+"'"+","
        requestline = requestline.rstrip(',')
        requestline += " WHERE "+str(desc[0])+" = "+str(setid)+";"
        print(requestline)
        cur.execute(requestline)
    
    def Show(self, column):
        #print('select * from '+self.tablename+";")
        cur.execute('select %s from %s;'%(column, self.tablename))
        return cur.fetchall()
    
    def Search(self, param, value):
        cur.execute('select * from %s where %s = "%s"'%(self.tablename, param, value))
        return cur.fetchall()

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'

@app.route("/")
def main():
    global isLogined
    global isFirstTry
    if (not isLogined):
        if (not isFirstTry):            
            return render_template("signin.html", repass = True)            
        else:
            isFirstTry = False
            return render_template("signin.html", repass = False)
    else:
        tests = DBItem('Test').Show('*')
        return render_template("index.html", user = user[0][0], group = user[0][2].lower(), tests=tests)

@app.route("/signin", methods=['POST'])
def signin():
    global isLogined
    global user
    user = DBItem("User").Search('Name', request.form['login'])
    if (len(user)!=0 and user[0][1]==request.form['password']):
        isLogined = True
        return main()
    else:
        return main()

@app.route("/signout", methods=['POST'])
def signout():
    global isLogined
    isLogined = False
    return main()

@app.route("/create", methods=['POST'])
def create():
    global testName
    global Collision
    testName = request.form['testname']
    if not testName:
        return main()
    DBItem('Test').Create((testName, int(time.time())),True)
    if Collision:
        Collision = False
        return main()
    global curQID
    curQID=0
    return render_template("create.html", testname=testName)

@app.route("/edit", methods=['POST'])
def edit():
    return "edit"

@app.route("/delete", methods=['POST'])
def delete():
    DBItem('Test').Delete('Name', request.form['testname'])
    return main()

@app.route("/nextq", methods=['POST'])
def nextq():
    qtype = request.form['type']
    question = request.form['qname']
    testname = request.form['testname']
    global curQID
    if((qtype=='isText' and ('textanswer' not in dict(request.form).keys())) or (qtype=='isRadio' and ('corradioanswer' not in dict(request.form).keys())) or (qtype=='isCheck' and ('corcheckanswer' not in dict(request.form).keys()))):
        print(['textanswer'] not in dict(request.form).items())
        print(dict(request.form).items()) 
        return render_template("create.html", testname=testname)
    curQID+=1
    DBItem('Question').Create((str(testname)+'.'+str(curQID),testname,question,qtype),True)
    if qtype=='isText':
        qu = 'you chosed '+request.form['textanswer']+' in '+qtype+question
        print(qu)
        DBItem('Answer').Create((request.form['textanswer'],1,str(testname)+'.'+str(curQID)),False)
    if qtype=='isRadio':
        qu = 'you chosed '+request.form['corradioanswer']+' in '+qtype+question
        print(qu)
        req = list(dict(request.form).items())
        for item in req:
            if item[0][:-1] in 'radioanswer':
                if item[0][-1:]==request.form['corradioanswer']:
                    DBItem('Answer').Create((item[1][0],1,str(testname)+'.'+str(curQID)),False)
                else:
                    DBItem('Answer').Create((item[1][0],0,str(testname)+'.'+str(curQID)),False)
        
    if qtype=='isCheck':
        qu = 'you chosed '+str(request.form.getlist('corcheckanswer'))+' in '+qtype+question
        print(qu) 
        req = list(dict(request.form).items())
        for item in req:
            if item[0][:-1] in 'checkanswer':
                if item[0][-1:] in request.form.getlist('corcheckanswer'):
                    DBItem('Answer').Create((item[1][0],1,str(testname)+'.'+str(curQID)),False)
                else:
                    DBItem('Answer').Create((item[1][0],0,str(testname)+'.'+str(curQID)),False)
    return render_template("create.html", testname=testname)

@app.route("/finishq", methods=['POST'])
def finishq():
    qtype = request.form['type']
    question = request.form['qname']
    testname = request.form['testname']
    global curQID
    if((qtype=='isText' and ('textanswer' not in dict(request.form).keys())) or (qtype=='isRadio' and ('corradioanswer' not in dict(request.form).keys())) or (qtype=='isCheck' and ('corcheckanswer' not in dict(request.form).keys()))):
        print(['textanswer'] not in dict(request.form).items())
        print(dict(request.form).items()) 
        return render_template("create.html", testname=testname)
    curQID+=1
    DBItem('Question').Create((str(testname)+'.'+str(curQID),testname,question,qtype),True)
    if qtype=='isText':
        qu = 'you chosed '+request.form['textanswer']+' in '+qtype+question
        print(qu)
        DBItem('Answer').Create((request.form['textanswer'],1,str(testname)+'.'+str(curQID)),False)
    if qtype=='isRadio':
        qu = 'you chosed '+request.form['corradioanswer']+' in '+qtype+question
        print(qu)
        req = list(dict(request.form).items())
        for item in req:
            if item[0][:-1] in 'radioanswer':
                if item[0][-1:]==request.form['corradioanswer']:
                    DBItem('Answer').Create((item[1][0],1,str(testname)+'.'+str(curQID)),False)
                else:
                    DBItem('Answer').Create((item[1][0],0,str(testname)+'.'+str(curQID)),False)
        
    if qtype=='isCheck':
        qu = 'you chosed '+str(request.form.getlist('corcheckanswer'))+' in '+qtype+question
        print(qu) 
        req = list(dict(request.form).items())
        for item in req:
            if item[0][:-1] in 'checkanswer':
                if item[0][-1:] in request.form.getlist('corcheckanswer'):
                    DBItem('Answer').Create((item[1][0],1,str(testname)+'.'+str(curQID)),False)
                else:
                    DBItem('Answer').Create((item[1][0],0,str(testname)+'.'+str(curQID)),False)
    return main()

@app.route("/start", methods=['POST'])
def start():
    testname = request.form['testname']
    testquestions = DBItem('Question').Search('TestName',testname)
    qnames = list(map(lambda x:x[2], testquestions))
    qnums = list(map(lambda x:x[0], testquestions))
    qtype = list(map(lambda x:x[3], testquestions))
    testdict = {}
    for i in range(len(qnames)):
        res = list(map(lambda x:x[1], DBItem('Answer').Search('QuestionId',qnums[i])))
        res = (res,qtype[i],qnums[i])
        testdict[qnames[i]] = res
    return render_template('passing.html', testdict = testdict, testname=testname)

@app.route("/handler", methods=['POST'])
def handler():
    req = dict(request.form)
    testname = request.form['testname']
    reqquestions = list(filter(lambda x: 'user_' in x, req))
    reqquestionid = list(filter(lambda x: 'qid' in x, req))
    for item in reqquestionid:
        questionid = item[4:]
        print(questionid)
        qname = DBItem('Question').Search('Number', questionid)[2]
        answers = req['user_'+str(qname)]
    return render_template('results.html', req = req)

if __name__ == '__main__':
  app.run(debug = True)