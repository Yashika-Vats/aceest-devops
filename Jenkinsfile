pipeline {
    agent any
    stages {
        stage('Clone') {
            steps {
                git 'https://github.com/YOUR_USERNAME/aceest-devops.git'
            }
        }
        stage('Install') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }
        stage('Test') {
            steps {
                sh 'pytest'
            }
        }
        stage('Build Docker') {
            steps {
                sh 'docker build -t aceest-app .'
            }
        }
    }
}