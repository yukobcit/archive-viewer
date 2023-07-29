from flask import Flask
from main import

app = Flask(__name__)

# Set endpoints
@app.route('/')
def hello():
    return 'Hello, World!'

@app.route('/api/data')
def get_data():
    # ここでデータを取得・処理して返す
    data = {'key': 'value'}
    return data

@app.route('/archives/<username>')
def search_user(username):

    return f'Searching for Twitch user: {username}'

if __name__ == '__main__':
    app.run(debug=True)