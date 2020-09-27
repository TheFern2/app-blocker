from flask import Flask, request

app = Flask(__name__)

users = {}
users["Cristy"] = 0
users["Tristan"] = 0


@app.route('/permission/<string:user>', methods=['GET'])
def get_user_permission(user):
    return str(users[user])


@app.route('/permission/<string:user>/<int:permission>', methods=['POST'])
def set_user_permission(user, permission):
    if permission > 2:
        return "Invalid permission, 0 or 1"
    if request.method == 'POST':
        users[user] = permission
    return f"User {user} Permission Set to {permission}"


if __name__ == '__main__':
    app.run(debug=True, host='192.168.0.42', port=3010)
