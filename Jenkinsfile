pipeline {
    agent {
        kubernetes {
            label 'ez-joy-friends'
            idleMinutes 5
            yamlFile 'build-pod.yaml'
            defaultContainer 'ez-docker-helm-build'
        }
    }

    environment {
        GITHUB_CREDS = 'ido-games-reviews-github-cred'
        DOCKER_IMAGE = 'idof228/games-reviews-app'
        MONGODB_URI = 'mongodb://mongo:27017/games_reviews_db'
        GITHUB_URL = 'https://api.github.com'
        OWNER = 'IdoFoyershtein'
        REPO = 'Games-Reviews'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout([$class: 'GitSCM', branches: [[name: '*/main']], 
                          userRemoteConfigs: [[url: "https://github.com/${OWNER}/${REPO}.git"]]])
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    dockerImage = docker.build("${DOCKER_IMAGE}:latest", "--no-cache .")
                }
            }
        }
        
        stage('Run Unit Tests') {
            steps {
                script {
                    sh 'docker-compose -f docker-compose.yaml up -d'
                    sh 'docker-compose -f docker-compose.yaml run test pytest'
                    sh 'docker-compose -f docker-compose.yaml down'
                }
            }
        }
        
        stage('Push Docker image') {
            when {
                branch 'main'
            }
            steps {
                script {
                    docker.withRegistry('https://registry.hub.docker.com', 'ido-dockerhub-games-reviews-cred') {
                        dockerImage.push("${env.BUILD_NUMBER}")
                        dockerImage.push("latest")
                    }
                }
            }
        }

        stage('Create Pull Request') {
            when {
                not {
                    branch 'main'
                }
            }
            steps {
                script {
                    withCredentials([string(credentialsId: 'ido-games-reviews-github-secret-api', variable: 'GITHUB_API_TOKEN')]) {
                        def response = sh(script: """
                            curl -s -o response.json -w "%{http_code}" -X POST \
                            -H "Authorization: token ${GITHUB_API_TOKEN}" \
                            -d '{ "title": "PR from ${env.BRANCH_NAME} into main", "head": "${env.BRANCH_NAME}", "base": "main" }' \
                            ${GITHUB_URL}/repos/${OWNER}/${REPO}/pulls
                        """, returnStdout: true).trim()
                        if (response.startsWith("2")) {
                            echo "Pull request created successfully."
                        } else {
                            echo "Failed to create pull request. Response Code: ${response}"
                            def jsonResponse = readJSON file: 'response.json'
                            echo "Error message: ${jsonResponse.message}"
                            error "Pull request creation failed."
                        }
                    }
                }
            }
        }
    }
    
    post {
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
        }
        always {
            cleanWs()
        }
    }
}
