# Simple Java Fix Script
# Run this as Administrator

Write-Host "Simple Java Fix" -ForegroundColor Green
Write-Host "================" -ForegroundColor Green

# Step 1: Find Java installation
Write-Host "Step 1: Finding Java installation..." -ForegroundColor Yellow

$javaPath = $null

# Check common Java paths
$possiblePaths = @(
    "C:\Program Files\Java\jdk-14.0.2",
    "C:\Program Files\Java\jdk-14.0.1", 
    "C:\Program Files\Java\jdk-14",
    "C:\Program Files\Java\jdk-11.0.2",
    "C:\Program Files\Java\jdk-11",
    "C:\Program Files\Java\jdk-17",
    "C:\Program Files\Java\jdk-16",
    "C:\Program Files\Java\jdk-15"
)

foreach ($path in $possiblePaths) {
    if (Test-Path "$path\bin\java.exe") {
        $javaPath = $path
        Write-Host "Found Java at: $javaPath" -ForegroundColor Green
        break
    }
}

if (-not $javaPath) {
    Write-Host "Java not found in common locations!" -ForegroundColor Red
    Write-Host "Please check if Java is installed at:" -ForegroundColor Yellow
    foreach ($path in $possiblePaths) {
        Write-Host "  - $path" -ForegroundColor Gray
    }
    exit 1
}

# Step 2: Set JAVA_HOME
Write-Host ""
Write-Host "Step 2: Setting JAVA_HOME..." -ForegroundColor Yellow
[Environment]::SetEnvironmentVariable("JAVA_HOME", $javaPath, "Machine")
Write-Host "JAVA_HOME set to: $javaPath" -ForegroundColor Green

# Step 3: Add to PATH
Write-Host ""
Write-Host "Step 3: Adding Java to PATH..." -ForegroundColor Yellow
$currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
$javaBinPath = "$javaPath\bin"

if ($currentPath -notlike "*$javaBinPath*") {
    $newPath = "$currentPath;$javaBinPath"
    [Environment]::SetEnvironmentVariable("Path", $newPath, "Machine")
    Write-Host "Added to PATH: $javaBinPath" -ForegroundColor Green
} else {
    Write-Host "Java already in PATH" -ForegroundColor Blue
}

# Step 4: Update current session
Write-Host ""
Write-Host "Step 4: Updating current session..." -ForegroundColor Yellow
$env:JAVA_HOME = $javaPath
$env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine")

# Step 5: Test Java
Write-Host ""
Write-Host "Step 5: Testing Java..." -ForegroundColor Yellow

try {
    $javaVersion = & "$javaPath\bin\java.exe" -version 2>&1
    Write-Host "Java working!" -ForegroundColor Green
    Write-Host "Version: $($javaVersion[0])" -ForegroundColor White
} catch {
    Write-Host "Java test failed: $_" -ForegroundColor Red
}

try {
    $javacVersion = & "$javaPath\bin\javac.exe" -version 2>&1
    Write-Host "Javac working!" -ForegroundColor Green
    Write-Host "Version: $javacVersion" -ForegroundColor White
} catch {
    Write-Host "Javac test failed: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "Java fix completed!" -ForegroundColor Green
Write-Host "Please restart your terminal/PowerShell for changes to take effect." -ForegroundColor Yellow

# Show summary
Write-Host ""
Write-Host "Summary:" -ForegroundColor Cyan
Write-Host "JAVA_HOME: $env:JAVA_HOME" -ForegroundColor White
Write-Host "Java bin: $javaBinPath" -ForegroundColor White
