from flask import Flask, render_template, request, redirect,flash,session
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import json
import requests
import time
import math
from datetime import datetime
import hashlib
import requests
from requests.api import head
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import itertools
import string
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OrdinalEncoder
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super secret key'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///feedback.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)

# em=""
# pa=""

class ContactUs(db.Model):
    sno=db.Column(db.Integer, primary_key=True)
    fname=db.Column(db.String(20), nullable=False)
    lname=db.Column(db.String(20), nullable=False)
    gender=db.Column(db.String(7), nullable=False)
    phone=db.Column(db.Integer, nullable=False)
    email=db.Column(db.String(20), nullable=False)
    msg=db.Column(db.String(500), nullable=False)
    response=db.Column(db.String(500), nullable=True)

class registration(db.Model):
    sno=db.Column(db.Integer, primary_key=True)
    fname=db.Column(db.String(20), nullable=False)
    lname=db.Column(db.String(20), nullable=False)
    gender=db.Column(db.String(7), nullable=False)
    phone=db.Column(db.Integer, nullable=False)
    email=db.Column(db.String(50), nullable=False)
    role=db.Column(db.String(10),nullable=False)
    status=db.Column(db.String(10),nullable=False)
    password=db.Column(db.String(20), nullable=False)
    
class weather(db.Model):
    sno=db.Column(db.Integer, primary_key=True) 
    Email=db.Column(db.String(50), nullable=False)
    City=db.Column(db.String(20), nullable=False)
    Longitude=db.Column(db.String(20), nullable=False)
    Latitude=db.Column(db.String(20), nullable=False)
    Weather=db.Column(db.String(20), nullable=False)
    Temperature=db.Column(db.String(20), nullable=False)
    Feels_Like=db.Column(db.String(20), nullable=False)
    Pressure=db.Column(db.String(20), nullable=False)
    Humidity=db.Column(db.String(20), nullable=False)
    Wind=db.Column(db.String(20), nullable=False)
    Time=db.Column(db.String(20), nullable=False)

class feedback(db.Model):
    sno=db.Column(db.Integer, primary_key=True) 
    Email=db.Column(db.String(20), nullable=False)
    Feedb=db.Column(db.String(50), nullable=False)
    Time=db.Column(db.String(20), nullable=False)

class cropdetails(db.Model):
    Sno=db.Column(db.Integer, primary_key=True)
    Crop=db.Column(db.String(20), nullable=False)
    Details=db.Column(db.String(500), nullable=False)
    ImgName=db.Column(db.String(30), nullable=False)
         

@app.route("/admin/",methods=["GET","POST"])
def adminlogin():
    # global em,pa
    if 'email' in session and session['role']=="Admin":
        flash("You are already login","success")
        return render_template('admin/home.html',se=session['logo'])

    if request.method=="POST":
        email=request.form['email']
        password=request.form['password']
        
        if email=="" or password=="":
            flash("Please Enter Email or Password","warning")
            return redirect("/admin/")
        
        p = hashlib.md5(password.encode())
        lo=registration.query.all()
        
        for i in lo:
            if email==i.email:
                if i.status=="Blocked":
                    flash(i.email+" is blocked by our admin","warning")
                    return redirect("/admin/")

                if i.role=="User":
                    flash("You are not authorized to access this page!!","warning")
                    return redirect("/admin/")

                if p.hexdigest()!=i.password:
                    flash("Invalid Email or Password!!","warning")
                    return redirect("/admin/")
                # em=i.email
                # pa=i.password
                session['email']=email
                session['logo']=(i.fname[0:1]+i.lname[0:1]).upper()
                session['role']=i.role
                break
            # if em=="" and pa="":
        if 'email' in session:
            return redirect("/admin/home")
        else:
            return redirect("/admin/")

    return render_template("admin/adminlogin.html")

