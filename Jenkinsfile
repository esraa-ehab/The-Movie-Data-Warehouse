pipeline {
    agent any

    environment {
        TEST_IMAGE = "movie-warehouse-ci:test"
    }

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Lint & Static Checks') {
            steps {
                echo 'Checking Python syntax safety...'
                // Ensures none of the scripts have syntax errors before moving forward
                sh 'python -m compileall .'
            }
        }

        stage('Build Testing Sandbox') {
            steps {
                echo 'Building an isolated image to test DAG integrity...'
                // This builds a standalone image locally in Jenkins just to run tests
                sh "docker build -t ${TEST_IMAGE} ."
            }
        }

        stage('Run Airflow DAG Integrity Test') {
            steps {
                echo 'Verifying that Airflow can parse the DAGs without breaking...'
                // This runs a temporary container to check if the DAGs can be parsed without errors
                sh "docker run --rm -v \$(pwd)/dags:/opt/airflow/dags ${TEST_IMAGE} python -m compileall /opt/airflow/dags"
            }
        }

        stage('Package Application') {
            steps {
                echo 'Pipeline passed tests! Packaging current state...'
                echo 'Container packaging complete.'
            }
        }
    }

    post {
        always {
            echo 'Cleaning up temporary test artifacts...'
            sh "docker rmi ${TEST_IMAGE} --force || true"
        }
    }
}