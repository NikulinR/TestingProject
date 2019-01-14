import sqlite3
from flask import Flask, render_template,g, request, redirect, url_for

DATABASE = 'Testing.db'
app = Flask(__name__)
db = sqlite3.connect(DATABASE, check_same_thread=False)
cur = db.cursor()
isLogined = False
isFirstTry = True
testName = ''
user = ''

class DBItem():
    
    tablename = ""
    def __init__(self, tablename):
        self.tablename = tablename
        
    #add saving
    def Delete(self, attribute, value):
        print("delete from %s where %s = '%s'"%(self.tablename, attribute, value))
        cur.execute("delete from %s where %s = '%s';"%(self.tablename, attribute, value))
        db.commit()
        
    def Create(self, args):
        cur.execute('select * from '+self.tablename)
        desc = str(list(map(lambda x: x[0], cur.description))).strip('[').strip(']').rstrip(',')
        
        print("insert into %s (%s) values (%s);"%(self.tablename,desc,str(args).strip('(').strip(')').rstrip(',')))
        
        cur.execute("insert into %s (%s) values (%s);"%(self.tablename,desc,str(args).strip('(').strip(')').rstrip(',')))
        #cur.execute("insert or replace into %s values %s"%(self.tablename,args))  
        db.commit()
        
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
    
    def Show(self):
        print('select * from '+self.tablename+";")
        cur.execute('select * from '+self.tablename+";")
        return cur.fetchall()
    
    def Search(self, param, value):
        cur.execute('select * from %s where %s = "%s"'%(self.tablename, param, value))
        return cur.fetchall()

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
        return render_template("index.html", user = user[0][0], group = user[0][2].lower())

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
    testName = request.form['testname']
    if not testName:
        return main()
    return render_template("create.html", testname=testName)

@app.route("/edit", methods=['POST'])
def edit():
    return "edit"

@app.route("/delete", methods=['POST'])
def delete():
    return "delete"



if __name__ == '__main__':
  app.run(debug = True)