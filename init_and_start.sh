python3 ws-server.py &
flask data-generator 100 1 &
# To serve static
FLASK_ENV=development flask run --no-debugger --no-reload