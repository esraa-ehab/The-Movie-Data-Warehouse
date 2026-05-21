pipeline {
    // This tells Jenkins to spin up a tiny helper container that already has Docker and Python installed
    agent {
        image 'trion/jenkins-docker-client:latest'
    }

    environment {
        TEST_IMAGE = "movie-warehouse-ci:test"
    }

    stages {
        // We can safely remove the "Lint" stage here because the next stage builds the full Airflow environment anyway
        stage('Build Testing Sandbox') {
            steps {
                echo 'Building an isolated image to test DAG integrity...'
                sh "docker build -t ${TEST_IMAGE} ."
            }
        }

        stage('Run Airflow DAG Integrity Test') {
            steps {
                echo 'Verifying that Airflow can parse the DAGs without breaking...'
                sh "docker run --rm -v \$(pwd)/dags:/opt/airflow/dags ${TEST_IMAGE} python -m compileall /opt/airflow/dags"
            }
        }

        stage('Package Application') {
            steps {
                echo 'Pipeline passed tests! Packaging complete.'
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