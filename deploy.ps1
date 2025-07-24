# PowerShell script for deploying ImmoAssist to Cloud Run

# Configuration
$PROJECT_ID = "gothic-agility-464209-f4"
$IMAGE_NAME = "immoassist"
$REGION = "europe-central2"
$SERVICE_NAME = "immoassist"

# Check Docker
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
  Write-Host "Error: Docker not found. Please install Docker Desktop" -ForegroundColor Red
  exit 1
}

# Check gcloud
if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
  Write-Host "Error: gcloud CLI not found. Please install Google Cloud SDK" -ForegroundColor Red
  exit 1
}

Write-Host "Starting ImmoAssist deployment to Cloud Run..." -ForegroundColor Green
Write-Host "   Project: $PROJECT_ID" -ForegroundColor Cyan
Write-Host "   Region: $REGION" -ForegroundColor Cyan
Write-Host "   Service: $SERVICE_NAME" -ForegroundColor Cyan
Write-Host ""

# Step 1: Build Docker image
Write-Host "Building Docker image..." -ForegroundColor Yellow
$buildResult = docker build -t "gcr.io/$PROJECT_ID/$IMAGE_NAME`:latest" .

if ($LASTEXITCODE -ne 0) {
  Write-Host "Error building Docker image" -ForegroundColor Red
  exit 1
}

Write-Host "Docker image built successfully" -ForegroundColor Green
Write-Host ""

# Step 2: Push image to Google Container Registry
Write-Host "Pushing image to Google Container Registry..." -ForegroundColor Yellow
$pushResult = docker push "gcr.io/$PROJECT_ID/$IMAGE_NAME`:latest"

if ($LASTEXITCODE -ne 0) {
  Write-Host "Error pushing image" -ForegroundColor Red
  exit 1
}

Write-Host "Image pushed to GCR successfully" -ForegroundColor Green
Write-Host ""

# Step 3: Deploy to Cloud Run
Write-Host "Deploying to Cloud Run..." -ForegroundColor Yellow
$deployResult = gcloud run deploy $SERVICE_NAME `
  --image "gcr.io/$PROJECT_ID/$IMAGE_NAME`:latest" `
  --platform managed `
  --region $REGION `
  --allow-unauthenticated `
  --port 8000 `
  --memory 2Gi `
  --cpu 1 `
  --max-instances 10 `
  --project $PROJECT_ID

if ($LASTEXITCODE -ne 0) {
  Write-Host "Error deploying to Cloud Run" -ForegroundColor Red
  exit 1
}

Write-Host ""
Write-Host "Deployment completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Your application is available at:" -ForegroundColor Cyan

# Get service URL
$SERVICE_URL = gcloud run services describe $SERVICE_NAME --region=$REGION --project=$PROJECT_ID --format="value(status.url)"

Write-Host "   Main URL: $SERVICE_URL" -ForegroundColor White
Write-Host "   Chat interface: $SERVICE_URL/chat/" -ForegroundColor White
Write-Host ""
Write-Host "Important: Chat will be available at $SERVICE_URL/chat/" -ForegroundColor Yellow
Write-Host ""
Write-Host "Additional endpoints:" -ForegroundColor Cyan
Write-Host "   - ADK interface: $SERVICE_URL/" -ForegroundColor White
Write-Host "   - TTS API: $SERVICE_URL/tts" -ForegroundColor White 