# PID=`ps -ef | grep "app.py" | grep -v "grep" | grep -v "kill" | awk '{print $2}'`
# kill -9 $PID
uwsgi --stop ./uwsgi.pid