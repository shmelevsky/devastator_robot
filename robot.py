from flask import Flask, render_template, redirect, jsonify, request
import subprocess
import  random
app = Flask(__name__)




def ping_server():
    cmd = ['/usr/bin/fping  -q -B  1 -C 1 -p 500 -r 5 -t 500  82.193.109.230']
    out = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    ping = out.communicate()[1:][0].decode('UTF-8').split(':')[1]
    return ping


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/forward')
def forward():
    print('FORWARD')
    return redirect('/')


@app.route('/left')
def left():
    print('LEFT')
    return redirect('/')


@app.route('/right')
def right():
    print('RIGHT')
    return redirect('/')


@app.route('/backward')
def backward():
    print('BACKWARD')
    return redirect('/')


@app.route('/stop')
def stop():
    print('STOP')
    return redirect('/')


@app.route('/get_ping', methods=['POST'])
def get_ping():
    if request.method == 'POST':
        return jsonify(ping_server())


@app.route('/get_distance', methods=['POST'])
def get_distance():
    if request.method == 'POST':
        return jsonify(random.randint(10, 2000))


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8080)