@app.route("/admin/signup",methods=["GET","POST"])
def adminsignup():

    if 'email' in session:
        flash("You are already login","success")
        return render_template('home.html',se=session['logo'])


    if request.method=="POST":
        fname=request.form['fname']
        lname=request.form['lname']
        gender=request.form['gender']
        phone=request.form['phone']
        email=request.form['email']
        password=request.form['password']
        
        if fname=="" or lname=="" or len(phone)!=10 or email=="" or password=="":
            flash("Please fill all the feilds and phone number should be of 10 digits","warning")
            return redirect("/admin/signup")
        else:
            p = hashlib.md5(password.encode())
            log=registration(fname=fname,lname=lname,gender=gender,phone=phone,email=email,password=p.hexdigest(),role="Admin",status="None")
            db.session.add(log)
            db.session.commit()
            flash("Successfully Sign Up","success")
            return redirect("/admin/")
        
    return render_template("admin/adminregister.html")

@app.route("/admin/home")
def adminhome():
    if 'email' in session and session['role']=="Admin":
        return render_template("/admin/home.html",se=session['logo'])
    else:
        return redirect("/admin/")

@app.route("/admin/users")
def users():
    if 'email' in session and session['role']=="Admin":
        allfeed=registration.query.filter_by(role='User').all()
        return render_template("admin/user.html",allfeed=allfeed,se=session['logo'])
    else:
        return redirect("/admin/")

@app.route("/admin/status/<string:email>")
def status(email):
    if 'email' in session and session['role']=="Admin":
        s=registration.query.filter_by(email=email).first()
        if s.status=="Unblocked":
            s.status="Blocked"
        else:
            s.status="Unblocked"
        a=s.status
        db.session.add(s)
        db.session.commit()
        flash(email+" is "+a+" successfully","success")
        return redirect("/admin/users")

@app.route("/admin/profile/<string:email>")
def pro(email):
    if 'email' in session and session['role']=="Admin":
        r=registration.query.filter_by(email=email).first()
        f=feedback.query.filter_by(Email=email).all()
        c=ContactUs.query.filter_by(email=email).all()
        w=weather.query.filter_by(Email=email).all()
        return render_template("admin/profile.html",r=r,f=f,c=c,w=w,se=session['logo'])

@app.route("/admin/Feedbacks")
def feed():
    if 'email' in session and session['role']=="Admin":
        f=feedback.query.all()
        return render_template("/admin/feedback.html",f=f,se=session['logo'])
    else:
        return redirect("/admin")

@app.route("/admin/ContactUs")
def quer():
    if 'email' in session and session['role']=="Admin":
        c=ContactUs.query.all()
        return render_template("admin/queries.html",c=c,se=session['logo'])
    else:
        return redirect("/admin")

@app.route("/admin/delete/<string:email>/<int:sno>")
def delete(email,sno):
    # if em !="" and pa !="":   
    if 'email' in session and session['role']=="Admin":
        f=feedback.query.filter_by(Email=email,sno=sno).first()
        db.session.delete(f)
        db.session.commit()
        flash(email+" feedback is successfully deleted","success")
        return redirect('/admin/users')
    else:
        return redirect("/")

@app.route("/admin/response/<string:email>/<int:sno>",methods=['GET','POST'])
def resp(email,sno):
    # if em !="" and pa !="":   
    if 'email' in session and session['role']=="Admin":
        if request.method=='POST':
            r=request.form['response']
            c=ContactUs.query.filter_by(email=email,sno=sno).first()
            c.response=r
            db.session.add(c)
            db.session.commit()
            flash(email+" response send is successfully","success")
        return redirect('/admin/users')
    else:
        return redirect("/")


@app.route("/admin/profile")
def adprofile():
    if 'email' in session and session['role']=="Admin":
        lo=registration.query.filter_by(email=session['email']).first()
        return render_template("/admin/myprofile.html",lo=lo,se=session['logo'])
    else:
        return redirect("/admin/")

