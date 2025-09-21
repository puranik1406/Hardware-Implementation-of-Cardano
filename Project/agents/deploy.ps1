# Agent A Production Deployment Script (PowerShell)

param(
    [string]$Environment = "production",
    [switch]$SkipTests = $false,
    [switch]$Force = $false
)

# Configuration
$ServiceName = "agent-a"
$DockerImage = "agent-a:latest"
$ContainerName = "agent-a-service"
$Port = "8001"
$LogDir = ".\logs"

# Functions
function Write-Info {
    param([string]$Message)
    Write-Host "🚀 [INFO] $Message" -ForegroundColor Green
}

function Write-Warn {
    param([string]$Message)
    Write-Host "⚠️  [WARN] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ [ERROR] $Message" -ForegroundColor Red
}

function Test-Prerequisites {
    Write-Info "Checking prerequisites..."
    
    # Check if Docker is installed
    try {
        $null = docker --version
        Write-Info "Docker is installed ✅"
    }
    catch {
        Write-Error "Docker is not installed. Please install Docker Desktop first."
        exit 1
    }
    
    # Check if Docker Compose is installed
    try {
        $null = docker-compose --version
        Write-Info "Docker Compose is installed ✅"
    }
    catch {
        Write-Error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    }
    
    Write-Info "Prerequisites check passed ✅"
}

function Initialize-Directories {
    Write-Info "Setting up directories..."
    
    $directories = @("logs", "monitoring", "docker")
    
    foreach ($dir in $directories) {
        if (!(Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Info "Created directory: $dir"
        }
    }
    
    Write-Info "Directories setup completed ✅"
}

function Build-DockerImage {
    Write-Info "Building Docker image..."
    
    Set-Location docker
    try {
        docker build -t $DockerImage .
        Write-Info "Docker image built successfully ✅"
    }
    catch {
        Write-Error "Failed to build Docker image"
        Set-Location ..
        exit 1
    }
    finally {
        Set-Location ..
    }
}

function Stop-ExistingContainer {
    Write-Info "Stopping existing container..."
    
    $existingContainer = docker ps -q -f "name=$ContainerName"
    if ($existingContainer) {
        docker stop $ContainerName
        docker rm $ContainerName
        Write-Info "Existing container stopped and removed ✅"
    }
    else {
        Write-Info "No existing container found ✅"
    }
}

function Start-DockerCompose {
    Write-Info "Deploying with Docker Compose..."
    
    Set-Location docker
    try {
        docker-compose up -d
        Write-Info "Docker Compose deployment completed ✅"
    }
    catch {
        Write-Error "Failed to deploy with Docker Compose"
        Set-Location ..
        exit 1
    }
    finally {
        Set-Location ..
    }
}

function Test-HealthCheck {
    Write-Info "Performing health check..."
    
    # Wait for service to start
    Start-Sleep -Seconds 10
    
    $maxAttempts = 30
    $attempt = 1
    
    do {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:$Port/" -Method GET -TimeoutSec 5
            if ($response.StatusCode -eq 200) {
                Write-Info "Health check passed ✅"
                return $true
            }
        }
        catch {
            Write-Warn "Health check attempt $attempt/$maxAttempts failed, retrying in 2 seconds..."
            Start-Sleep -Seconds 2
            $attempt++
        }
    } while ($attempt -le $maxAttempts)
    
    Write-Error "Health check failed after $maxAttempts attempts"
    return $false
}

function Start-Monitoring {
    Write-Info "Setting up monitoring..."
    
    # Start metrics collection in background
    Start-Process python -ArgumentList "monitoring/metrics_collector.py" -WindowStyle Hidden
    
    Write-Info "Monitoring setup completed ✅"
}

function Show-DeploymentStatus {
    Write-Info "Deployment Status:"
    Write-Host "=================="
    
    # Container status
    $containerStatus = docker ps -q -f "name=$ContainerName"
    if ($containerStatus) {
        Write-Info "Container Status: Running ✅"
    }
    else {
        Write-Error "Container Status: Not Running ❌"
    }
    
    # Service health
    try {
        $null = Invoke-WebRequest -Uri "http://localhost:$Port/" -Method GET -TimeoutSec 5
        Write-Info "Service Health: Healthy ✅"
    }
    catch {
        Write-Error "Service Health: Unhealthy ❌"
    }
    
    # Port status
    $portStatus = netstat -an | Select-String ":$Port "
    if ($portStatus) {
        Write-Info "Port $Port : Listening ✅"
    }
    else {
        Write-Error "Port $Port : Not Listening ❌"
    }
    
    Write-Host ""
    Write-Info "Service URL: http://localhost:$Port"
    Write-Info "API Documentation: http://localhost:$Port/docs"
    Write-Info "Health Check: http://localhost:$Port/"
}

function Run-IntegrationTests {
    if (!$SkipTests) {
        Write-Info "Running integration tests..."
        
        try {
            python comprehensive_integration_tests.py
            Write-Info "Integration tests completed ✅"
        }
        catch {
            Write-Warn "Integration tests failed, but continuing with deployment"
        }
    }
    else {
        Write-Warn "Skipping integration tests (--SkipTests flag used)"
    }
}

# Main deployment process
function Start-Deployment {
    Write-Info "Starting Agent A deployment process..."
    Write-Host "Environment: $Environment"
    Write-Host "Force: $Force"
    Write-Host "Skip Tests: $SkipTests"
    Write-Host "=============================================="
    
    try {
        Test-Prerequisites
        Initialize-Directories
        Build-DockerImage
        Stop-ExistingContainer
        Start-DockerCompose
        
        if (Test-HealthCheck) {
            Start-Monitoring
            Show-DeploymentStatus
            Write-Info "🎉 Deployment completed successfully!"
        }
        else {
            Write-Error "❌ Deployment failed during health check"
            exit 1
        }
    }
    catch {
        Write-Error "❌ Deployment failed: $($_.Exception.Message)"
        exit 1
    }
}

# Run deployment
Start-Deployment
