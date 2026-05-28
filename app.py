from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/library/science')
def science_library():
    return render_template('science_library.html')

@app.route('/library/art')
def art_library():
    return render_template('art_library.html')

@app.route('/library/commercial')
def commercial_library():
    return render_template('commercial_library.html')

if __name__ == '__main__':
    app.run(debug=True)
