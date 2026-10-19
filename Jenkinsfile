pipeline {
  agent any
  options {
    disableConcurrentBuilds()
    timeout(time: 30, unit: 'MINUTES')
    buildDiscarder(logRotator(numToKeepStr: '10'))
  }
  environment {
    IMAGE_NAME = 'sanskrit-saathi'
    CI = 'true'
  }
  triggers { pollSCM('H/2 * * * *') }
  stages {
    stage('Checkout') {
      steps {
        checkout scm
        bat 'git log -1 --format="%%H %%s"'
      }
    }
    stage('Build') {
      steps {
        bat 'node --version'
        bat 'python --version'
        dir('frontend') {
          bat 'call npm ci'
          bat 'call npm run build'
        }
        bat 'python -m venv .venv'
        bat '.venv\\Scripts\\python.exe -m pip install -r backend\\requirements.txt'
        bat '.venv\\Scripts\\python.exe -m pip install pytest'
      }
    }
    stage('Test/Validate') {
      steps {
        dir('backend') {
          bat '..\\.venv\\Scripts\\python.exe -m pytest'
        }
      }
    }
    stage('Docker Build') {
      steps {
        script {
          env.GIT_SHA = bat(returnStdout: true, script: '@git rev-parse HEAD').trim()
        }
        bat 'docker info > nul'
        bat 'docker build --label org.opencontainers.image.revision=%GIT_SHA% -t %IMAGE_NAME%:%BUILD_NUMBER% .'
        bat 'docker image inspect %IMAGE_NAME%:%BUILD_NUMBER% --format "Image created: {{.Id}}"'
      }
    }
    stage('Result') {
      steps {
        echo "Build ${env.BUILD_NUMBER} passed. Image: ${env.IMAGE_NAME}:${env.BUILD_NUMBER}"
      }
    }
  }
  post {
    success { echo 'CI pipeline completed successfully.' }
    failure { echo 'CI pipeline failed. Check the failed stage and Console Output.' }
  }
}