@app.route("/admin/profileupdate",methods=["GET","POST"])
def adprofileupdate():
    if 'email' in session and session['role']=="Admin":
        if request.method=='POST':
            fname=request.form['fname']
            lname=request.form['lname']
            gender=request.form['gender']
            phone=request.form['phone']
            cpass=request.form['cpassword']
            npass=request.form['npassword']
            copass=request.form['copassword']

            re=registration.query.filter_by(email=session['email']).first()
            
            if cpass!="":
                c=hashlib.md5(cpass.encode())
                if c.hexdigest()!=re.password:
                    flash("Invalid Current Password","warning")
                    return redirect("/admin/profile")
                else:
                    if npass=="":
                        flash("New password is empty string","warning")
                        return redirect("/admin/profile")
                    
                    elif npass!=copass:
                        flash("New and Confirm password does not matched","warning")
                        return redirect("/admin/profile")
                    n=hashlib.md5(npass.encode())
                    re.password=n.hexdigest()            
            re.fname=fname
            re.lname=lname
            re.gender=gender
            re.phone=phone
            session['logo']=(fname[0:1]+lname[0:1]).upper()

            db.session.add(re)
            db.session.commit()
            flash("Your profile is successfully updated","success")

            return redirect('/admin/profile')

    else:
        redirect("/admin/")

@app.route("/",methods=["GET","POST"])
def login():
    # global em,pa
    if 'email' in session:
        flash("You are already login","success")
        return render_template('home.html',se=session['logo'])

    if request.method=="POST":
        email=request.form['email']
        password=request.form['password']
        
        if email=="" or password=="":
            flash("Please Enter Email or Password","warning")
            return redirect("/")
        
        p = hashlib.md5(password.encode())
        lo=registration.query.all()
        e=0
        s=0
        for i in lo:
            if email==i.email:
                e=1
                if i.status=="Blocked":
                    s=1
                    break
                if p.hexdigest()==i.password:
                # em=i.email
                # pa=i.password
                  session['email']=email
                  session['logo']=(i.fname[0:1]+i.lname[0:1]).upper()
                  session['role']=i.role
                  break
        # if em=="" and pa="":
        if 'email' in session:
            return redirect("/home")
        else:
            if e==1:  
              if s==1:
                  flash(i.email+" is blocked by our admin!!","warning")
              else:
                   flash("Invalid Email or Password","warning")
            else:
              flash("You may have not signed up!!","warning")
            return redirect("/")

    return render_template("login.html")

@app.route("/signup",methods=["GET","POST"])
def signup():

    if 'email' in session:
        flash("You are already login","success")
        return render_template('home.html',se=session['logo'])


    if request.method=="POST":
        fname=request.form['fname']
        lname=request.form['lname']
        gender=request.form['gender']
        phone=request.form['phone']
        email=request.form['email']
        password=request.form['password']
        
        if fname=="" or lname=="" or len(phone)!=10 or email=="" or password=="":
            flash("Please fill all the feilds and phone number should be of 10 digits","warning")
            return redirect("/signup")
        else:
            p = hashlib.md5(password.encode())
            log=registration(fname=fname,lname=lname,gender=gender,phone=phone,email=email,password=p.hexdigest(),role="User",status="Unblocked")
            db.session.add(log)
            db.session.commit()
            flash("Successfully Sign Up","success")
            return redirect("/")
        
    return render_template("register.html")

@app.route("/logout")
def logout():
    # global em,pa
    # em=""
    # pa=""
    # r=session['role']
    session.pop('email')
    session.pop('logo')
    session.pop('role')
    # if r=="Admin":
    #    return redirect("/admin/")
    # else:

    return redirect("/")

@app.route("/profile")
def profile():
    if 'email' in session:
        lo=registration.query.filter_by(email=session['email']).first()
        return render_template("profile.html",lo=lo,se=session['logo'])
    else:
        return redirect("/")

