[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$AssetDirectory,
    [Parameter(Mandatory = $true)][string]$OutputDirectory
)

# Measure only the nine designated assets. No upload or archive modification.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$assetRoot = (Resolve-Path -LiteralPath $AssetDirectory).ProviderPath
if (-not (Test-Path -LiteralPath $assetRoot -PathType Container)) {
    throw 'AssetDirectory must be a directory.'
}
$names = @('ocr_join_tools_20260910_public.zip')
1..8 | ForEach-Object { $names += ('ocr_part_{0:D3}_transport.zip' -f $_) }

$items = @()
foreach ($name in $names) {
    $item = Get-Item -LiteralPath (Join-Path $assetRoot $name)
    if ($item.PSIsContainer -or $item.Length -le 0) { throw "Invalid asset: $name" }
    if ($item.Length -ge 2GB) { throw "Asset must be smaller than 2 GiB: $name" }
    $items += $item
}

$outRoot = [System.IO.Path]::GetFullPath($OutputDirectory)
$sumPath = Join-Path $outRoot 'SHA256SUMS_ASSETS.txt'
$jsonPath = Join-Path $outRoot 'release-assets.json'
foreach ($path in @($sumPath, $jsonPath)) {
    if (Test-Path -LiteralPath $path) { throw 'Output already exists; use a new output directory.' }
}

$records = @()
foreach ($item in $items) {
    $digest = (Get-FileHash -LiteralPath $item.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    $records += [pscustomobject]@{ name = $item.Name; bytes = $item.Length; sha256 = $digest }
}

$manifest = [ordered]@{
    schema_version = 1
    release = 'v0.1.0'
    distribution_date = '2026-09-10'
    measured_at_utc = [DateTime]::UtcNow.ToString('o')
    status = 'measured_only_not_authenticated_or_privacy_audited'
    assets = $records
    restored_zip = [ordered]@{
        name = 'dw_ocr_with_code.zip'
        expected_sha256 = '10e5428a9501ed3f2a754a2eb71d989ae7269d1d220acff428151ec7b6bf59b1'
        source = 'distribution_specification'
        measured = $false
    }
}
$sumText = (($records | ForEach-Object { $_.sha256 + '  ' + $_.name }) -join "`n") + "`n"
$jsonText = ($manifest | ConvertTo-Json -Depth 6) + "`n"
[System.IO.Directory]::CreateDirectory($outRoot) | Out-Null
$utf8 = New-Object System.Text.UTF8Encoding($false)
foreach ($entry in @(@($sumPath, $sumText), @($jsonPath, $jsonText))) {
    $stream = [System.IO.File]::Open($entry[0], [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write)
    try {
        $bytes = $utf8.GetBytes($entry[1])
        $stream.Write($bytes, 0, $bytes.Length)
    } finally { $stream.Dispose() }
}
Write-Output 'Measured 9 assets. This does not authenticate files or audit their contents.'
