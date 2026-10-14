param(
    [string]$ReleaseName = 'WireConform_ETAPS_iFS_2027'
)

$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$ReleaseRoot = Join-Path $Root 'release'
$PackageRoot = Join-Path $ReleaseRoot $ReleaseName
$ZipPath = Join-Path $ReleaseRoot ($ReleaseName + '.zip')

if (Test-Path -LiteralPath $PackageRoot) {
    throw "Release directory already exists: $PackageRoot. Refusing to overwrite it."
}
if (Test-Path -LiteralPath $ZipPath) {
    throw "Release ZIP already exists: $ZipPath. Refusing to overwrite it."
}

New-Item -ItemType Directory -Path $PackageRoot -Force | Out-Null

$Items = @(
    'AGENTS.md', 'README.md', 'START_HERE.md', 'RUN_REAL_EXPERIMENTS.md',
    'SUBMISSION_READINESS.md', 'NOVELTY_AND_RISKS.md', 'package.json',
    'package-lock.json', 'openapitools.json', 'openapi-ts.config.mjs',
    'requirements-dev.txt', 'artifact', 'runner', 'outputs', 'experiments',
    'validation', 'tests', 'codex', 'evidence', 'manuscript', '.github'
)

foreach ($Item in $Items) {
    $Source = Join-Path $Root $Item
    if (-not (Test-Path -LiteralPath $Source)) {
        throw "Required release item missing: $Source"
    }
    Copy-Item -LiteralPath $Source -Destination $PackageRoot -Recurse -Force
}

# Runtime caches and render intermediates are not needed to audit or recreate the study.
$ExcludedRelative = @(
    '.pydeps', '.venv', '.pytest_cache', '.pytest_tmp', '.tools', 'node_modules',
    'artifact\\__pycache__', 'runner\\__pycache__', 'tests\\__pycache__',
    'evidence\\pdf_render'
)
foreach ($Relative in $ExcludedRelative) {
    $Target = Join-Path $PackageRoot $Relative
    if (Test-Path -LiteralPath $Target) {
        Remove-Item -LiteralPath $Target -Recurse -Force
    }
}

$Readme = @"
# WireConform release package

This archive contains the sources, frozen corpus, generated clients, raw observations,
reproduction records, final manuscript, and audit material for the ETAPS 2027 iFS study.

Install dependencies with `npm ci` and `python -m pip install -r requirements-dev.txt`,
then follow `evidence/final/REPRODUCE.md`.

Runtime dependency caches are intentionally excluded. Exact package versions are pinned by
`package-lock.json`; generated source and all captured evidence are included.
"@
Set-Content -LiteralPath (Join-Path $PackageRoot 'RELEASE_NOTES.md') -Value $Readme -Encoding utf8

$Files = Get-ChildItem -LiteralPath $PackageRoot -Recurse -File |
    Sort-Object FullName |
    ForEach-Object {
        [PSCustomObject]@{
            path = $_.FullName.Substring($PackageRoot.Length + 1).Replace('\\', '/')
            sha256 = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
            bytes = $_.Length
        }
    }
$Manifest = [PSCustomObject]@{
    release_name = $ReleaseName
    generated_utc = (Get-Date).ToUniversalTime().ToString('o')
    file_count = @($Files).Count
    files = @($Files)
}
$Manifest | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $PackageRoot 'evidence\final\SHA256SUMS.json') -Encoding utf8

Compress-Archive -LiteralPath $PackageRoot -DestinationPath $ZipPath -CompressionLevel Optimal
Get-FileHash -LiteralPath $ZipPath -Algorithm SHA256 | Format-List Path,Hash
