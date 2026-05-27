from flask import Flask, render_template, jsonify

app = Flask(__name__)

# This is your Python data structure representing the departments
DEPARTMENTS = {
    "science": {
        "name": "Science Department",
        "icon": "🔬",
        "books_count": 14,
        "description": "Access Physics, Chemistry, Biology texts, and custom engineering blueprints."
    },
    "art": {
        "name": "Art Department",
        "icon": "🎨",
        "books_count": 12,
        "description": "Access Literature, History, Government readings, and creative writing archives."
    },
    "commercial": {
        "name": "Commercial Department",
        "icon": "📊",
        "books_count": 15,
        "description": "Access Financial Accounting, Commerce, Economics manuals, and business models."
    }
}

@app.route('/')
def home():
    # Python sends this data dynamically straight into your HTML layout
    return render_template('index.html', departments=DEPARTMENTS)

@app.route('/api/quiz/<dept_id>')
def get_quiz(dept_id):
    return jsonify({"status": "success", "message": f"Quiz room for {dept_id} coming soon!"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
