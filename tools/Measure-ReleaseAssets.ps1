[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$AssetDirectory,
    [Parameter(Mandatory=$true)][string]$OutputDirectory,
    [string]$ManifestPath = ''
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($ManifestPath)) { $ManifestPath = Join-Path $PSScriptRoot '..\release-assets.json' }
$assetRoot = (Resolve-Path -LiteralPath $AssetDirectory).ProviderPath
$manifest = Get-Content -LiteralPath $ManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
if ($manifest.schema_version -ne 1 -or $manifest.release -ne 'v0.2.0') { throw 'Unexpected release manifest.' }
$outputRoot = [IO.Path]::GetFullPath($OutputDirectory)
if (Test-Path -LiteralPath $outputRoot) { throw 'Use a new output directory.' }
$names = @{}
$records = @()
foreach ($asset in $manifest.assets) {
    $name = [string]$asset.name
    if ([IO.Path]::GetFileName($name) -cne $name -or $name.Contains(':') -or $names.ContainsKey($name)) { throw 'Unsafe or duplicate asset name.' }
    $names[$name] = $true
    $item = Get-Item -LiteralPath (Join-Path $assetRoot $name)
    if ($item.PSIsContainer -or $item.Length -ne [long]$asset.bytes) { throw "Size mismatch: $name" }
    $stream = [IO.File]::OpenRead($item.FullName)
    $algorithm = [Security.Cryptography.SHA256]::Create()
    try { $hash = [BitConverter]::ToString($algorithm.ComputeHash($stream)).Replace('-', '').ToLowerInvariant() }
    finally { $algorithm.Dispose(); $stream.Dispose() }
    if ($hash -cne $asset.sha256) { throw "Hash mismatch: $name" }
    $records += [pscustomobject]@{ name=$name; bytes=$item.Length; sha256=$hash }
}
[IO.Directory]::CreateDirectory($outputRoot) | Out-Null
$report = [ordered]@{ schema_version=1; release=$manifest.release; status='HASHES_VERIFIED'; assets=$records }
$utf8 = New-Object System.Text.UTF8Encoding($false)
[IO.File]::WriteAllText((Join-Path $outputRoot 'measured-assets.json'), (($report | ConvertTo-Json -Depth 6)+"`n"), $utf8)
Write-Output ("Verified {0} payload assets. This is an integrity check, not authentication or a content audit." -f $records.Count)
