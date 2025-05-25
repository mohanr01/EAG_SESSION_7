from flask import Flask, request, jsonify
from flask_cors import CORS
import logger
import mcp_server
import agent

app = Flask(__name__)
CORS(app)


@app.route('/index', methods=['POST'])
def index_content():
    try:
        data = request.json
        logger.loggingInfo(f"request data: {data}")
        url = data.get('url')
        logger.loggingInfo(f"url {url}")
        mcp_server.process_url(url=url)
        #text = f"{data['title']} {data['content']}"
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/search', methods=['POST'])
def search():
    try:
        query = request.json
        query = query.get('query')
        logger.loggingInfo(f"incoming query:::{query}")
        result = agent.search(query)
        logger.loggingInfo(result)
        result = result.replace("FINAL_ANSWER:","").replace("[","").replace("]","").strip().split("|")
        return jsonify({'success': True, 'results': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(port=5000) 