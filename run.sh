nohup daphne web.asgi:channel_layer -b 0.0.0.0 -p 8000 &
nohup python3 manage.py runworker --threads 4 &
echo