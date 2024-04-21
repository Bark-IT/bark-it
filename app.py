import random
import os
# database
#from pymongo import MongoClient

import json

#from cryptography.fernet import Fernet

from flask_socketio import SocketIO, send
from flask import (
    Flask,
    abort,
    redirect,
    render_template,
    request,
    send_file,
    send_from_directory,
    url_for,
    session
)

# email
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

global settings
settings = {}
with open("config.cfg","r") as config:
    configsplit = config.read().split("\n")
    for i in configsplit:
        if i[0] == "#":
            continue
        settingsplit = i.split("=")
        settings[settingsplit[0]] = settingsplit[1]

app = Flask(__name__)
app.config['SECRET_KEY'] = settings["key"]
socketio = SocketIO(app)





def checkemail(email):
    emailsplit = email.split("@")
    if len(emailsplit) == 1:
        return False
    return True

def makeaccount(name):
    os.makedirs("accounts/"+name)
    open("accounts/"+name+"/pages","w").write("")
    open("accounts/"+name+"/posts","w").write("")
    open("accounts/"+name+"/videos","w").write("")
    open("accounts/"+name+"/followers","w").write("")
    open("accounts/"+name+"/following","w").write("")

def transferaccount(oldname,name):
    os.rename("accounts/"+oldname+"","accounts/"+name+"")

   


def send_email(subject, body, to_email):
    gmail_user = settings["email"]
    gmail_password = settings["password"]
    message = MIMEMultipart()
    message["From"] = gmail_user
    message["To"] = to_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(gmail_user, gmail_password)
            server.sendmail(gmail_user, to_email, message.as_string())
        print("Email sent successfully.")
    except Exception as e:
        print("Error sending email:", str(e))





@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')


@socketio.on('message')
def handle_message(message):
    print(message)
    packet = json.loads(message)

    if packet.get("packet",False):
        match packet["packet"]:
            case "tick":
                send(json.dumps(packet), room=request.sid)
            case "getalgorithmvideo":
                randid = random.choice(["nathan","abcdefg"])
                video = json.loads(open("uservideos/"+randid+"/data.json","r").read())
                send('{"packet":"video", "video":"'+randid+'","views":"'+str(video["views"])+'", "name" : "'+video["name"]+'", "publisher" :"'+video["publisher"]+'", "id" : "'+randid+'"}', room=request.sid)
            case "getdailytrendingvideo":
                pass
            case "updateviewcount":
                video = json.loads(open("uservideos/"+packet["id"]+"/data.json","r").read())
                video["views"] += 1
                with open("uservideos/"+packet["id"]+"/data.json","w") as videowrite:
                    videowrite.write(json.dumps(video))
            case "name":
                try:
                    with open("emails/"+session["email"]+"/data","r") as datafile:
                        datasplit = datafile.read().split("\n")
                        if session["password"] == datasplit[1]:
                            packet2 = {
                            "packet":"name",
                            "name": datasplit[0]
                            }
                            send(str(packet2).replace("'",'"'),room=request.sid)
                        else:
                            session.clear()
                except KeyError:
                    return
            case "namecheck":
                packet2 = {
                    "packet":"namecheck",
                    "value":str(packet["name"] in os.listdir("accounts"))
                }
                send(str(packet2).replace("'",'"'),room=request.sid)
                return
@app.route("/")
def main():
    with open("mainpage.html","r") as index:
        return index.read()

@app.route("/images/<path:filename>")
def images(filename):
    try:
        return send_from_directory("images", filename, as_attachment=True)
    except FileNotFoundError:
        abort(404)

@app.route("/video/<id>")
def video(id):
    try:
        return send_file("uservideos/"+id+"/video.mp4", mimetype="video/mp4", as_attachment=False)
    except FileNotFoundError:
        abort(404)

@app.route("/videothumbnail/<id>")
def videothumbnail(id):
    try:
        return send_file("uservideos/"+id+"/thumbnail.png", mimetype="image/png", as_attachment=False)
    except FileNotFoundError:
        abort(404)




# post requests
@app.route('/register', methods=['POST'])
def register():
    if not request.form.get("email",False):
        return redirect("/#regerror")
    if not checkemail(request.form["email"]):
        return redirect("/#regerror")
    if request.form["email"] in os.listdir("emails"):
        return redirect("/#regerror")
    else:
        code = ""
        for i in range(10):
            code+=str((round(random.random()*9)))
        os.mkdir("emails/"+request.form["email"])
        open("emails/"+request.form["email"]+"/code","w").write(code)
        check = 0
        while request.form["email"].split("@")[0]+str(check) in os.listdir("accounts"):
            check += 1
        name = request.form["email"].split("@")[0]+str(check)
        open("emails/"+request.form["email"]+"/data","w").write(name+"\n"+request.form["password"])
        # make account directory
        makeaccount(name)


        email = open("email.txt","r").read().replace("^code^",code)
        send_email("Bark-IT! register code",email,request.form["email"])
        session["email"] = request.form["email"]
        session["password"] = request.form["password"]
        return redirect("/#code")

@app.route('/login', methods=['POST'])
def login():
    with open("emails/"+request.form["email"]+"/data","r") as datafile:
        if request.form["email"] in os.listdir("emails"):
            
            data = datafile.read().split("\n")
            
            if request.form["password"] == data[1]:
                session["email"] = request.form["email"]
                session["password"] = request.form["password"]
                return redirect("/")
            else:
                return redirect("/#logerror")
        else:
            return redirect("/#logerror")

@app.route('/code', methods=['POST'])
def code():
    try:
        with open("emails/"+request.form["email"]+"/code","r") as codefile:
            if request.form["code"] == codefile.read():
                os.remove("emails/"+request.form["email"]+"/code")
                return redirect("/#setup")
    except:
        pass
    return redirect("/#codeerror")

@app.route('/setup', methods=['POST'])
def setup():
    if not session.get("email",False):
        return redirect("/#logerror")

    if not request.form.get("username",False):
        return redirect("/#logerror")

    if request.form["username"] in os.listdir("accounts"):
        return redirect("/#nameerror")
    with open("emails/"+session["email"]+"/data","r") as file:
        filesplit = file.read().split("\n")
        open("emails/"+session["email"]+"/data","w").write(request.form["username"]+"\n"+filesplit[1])
        transferaccount(filesplit[0],request.form["username"])
    return redirect("/")

@app.route('/logout')
def logout():
    session.clear()
    return redirect("/")

if __name__ == '__main__':
    socketio.run(app, debug=True)