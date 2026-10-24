pipeline {
    agent any
    options { timestamps() }
    stages {
        stage('Checkout') { steps { checkout scm } }
        stage('Install dependencies and test') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pytest -q
                '''
            }
        }
        stage('Build Docker image') {
            steps { sh 'docker build -t modelvault:latest .' }
        }
    }
    post {
        success { echo 'Tests passed and Docker image built.' }
        failure { echo 'Pipeline failed; inspect stage logs.' }
        always { echo 'ModelVault CI pipeline finished.' }
    }
}
