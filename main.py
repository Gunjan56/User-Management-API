from apis.message import socketio
from app import create_app

if __name__ == '__main__':
    app = create_app()
    socketio.run(app,debug=False, host='localhost', port=5000)
