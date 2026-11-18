pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        IMAGE_NAME = 'dwiti3184/cloudforge-api'
        IMAGE_TAG = "${IMAGE_NAME}:${GIT_COMMIT}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Unit Tests') {
            steps {
                sh '''
                    docker run --rm \
                      -v "$WORKSPACE:/workspace" \
                      -w /workspace \
                      python:3.12-slim \
                      python -m unittest discover -s tests -v
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build \
                      -f docker/Dockerfile.api \
                      -t "$IMAGE_TAG" .
                '''
            }
        }

        stage('Trivy Security Scan') {
            steps {
                sh '''
                    trivy image \
                      --severity HIGH,CRITICAL \
                      --ignore-unfixed \
                      --exit-code 1 \
                      "$IMAGE_TAG"
                '''
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_TOKEN'
                )]) {
                    sh '''
                        echo "$DOCKER_TOKEN" | docker login \
                          --username "$DOCKER_USER" \
                          --password-stdin

                        docker push "$IMAGE_TAG"
                        docker tag "$IMAGE_TAG" "$IMAGE_NAME:latest"
                        docker push "$IMAGE_NAME:latest"

                        docker logout
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'CloudForge pipeline completed successfully!'
        }
        failure {
            echo 'CloudForge pipeline failed. Check the stage logs.'
        }
    }
}
