# catchall-webbrowsing for Adguard Home
Flask app for catching web requests and recording them
I have created this app to redirect all blocked DNS queries from Adguard Home, to the ip of docker container.
The app will record what website was used, and it will also return information the website was blocked.
- default Adguard Home behaviour is to return non existent response, if you do not pay attention, you may miss that it was your DNS filter.
It will listen on port 80 and 443, 443 port need certificate, i have added script to create certificate with CA signing.
If you need, you can add the CA certificate to trusted certificates for easier use ( will work only on the IP, unless you make it for all hostnames)

The application is started by using `startup.sh`
```
#!/bin/bash
pip install -r requirements.txt

export FLASK_RUN_EXTRA_FILES="startup.sh"
export FLASK_DEBUG=True
export FLASK_RUN_HOST="0.0.0.0"
export FLASK_RUN_PORT=80

flask run & python app.py
```
This will first run the app on port 80 and all interfaces and last command it will run on the port 443 as per the `app.py` code

This app is using [Interactive Bootstrap 5 DataTables](https://www.datatables.net/) for easier data lookup.
![Screenshot_20240518_203638](https://github.com/ghostersk/catchall-webbrowsing/assets/68815071/f8e7dd56-fd9b-4462-8a7e-e81e8e4e7fe6)

## List all blocked attempts
![Screenshot_20240518_190418](https://github.com/ghostersk/catchall-webbrowsing/assets/68815071/ad23243f-aaa4-4593-b8e5-0f692d204fc8)

You can deploy it with docker-compose, as per the docker-compose.yml example
I am using static IP address of the catchall container to send all blocked queries there from [Adguard Home in DNS Settings](https://adguard.com/kb/adguard-for-ios/solving-problems/low-level-settings/#:~:text=Blocking%20mode%E2%80%8B,REFUSED%20%E2%80%94%20respond%20with%20REFUSED%20code):
![Screenshot_20240329_125519](https://github.com/ghostersk/catchall-webbrowsing/assets/68815071/8a291a09-9f7c-4bdb-8b23-374c51e320d7)

On end to make sure you do not have to confirm invalid SSL certificate, I have added custom domain (in `app.py` update the `webblocker_host` , what can be set to anything and then you just need to use for example Nginx Proxy to point the url with valid SSL or with HTTP only to the ip where this Catchall is running.
![image](https://github.com/ghostersk/catchall-webbrowsing/assets/68815071/b06e61c1-5fec-401e-b7ce-20cabee2017b)

