from flask import Flask, request, Response, render_template, redirect, url_for
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import threading

# Set this URL to URL where the app will be redirected after it receive traffic.
# This URL should have valid certificate ( self signed or Letsencrypt )
# otherwise you will be always warned about bad certificate.
# I used Nginx Proxy Manager to give me this, and added DNS record to Adguard
# As I have this on internal network
webblocker_host="http://webblocker.vm.com"

app = Flask(__name__)

# SQLAlchemy setup
db_uri = 'sqlite:///request_logs.db'
engine = create_engine(db_uri)
Base = declarative_base()

class RequestLog(Base):
    __tablename__ = 'request_logs'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    method = Column(String)
    url = Column(String)
    root_domain =  Column(String)
    post_data = Column(String)
    headers = Column(String)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

HTTP_METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']

@app.route('/webblocker/<int:id>', methods=['GET'])
def webblocker(id):
    if request.path == '/favicon.ico':
        return Response(status=200)
    try:
        with Session() as session:
            record = session.query(RequestLog).filter_by(id=id).one()
    except NoResultFound as error:
        return render_template('index.html', error=er)
    return render_template('index.html', records=record)

@app.route('/', defaults={'path': ''}, methods=HTTP_METHODS)
@app.route('/<path:path>', methods=HTTP_METHODS)
def catch_all(path):
    if request.path == '/favicon.ico':
        return Response(status=200)

    # Log the request
    with Session() as session_db:
        if request.method == 'POST': 
            post_data = str(request.form)
        elif request.method == 'GET':
            post_data = str(request.args)
        else:
            post_data = ""
        records = {
            'method': request.method,
            'url': request.url,
            'root_domain': request.host.split(':')[0],
            'post_data': post_data,
            'headers': str(request.headers)
        }

        log_entry = RequestLog(**records)
        session_db.add(log_entry)
        session_db.commit()
        log_id = log_entry.id
    # Redirect to the webblocker URL without query parameters
    webblocker_path = url_for('webblocker',id=log_id)
    webblocker_url = f"{webblocker_host}{webblocker_path}"
    return redirect(webblocker_url, code=302)


@app.route('/webblocker/showquery')
def show_query():
    # Retrieve all records from the request_logs table
    with Session() as session:
        logs = session.query(RequestLog).all()

    return render_template('records.html', records=logs)

@app.route('/webblocker/delete_records', methods=['POST'])
def delete_records():
    # Delete all records from the request_logs table
    with Session() as session:
        session.query(RequestLog).delete()
        session.commit()

    # Redirect back to the page displaying the records
    return redirect(url_for('show_query'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=443, ssl_context=('ssl/cert.pem', 'ssl/key.pem'))
   # app.run(debug=True,host="0.0.0.0", port=80)
