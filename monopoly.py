from monopoly import create_app, socketio

app = create_app(debug=True)

if __name__ == '__main__':
    socketio.run(app)
