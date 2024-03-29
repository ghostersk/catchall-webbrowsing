from flask import Flask, request, Response, render_template, redirect, url_for
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import threading


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

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
HTTP_METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']

@app.route('/', defaults={'path': ''}, methods=HTTP_METHODS)
@app.route('/<path:path>', methods=HTTP_METHODS)
def catch_all(path):
    if request.path == '/favicon.ico':
        return Response(status=200)
    # Log the request
    with Session() as session:
        records = {
            'method': request.method,
            'url': request.url,
            'root_domain': request.host.split(':')[0]
        }
        log_entry = RequestLog(**records)
        session.add(log_entry)
        session.commit()
        

    return render_template('index.html', records=records)


@app.route('/test/showquery')
def show_query():
    # Retrieve all records from the request_logs table
    with Session() as session:
        logs = session.query(RequestLog).all()

    return render_template('records.html', records=logs)

@app.route('/test/delete_records', methods=['POST'])
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
