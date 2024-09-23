from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_barcode', methods=['POST'])
def process_barcode():
    barcode_data = request.json.get('barcode_data')
    # Process barcode_data as needed (e.g., database storage, further computation)
    print('Received barcode data:', barcode_data)
    return 'Barcode data received and processed successfully!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
