#! /usr/bin/env sh

/usr/bin/supervisord -c /app/supervisord.conf
/usr/local/bin/python /usr/local/bin/uvicorn main:app --host 0.0.0.0 --port 8000