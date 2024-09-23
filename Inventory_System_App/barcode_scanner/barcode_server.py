from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/scan', methods=['POST'])
def scan_barcode():
    barcode_data = request.form.get('barcode')
    if barcode_data:
        print(f"Scanned barcode: {barcode_data}")
        return barcode_data, 200
    else:
        return "No barcode data", 400

@app.route('/scan_from_camera', methods=['POST'])
def scan_from_camera():
    # Handle scanning from camera (to be implemented)
    # This route will process barcode scanning via camera
    return "Barcode scanning from camera endpoint", 200

@app.route('/test')
def test_page():
    return render_template('test.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