@app.route("/profileupdate",methods=["GET","POST"])
def profileupdate():
    if 'email' in session:
        if request.method=='POST':
            fname=request.form['fname']
            lname=request.form['lname']
            gender=request.form['gender']
            phone=request.form['phone']
            cpass=request.form['cpassword']
            npass=request.form['npassword']
            copass=request.form['copassword']

            re=registration.query.filter_by(email=session['email']).first()
            
            if cpass!="":
                c=hashlib.md5(cpass.encode())
                if c.hexdigest()!=re.password:
                    flash("Invalid Current Password","warning")
                    return redirect("/profile")
                else:
                    if npass=="":
                        flash("New password is empty string","warning")
                        return redirect("/profile")
                    
                    elif npass!=copass:
                        flash("New and Confirm password does not matched","warning")
                        return redirect("/profile")
                    n=hashlib.md5(npass.encode())
                    re.password=n.hexdigest()            
            re.fname=fname
            re.lname=lname
            re.gender=gender
            re.phone=phone
            session['logo']=(fname[0:1]+lname[0:1]).upper()

            db.session.add(re)
            db.session.commit()
            flash("Your profile is successfully updated","success")

            return redirect('/profile')

    else:
        redirect("/")

@app.route("/home")
def hello_world():
    # if em !="" and pa !="":
    if 'email' in session:
        return render_template("home.html",se=session['logo'])
    else:
        return redirect("/")

