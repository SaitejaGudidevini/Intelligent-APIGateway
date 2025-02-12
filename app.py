from flask import Flask, request
import yaml
import requests

app = Flask(__name__)

# Load config
with open('config.yml') as f:
    config = yaml.safe_load(f)

@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def gateway(path):
    """Main gateway routing logic"""
    # TODO: Implement routing, rate limiting, auth etc.
    return {'message': 'Gateway running'}

if __name__ == '__main__':
    app.run(
        host=config['gateway']['host'],
        port=config['gateway']['port']
    )
