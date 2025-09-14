from flask import Flask, request, jsonify
import numpy as np
import os
import tempfile

from test import ECGSingleFileProcessor, analyser_fichier_ecg_unique

app = Flask(__name__)

MODEL_PATH = "best_ecg_hybrid_model.h5"
processor = ECGSingleFileProcessor(MODEL_PATH)

def convert_numpy_types(obj):
    if isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(v) for v in obj]
    elif isinstance(obj, np.generic):
        return obj.item()
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj

@app.route('/predict', methods=['POST'])
def predict():
    # Case 1: Array input via JSON
    if request.is_json:
        data = request.get_json()
        array = data.get('array') if isinstance(data, dict) else None
        if array is None and isinstance(data, dict):
            array = data.get('ecg')
        if array is None:
            return jsonify({'success': False, 'error': 'No array provided in JSON.'}), 400
        try:
            np_array = np.array(array, dtype=np.float64)
            result = processor.predict_from_array(np_array)
            result = convert_numpy_types(result)
            return jsonify(result)
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    # Case 2: File upload (expects .dat and .hea files)
    if 'file' in request.files:
        file = request.files['file']
        filename = file.filename
        if not filename.endswith('.dat'):
            return jsonify({'success': False, 'error': 'Only .dat files are supported.'}), 400

        # Save .dat file to temp directory
        with tempfile.TemporaryDirectory() as tmpdir:
            dat_path = os.path.join(tmpdir, filename)
            file.save(dat_path)

            # Try to find corresponding .hea file in the request
            hea_file = request.files.get('hea')
            if hea_file:
                hea_filename = hea_file.filename
                hea_path = os.path.join(tmpdir, hea_filename)
                hea_file.save(hea_path)
            else:
                # Try to infer .hea filename
                hea_path = dat_path.replace('.dat', '.hea')
                if not os.path.exists(hea_path):
                    return jsonify({'success': False, 'error': 'No .hea file provided.'}), 400

            # Remove extension for chemin_base
            chemin_base = dat_path[:-4]
            result = analyser_fichier_ecg_unique(chemin_base, model_path=MODEL_PATH)
            # Remove numpy arrays from result for JSON serialization
            if 'signal_preprocessed' in result:
                result.pop('signal_preprocessed')
            result = convert_numpy_types(result)
            return jsonify(result)

    return jsonify({'success': False, 'error': 'No valid input provided.'}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)