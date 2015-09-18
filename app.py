from flask import Flask, render_template, session, request
from flask.ext.socketio import SocketIO, emit, join_room, leave_room, \
    close_room, disconnect

import json
import uuid

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
thread = None

@app.route('/')
def index():
    name = session.get("name",None)
    if not name:
        session["name"] = uuid.uuid4()
    print session["name"]
    return render_template('index.html',uuid=session["name"])

@socketio.on('connect', namespace='/quill')
def conn_message():
    pass
    
@socketio.on('on-changed', namespace='/quill')
def conn_message(message):
    changing = message["data"]["ops"]
    op=None
    value=None
    st=0
    end=0
    attr={}
    changes = []
    length = 0
    for i in changing:
        retain = i.get("retain",0)
        insert = i.get("insert",None)
        delete = i.get("delete",None)
        attr = i.get("attributes",None)
        if not insert and not delete and not attr:
            st = retain
        if not insert and not delete and attr:
            retain += st
            chag = {"op":"format","value":attr,"st":st,"end":retain}
            changes.append(chag)
        if insert:
            op="insert"
            value=insert
            length = len(value)
            chag = {"op":"insert","value":value,"st":st,"attr":attr}
            changes.append(chag)
            continue
        if delete:
            st += length
            delete += st
            chag = {"op":"delete","value":delete,"st":st}
            changes.append(chag)    
    emit("rev-changed",{"data":changes,"uuid":session["name"]},broadcast=True)
    
if __name__ == '__main__':
    socketio.run(app,"127.0.0.1",8080)
