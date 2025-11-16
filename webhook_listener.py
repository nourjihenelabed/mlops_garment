from flask import Flask, request, jsonify
import subprocess
import os
import logging
from threading import Thread
import joblib

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    """Handle GitHub webhook posts"""
    try:
        # Verify it's a push event from GitHub
        event = request.headers.get('X-GitHub-Event')
        if event == 'ping':
            logger.info("Received ping event from GitHub")
            return jsonify({"status": "success", "message": "Webhook is working!"}), 200
            
        elif event == 'push':
            logger.info("Received push event from GitHub")
            
            # Get the payload
            payload = request.get_json()
            repo_name = payload['repository']['full_name']
            commit_message = payload['head_commit']['message'] if payload.get('head_commit') else 'No commit message'
            
            logger.info(f"Push to {repo_name}: {commit_message}")
            
            # Run your ML pipeline in a separate thread to avoid timeout
            thread = Thread(target=run_ml_pipeline)
            thread.start()
            
            return jsonify({
                "status": "success", 
                "message": "ML pipeline triggered successfully",
                "repository": repo_name,
                "commit": commit_message
            }), 200
        
        else:
            logger.info(f"Ignored event: {event}")
            return jsonify({"status": "ignored", "message": f"Event {event} not handled"}), 200
            
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

def run_ml_pipeline():
    """Run the ML pipeline when webhook is triggered"""
    try:
        logger.info("Starting ML pipeline execution...")
        
        # Change to your project directory
        project_dir = '/home/joujou/nourjihen-elabed-4DS1-ml_project'
        os.chdir(project_dir)
        
        # Run git pull to get latest code
        logger.info("Pulling latest code...")
        pull_result = subprocess.run(['git', 'pull'], capture_output=True, text=True)
        if pull_result.returncode != 0:
            logger.error(f"Git pull failed: {pull_result.stderr}")
        
        # Run your ML pipeline
        logger.info("Running ML pipeline...")
        pipeline_result = subprocess.run([
            'python', 'main.py', '--all', 
            '--data_path', 'dataProductivity-Prediction-of-Garment-Employeese.csv'
        ], capture_output=True, text=True)
        
        if pipeline_result.returncode == 0:
            logger.info("ML pipeline completed successfully!")
            logger.info(f"Output: {pipeline_result.stdout}")
        else:
            logger.error(f"ML pipeline failed: {pipeline_result.stderr}")
            
    except Exception as e:
        logger.error(f"Pipeline execution error: {str(e)}")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "ML Pipeline Webhook"})

if __name__ == '__main__':
    logger.info("Starting webhook listener on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
