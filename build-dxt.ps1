# WordPress MCP - DXT Package Builder (PowerShell)
# Creates a .dxt file for Anthropic Desktop Extensions

$VERSION = "1.1.1"
$OUTPUT_NAME = "wordpress-mcp-v$VERSION.dxt"
$TEMP_DIR = "dxt-build"

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "📦 Building WordPress MCP DXT Package" -ForegroundColor Cyan  
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Clean up any previous build
if (Test-Path $TEMP_DIR) {
    Remove-Item -Path $TEMP_DIR -Recurse -Force
}
if (Test-Path $OUTPUT_NAME) {
    Remove-Item -Path $OUTPUT_NAME -Force
}

# Create temp directory structure
Write-Host "Creating package structure..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path $TEMP_DIR | Out-Null
New-Item -ItemType Directory -Path "$TEMP_DIR\mcp-server" | Out-Null
New-Item -ItemType Directory -Path "$TEMP_DIR\wp-mcp-plugin" | Out-Null

# Copy manifest
Write-Host "📄 Copying manifest..." -ForegroundColor Yellow
Copy-Item -Path "dxt-manifest.json" -Destination "$TEMP_DIR\manifest.json"

# Copy MCP server files
Write-Host "🐍 Copying MCP server files..." -ForegroundColor Yellow
Copy-Item -Path "mcp-server\*.py" -Destination "$TEMP_DIR\mcp-server\" -Recurse
Copy-Item -Path "mcp-server\requirements.txt" -Destination "$TEMP_DIR\mcp-server\"
if (Test-Path "mcp-server\.env.example") {
    Copy-Item -Path "mcp-server\.env.example" -Destination "$TEMP_DIR\mcp-server\"
}

# Create tools subdirectory if exists
if (Test-Path "mcp-server\tools") {
    New-Item -ItemType Directory -Path "$TEMP_DIR\mcp-server\tools" -Force | Out-Null
    Copy-Item -Path "mcp-server\tools\*.py" -Destination "$TEMP_DIR\mcp-server\tools\" -ErrorAction SilentlyContinue
}

# Copy WordPress plugin files
Write-Host "📝 Copying WordPress plugin..." -ForegroundColor Yellow
Copy-Item -Path "wp-mcp-plugin\*.php" -Destination "$TEMP_DIR\wp-mcp-plugin\"
if (Test-Path "wp-mcp-plugin\readme.txt") {
    Copy-Item -Path "wp-mcp-plugin\readme.txt" -Destination "$TEMP_DIR\wp-mcp-plugin\"
}
if (Test-Path "wp-mcp-plugin\includes") {
    Copy-Item -Path "wp-mcp-plugin\includes" -Destination "$TEMP_DIR\wp-mcp-plugin\" -Recurse
}
if (Test-Path "wp-mcp-plugin\admin") {
    Copy-Item -Path "wp-mcp-plugin\admin" -Destination "$TEMP_DIR\wp-mcp-plugin\" -Recurse
}

# Copy documentation
Write-Host "📚 Copying documentation..." -ForegroundColor Yellow
Copy-Item -Path "README.md" -Destination "$TEMP_DIR\"
Copy-Item -Path "LICENSE" -Destination "$TEMP_DIR\"
Copy-Item -Path "QUICKSTART.md" -Destination "$TEMP_DIR\"
Copy-Item -Path "CHANGELOG.md" -Destination "$TEMP_DIR\"

Write-Host ""
Write-Host "🎁 Creating DXT package..." -ForegroundColor Yellow

# Create tar.gz archive (which is what .dxt really is)
# Using .NET compression as fallback since tar might not be available
try {
    # Try using tar first if available
    $tarExists = Get-Command tar -ErrorAction SilentlyContinue
    if ($tarExists) {
        Set-Location $TEMP_DIR
        tar -czf "..\$OUTPUT_NAME" *
        Set-Location ..
        Write-Host "✅ Created $OUTPUT_NAME using tar" -ForegroundColor Green
    }
    else {
        # Use PowerShell compression as fallback
        Add-Type -AssemblyName System.IO.Compression.FileSystem
        $zipPath = "$OUTPUT_NAME.zip"
        
        # Create zip first
        [System.IO.Compression.ZipFile]::CreateFromDirectory($TEMP_DIR, $zipPath)
        
        # Rename to .dxt
        Move-Item -Path $zipPath -Destination $OUTPUT_NAME -Force
        Write-Host "✅ Created $OUTPUT_NAME using PowerShell compression" -ForegroundColor Green
        Write-Host "⚠️  Note: This is a ZIP format. For proper tar.gz, use WSL or Git Bash" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "❌ Error creating package: $_" -ForegroundColor Red
}

# Cleanup
Write-Host ""
Write-Host "Cleaning up temporary files..." -ForegroundColor Yellow
Remove-Item -Path $TEMP_DIR -Recurse -Force

if (Test-Path $OUTPUT_NAME) {
    $fileSize = (Get-Item $OUTPUT_NAME).Length / 1MB
    Write-Host ""
    Write-Host "=====================================" -ForegroundColor Cyan
    Write-Host "📦 DXT Package Build Complete!" -ForegroundColor Green
    Write-Host "=====================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Package: $OUTPUT_NAME" -ForegroundColor White
    Write-Host "Version: $VERSION" -ForegroundColor White
    Write-Host "Size: $([math]::Round($fileSize, 2)) MB" -ForegroundColor White
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Test locally: dxt install $OUTPUT_NAME" -ForegroundColor White
    Write-Host "2. Submit to Anthropic via their submission process" -ForegroundColor White
    Write-Host "3. Share with the community!" -ForegroundColor White
    Write-Host ""
    Write-Host '"Intelligence Combined 🧠"' -ForegroundColor Magenta
    Write-Host "=====================================" -ForegroundColor Cyan
}
else {
    Write-Host "❌ Failed to create DXT package" -ForegroundColor Red
}