from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_email', methods=['POST'])
def generate_email():
    # Here is where we'll later hook Notion + ChatGPT + Gmail
    print("Button clicked! Generating email...")
    return jsonify({'message': 'Email generation started!'}), 200

if __name__ == '__main__':
    app.run(debug=True)
