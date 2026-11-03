
pipeline {
    agent {
        label 'flask-agent'
    }

    triggers {
        githubPush()
    }

    environment {
        DOCKER_IMAGE = 'vrak45/flask-cicd-app'
    }

    stages {

        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/YOUR_GITHUB_USERNAME/flask-cicd-project.git'
            }
        }

        stage('Build') {
            steps {
                sh '''
                    python3 -m venv venv
                    venv/bin/pip install -r requirements.txt
                    python3 -m compileall -q app.py
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                    venv/bin/pytest -v
                '''
            }
        }

        stage('Docker Build') {
            steps {
                sh '''
                    docker build -t ${DOCKER_IMAGE}:${BUILD_NUMBER} .
                    docker tag ${DOCKER_IMAGE}:${BUILD_NUMBER} ${DOCKER_IMAGE}:latest
                '''
            }
        }

        stage('Docker Push') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASSWORD'
                    )
                ]) {
                    sh '''
                        echo "$DOCKER_PASSWORD" | docker login \
                            -u "$DOCKER_USER" --password-stdin

                        docker push ${DOCKER_IMAGE}:${BUILD_NUMBER}
                        docker push ${DOCKER_IMAGE}:latest

                        docker logout
                    '''
                }
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    set -eu

                    NEW_IMAGE="${DOCKER_IMAGE}:${BUILD_NUMBER}"

                    PREVIOUS_IMAGE=$(docker inspect \
                        --format='{{.Config.Image}}' flask-app 2>/dev/null || true)

                    echo "Previous image: ${PREVIOUS_IMAGE:-none}"

                    docker pull "$NEW_IMAGE"

                    docker rm -f flask-app 2>/dev/null || true

                    docker run -d \
                        --name flask-app \
                        --restart unless-stopped \
                        -p 80:5000 \
                        -e APP_VERSION="$NEW_IMAGE" \
                        "$NEW_IMAGE"

                    echo "Checking application health..."

                    HEALTHY=false

                    for i in $(seq 1 12); do
                        if curl -fsS http://localhost/health; then
                            HEALTHY=true
                            break
                        fi
                        sleep 5
                    done

                    if [ "$HEALTHY" = true ]; then
                        echo "Deployment successful!"
                    else
                        echo "Deployment failed. Starting rollback..."

                        docker rm -f flask-app 2>/dev/null || true

                        if [ -n "$PREVIOUS_IMAGE" ]; then
                            docker run -d \
                                --name flask-app \
                                --restart unless-stopped \
                                -p 80:5000 \
                                "$PREVIOUS_IMAGE"

                            echo "Rollback attempted to previous image."
                        else
                            echo "No previous image available for rollback."
                        fi

                        exit 1
                    fi
                '''
            }
        }
    }

    post {
        success {
            echo 'CI/CD Pipeline completed successfully!'
        }

        failure {
            echo 'CI/CD Pipeline failed. Check the Console Output.'
        }
    }
}