@app.route("/currentwea",methods=['GET','POST'])
def currentwea():
    # if em !="" and pa !="":
    if 'email' in session:
        im=""
        co=""
        if request.method=='POST':
            c=request.form['city']
            if c=="":
                return render_template("currentwea.html",l={'0':0},se=session['logo'],c='red')
            else:
               url="https://api.openweathermap.org/data/2.5/weather?appid=850789bc308ec795c19f9f4df7ed367d&q="+c
               
               d=requests.get(url).json()
               l=dict(d)
               if l['cod']!='404':
                    t=time.strftime('%H:%M:%S', time.gmtime(l['dt']-l['timezone']))
                    l['dth']=t
                    l['main']['temp']=round(l['main']['temp']-273.15,2)

                    we=weather(Email=session['email'],City=l['name'],Longitude=l['coord']['lon'],Latitude=l['coord']['lon'],Weather=l['weather'][0]['main'],Temperature=(l['main']['temp']-273.15),Feels_Like=(l['main']['feels_like']-273.15),Pressure=l['main']['pressure'],Humidity=l['main']['humidity'],Wind=l['wind']['speed'],Time=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
                    db.session.add(we)
                    db.session.commit()
                    
                    if l['weather'][0]['main']=="Clear":
                        im="Clear Sky.jpeg"
                        co="black"
                    elif l['weather'][0]['main']=="Snow" or l['weather'][0]['main']=="Winter":
                        im="Winter.jpeg"
                        co="black"
                    elif l['weather'][0]['main']=="Sunny":
                        im="Sunny.jpeg"
                        co="black"
                    elif l['weather'][0]['main']=="Cloudy" or l['weather'][0]['main']=="Smoke" or l['weather'][0]['main']=="Clouds":
                        im="Cloudy.jpeg"
                        co="white"
                    elif l['weather'][0]['main']=="Rainy":
                        im="Rainy.jpeg"
                        co="white"
                    else:
                        im="General.jpeg"
                        co="white"

               return render_template("currentwea.html",l=l,se=session['logo'],im=im,co=co)

        return render_template("currentwea.html",l={'0':0},se=session['logo'],c='black')
    else:
        return redirect("/")

@app.route("/history")
def history():
    if 'email' in session:
        c = weather.query.filter_by(Email=session['email']).all()
        last = math.ceil(len(c)/3)
        print(last)
        page = request.args.get('page')
        if (not str(page).isnumeric()):
            page = 1
        page = int(page)
        c = c[(page-1)*3:(page-1)*3+ 3]
        
        if last==1:
            prev = "#"
            next = "#"
        elif page==1:
            prev = "#"
            next = "/history?page="+ str(page+1)
            flash("Your are on latest history search","info")
            
        elif page==last:
            prev = "/history?page="+ str(page-1)
            next = "#"
            flash("Your are on oldest history search","info")
        else:
            prev = "/history?page="+ str(page-1)
            next = "/history?page="+ str(page+1)
        
        return render_template('history.html',se=session['logo'],allfeed=c, prev=prev, next=next)
    else:
        return redirect("/")
    

@app.route("/deletehistory/<int:sno>")
def deletehistory(sno):
    # if em !="" and pa !="":   
    if 'email' in session:
        feed=weather.query.filter_by(Email=session['email'],sno=sno).first()
        db.session.delete(feed)
        db.session.commit()
        flash("History is successfully deleted","success")
        return redirect('/history')
    else:
        return redirect("/")

@app.route("/forecast",methods=['GET','POST'])
def forecast():
    # if em !="" and pa !="":
    if 'email' in session:
    
        if request.method=='POST':
            c=request.form['city']
            if c=="":
                return render_template("forecast.html",l={'0':0},se=session['logo'],c='red')
            else:
                url="https://api.weatherbit.io/v2.0/forecast/daily?city="+c+"&key=a6a52896bb4b4e5db0316789bb323bd2"
                data=requests.get(url).json()

                d=list()

                for i in range(0,len(data['data'])):
                        t=list()
                        t.append(data['data'][i]['temp'])
                        t.append(data['data'][i]['pres'])
                        t.append(data['data'][i]['rh'])
                        t.append(data['data'][i]['wind_spd'])
                        t.append(data['data'][i]['valid_date'])
                        d.append(t)
                    
                
                return render_template("forecast.html",se=session['logo'],l=data,d=d)
        return render_template("forecast.html",l={'0':0},se=session['logo'],c='black')
    else:
        return redirect("/")

@app.route("/crop",methods=['GET','POST'])
def crop():
    if 'email' in session:
        return render_template("crop.html",l={'0':0},se=session['logo'],c='black')
    else:
        return redirect("/")
    


@app.route("/cropprediction",methods=['GET','POST'])
def cropprediction():
    # if em !="" and pa !="":
    if 'email' in session:
        im=""
        co=""
        if request.method=='POST':
            c=request.form['city']
            if c=="":
                return render_template("crop.html",l={'0':0},se=session['logo'],c='red')
            else:
            
                url = "https://api.openweathermap.org/data/2.5/forecast?q="+c+"&exclude=minutely,hourly&appid=850789bc308ec795c19f9f4df7ed367d"
                
                d=requests.get(url).json()
                myjson=dict(d)
                            
                temperature = []
                feelslike = []
                temp_min = []
                temp_max = []
                humidity = []
                weather = []
                rainfall = [] 
                for i in range(0,len(myjson['list'])):
                    temperature.append(round(myjson['list'][i]['main']['temp']-273.2))
                    humidity.append(myjson['list'][i]['main']['humidity'])
                    if "rain" not in myjson['list'][i]:
                        rainfall.append(0)
                    else:
                        rainfall.append(round(myjson['list'][i]['rain']['3h']))    

                temp = sum(temperature)/len(temperature) 
                humi = sum(humidity)/len(humidity)
                rainf = sum(rainfall)/len(rainfall)

                data = pd.read_csv("Crop_recommendation.csv")
                ord_enc = OrdinalEncoder()

                data["label_code"] = ord_enc.fit_transform(data[["label"]])

                features = data[['temperature','humidity','rainfall']]

                label = data['label_code']

                clf = KNeighborsClassifier()
                clf.fit(features.values,label)

                preds = clf.predict([[temp,humi,rainf]])
                rev = ord_enc.inverse_transform([preds])
                res = list(itertools.chain(*rev))
                a = " ".join(map(str, res))
                cro=cropdetails.query.filter_by(Crop=a).first()
                cro.Crop=cro.Crop[:1].upper()+cro.Crop[1:]
                

                return render_template("cropprediction.html",se=session['logo'],cro=cro)

        return render_template("crop.html",l={'0':0},se=session['logo'])
    else:
        return redirect("/")


@app.route("/AboutUs",methods=['GET','POST'])
def about():
    # if em !="" and pa !="":
    if 'email' in session:
        if request.method=='POST':
            f=request.form['feedback']
            if f=="":
                flash("Please enter your feedback","warning")
                return redirect("/AboutUs")
            else:
                feedb=feedback(Email=session['email'],Feedb=f,Time=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
                db.session.add(feedb)
                db.session.commit()
                flash("Your feedback is successfully send ","success")
                return redirect("/AboutUs")

        return render_template("about.html",se=session['logo'])
    else:
        return redirect("/")

@app.route("/feedback")
def feedb():
    feed = feedback.query.filter_by().all()
    last = math.ceil(len(feed)/2)
    print(last)
    page = request.args.get('page')
    if (not str(page).isnumeric()):
        page = 1
    page = int(page)
    feed = feed[(page-1)*2:(page-1)*2+ 2]
    
    if last==1:
        prev = "#"
        next = "#"
    elif page==1:
        prev = "#"
        next = "/feedback?page="+ str(page+1)
        flash("Your are on latest feedback","info")
    elif page==last:
        prev = "/feedback?page="+ str(page-1)
        next = "#"
        flash("Your are on oldest feedback","info")
    else:
        prev = "/feedback?page="+ str(page-1)
        next = "/feedback?page="+ str(page+1)
    
    return render_template('feedback.html',se=session['logo'],feed=feed, prev=prev, next=next)


@app.route("/queries")
def queries():
    c = ContactUs.query.filter_by().all()
    last = math.ceil(len(c)/2)
    
    page = request.args.get('page')
    if (not str(page).isnumeric()):
        page = 1
    page = int(page)
    c = c[(page-1)*2:(page-1)*2+ 2]
    
    if last==1:
        prev = "#"
        next = "#"
    elif page==1:
        prev = "#"
        next = "/queries?page="+ str(page+1)
        flash("Your are on latest queries","info")
        
    elif page==last:
        prev = "/queries?page="+ str(page-1)
        next = "#"
        flash("Your are on oldest queries","info")
    else:
        prev = "/queries?page="+ str(page-1)
        next = "/queries?page="+ str(page+1)
    
    return render_template('queries.html',se=session['logo'],queries=c, prev=prev, next=next)

@app.route("/ContactUs",methods=["GET","POST"])
def contact():
    # if em !="" and pa !=""4
    if 'email' in session:
        if request.method=="POST":
            fname=request.form['fname']
            lname=request.form['lname']
            gender=request.form['gender']
            phone=request.form['phone']
            email=request.form['email']
            msg=request.form['feedb']
            if msg=="":
                flash("Please enter your","warning")
                redirect("/ContactUs")
            else:
                con=ContactUs(fname=fname,lname=lname,gender=gender,phone=phone,email=email,msg=msg,response='Null')
                db.session.add(con)
                db.session.commit()
                flash("Your Message is send successfully","success")
                return redirect("/ContactUs")
        
        lo=registration.query.filter_by(email=session['email']).first()
        return render_template("contact.html",lo=lo,se=session['logo'])
 
    else:
        return redirect("/")

# contactus curd operations

    
# @app.route("/update/<int:sno>",methods=['GET','POST'])
# def update(sno):
#     # if em !="" and pa !="":    
#     if 'email' in session:
#         if request.method=='POST':
#             fname=request.form['fname']
#             lname=request.form['lname']
#             gender=request.form['gender']
#             phone=request.form['phone']
#             email=request.form['email']
#             feedb=request.form['feedb']
#             if fname=="" or lname=="" or len(phone)!=10 or email=="" or feedb=="":
#                 flash("Please fill all the feilds and phone number should be of 10 digits","warning")
#                 redirect("/update/sno")
#             else:
#                 con=ContactUs.query.filter_by(sno=sno).first()
#                 con.fname=fname
#                 con.lname=lname
#                 con.gender=gender
#                 con.phone=phone
#                 con.email=email
#                 con.feedb=feedb

#                 db.session.add(con)
#                 db.session.commit()
#                 flash("Your feedback is successfully updated","success")

#                 return redirect('/history')

#         con=ContactUs.query.filter_by(sno=sno).first()
#         return render_template('update.html',feed=con,se=session['logo'])
#     else:
#         return redirect("/")

if __name__=="__main__":
    app.run(debug=True,port=8000)