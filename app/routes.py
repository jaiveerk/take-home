from app import ALLOWED_EXTENTIONS, app, handler
from flask import request
from flask import jsonify
import traceback


storageHandler = handler.Handler()

@app.route('/upload', methods=['POST'])
def upload():
	try:
		# logic to handle/parse request
		if 'data' not in request.files:
			return jsonify({'success': 'false', 'reason': 'file missing from request data'})
		
		file = request.files['data']

		if file.filename.split('.')[1].lower() not in ALLOWED_EXTENTIONS:
			print(file.filename)
			return jsonify({'success': 'false', 'reason': 'invalid filename: must be a yaml ending with .yaml or .yml'})

		return storageHandler.file_to_dict(file)

	except Exception as e:
		print(traceback.format_exc()) # <-- for debugging during development
		return jsonify({'success': 'false', 'reason': str(e)})


@app.route('/get/<path:query>', methods=['GET'])
def get(query):
	try:
		# logic to handle/parse request
		if query == '':
			return jsonify({'success': 'false', 'reason': 'query required'})
		

		return storageHandler.process_query(query)

	except Exception as e:
		print(traceback.format_exc())
		return jsonify({'success': 'false', 'reason': str(e)})


if __name__ == '__main__':
	app.run(debug = True)
