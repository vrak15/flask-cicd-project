
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
                    url: 'https://github.com/vrak15/flask-cicd-project.git'
            }
        }

        
stage('Build') {
    steps {
        sh '''
            set -e

            echo "Checking application files"

            test -f app.py
            test -f test_app.py
            test -f requirements.txt

            echo "Creating Python virtual environment"

            rm -rf venv

            python3 -m venv venv

            echo "Upgrading pip"

            venv/bin/python -m pip install --upgrade pip

            echo "Installing Python dependencies"

            venv/bin/pip install -r requirements.txt

            echo "Verifying pytest installation"

            venv/bin/pytest --version

            echo "Compiling application"

            venv/bin/python -m compileall -q app.py

            echo "Build completed successfully"
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
                        -p 80:5001 \
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
                                -p 80:5001 \
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
