from flask import Flask, request, jsonify
from .crew import InstagramFactCheckCrew

app = Flask(__name__)

@app.route('/fact-check', methods=['POST'])
def fact_check():
    try:
        # Get post data from request
        post_data = request.json
        
        # Validate required fields
        required_fields = ['username', 'description', 'post_url']
        for field in required_fields:
            if field not in post_data:
                return jsonify({
                    "error": f"Missing required field: {field}",
                    "status": "failed"
                }), 400

        # Initialize and run the crew
        crew = InstagramFactCheckCrew()
        result = crew.run(post_data)
        
        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "failed"
        }), 500

if __name__ == '__main__':
    app.run(debug=True) 