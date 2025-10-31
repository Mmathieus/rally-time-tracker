# Rally Time Tracker - PostgreSQL Authentication Setup Script
# This script creates pgpass.conf file for automatic PostgreSQL authentication

$pgpassPath = "$env:APPDATA\postgresql\pgpass.conf"
$pgpassDir = Split-Path -Parent $pgpassPath

# Define your database credentials here
# Format: @("host", "port", "database", "username", "password")
# Add more entries as needed for multiple databases
$credentials = @(
    @("localhost", "5432", "rallydb", "postgres", "1234"),
    # Uncomment and modify the lines below to add more databases:
    # @("localhost", "5432", "wrc9db", "postgres", "mypassword"),
    # @("localhost", "5432", "wrc10db", "postgres", "mypassword")
)

try {
    # Create directory if it doesn't exist
    New-Item -ItemType Directory -Path $pgpassDir -Force -ErrorAction Stop | Out-Null

    # Build pgpass.conf content
    $pgpassContent = @()
    foreach ($cred in $credentials) {
        if ($cred.Count -ne 5) {
            throw "Invalid credential format detected. Each entry must have exactly 5 values: host, port, database, username, password"
        }
        $line = $cred -join ":"
        $pgpassContent += $line
    }

    # Write credentials to pgpass.conf (overwrites existing file)
    Set-Content -Path $pgpassPath -Value $pgpassContent -Force -ErrorAction Stop

    # Find the longest username for proper alignment
    $maxUserLength = ($credentials | ForEach-Object { $_[3].Length } | Measure-Object -Maximum).Maximum

    Write-Host "✓ pgpass.conf created successfully at:" -ForegroundColor Green
    Write-Host "  $pgpassPath" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Configured credentials:" -ForegroundColor Magenta
    foreach ($cred in $credentials) {
        $userName = $cred[3].PadRight($maxUserLength)
        Write-Host "  → User: $userName | Database: $($cred[2])" -ForegroundColor Gray
    }
}
catch {
    Write-Host ""
    Write-Host "✗ Error: Failed to create pgpass.conf" -ForegroundColor Red
    Write-Host "  $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Possible solutions:" -ForegroundColor Cyan
    Write-Host "  • Run PowerShell as Administrator" -ForegroundColor Gray
    Write-Host "  • Check if %APPDATA% path is accessible" -ForegroundColor Gray
    Write-Host "  • Verify credential format in the script" -ForegroundColor Gray
    exit 1
}