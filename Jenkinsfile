pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        IMAGE_NAME = 'dwiti3184/cloudforge-api'
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
                script {
                    env.IMAGE_TAG = "${env.IMAGE_NAME}:${env.GIT_COMMIT}"
                }

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

        stage('Update GitOps Manifest') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'github-write-creds',
                    usernameVariable: 'GIT_USERNAME',
                    passwordVariable: 'GIT_TOKEN'
                )]) {
                    sh '''
                        set -eu

                        awk -v image="$IMAGE_TAG" '
			/- name: api/ {
                           in_api = 1
                           print
                           next
			}
			in_api && /image:/ {
				sub(/image:.*/, "image: " image)
				in_api = 0
			}
			{ print }
			' kubernetes/deployment.yaml > kubernetes/deployment.yaml.tmp

			mv kubernetes/deployment.yaml.tmp kubernetes/deployment.yaml                       

                        git config user.name "CloudForge Jenkins"
                        git config user.email "jenkins@cloudforge.local"

                        git add kubernetes/deployment.yaml

                        if git diff --cached --quiet; then
                            echo "No manifest changes to commit."
                        else
                            git commit -m "Update CloudForge image to ${GIT_COMMIT}"

                            ASKPASS=$(mktemp)
                            trap 'rm -f "$ASKPASS"' EXIT

                            cat > "$ASKPASS" <<'EOF'
#!/bin/sh
case "$1" in
    *Username*) echo "$GIT_USERNAME" ;;
    *Password*) echo "$GIT_TOKEN" ;;
    *) echo "$GIT_TOKEN" ;;
esac
EOF

                            chmod 700 "$ASKPASS"
                            export GIT_ASKPASS="$ASKPASS"
                            export GIT_TERMINAL_PROMPT=0

                            git push origin HEAD:main
                        fi
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
