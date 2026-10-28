# Install nature-library-search for Claude Code and/or Codex on Windows.
# Usage (PowerShell):  .\install.ps1            # both carriers
#                      .\install.ps1 -Target claude | codex
# The repo folder stays the single source: each carrier's skills folder gets a directory junction to it,
# so `git pull` in the repo updates both. No admin rights needed for junctions.
param([ValidateSet('both', 'claude', 'codex')] [string]$Target = 'both')
$src = Split-Path -Parent $MyInvocation.MyCommand.Path
$name = 'nature-library-search'
$dests = @()
if ($Target -in 'both', 'claude') { $dests += Join-Path $HOME '.claude\skills' }
if ($Target -in 'both', 'codex') { $dests += Join-Path $HOME '.codex\skills' }
foreach ($d in $dests) {
    New-Item -ItemType Directory -Force $d | Out-Null
    $link = Join-Path $d $name
    if ((Resolve-Path $src).Path -eq (Join-Path (Resolve-Path $d).Path $name)) { Write-Host "already the source: $link"; continue }
    if (Test-Path $link) {
        $item = Get-Item $link -Force
        if ($item.LinkType) { Write-Host "already linked: $link -> $($item.Target)"; continue }
        Write-Warning "$link exists and is not a link; leaving it alone (rename it and rerun to link)."
        continue
    }
    New-Item -ItemType Junction -Path $link -Target $src | Out-Null
    Write-Host "linked $link -> $src"
}
try { python -I -c "import matplotlib" 2>$null; if ($LASTEXITCODE -ne 0) { Write-Warning 'pip install matplotlib (needed for PRISMA diagrams)' } } catch { Write-Warning 'Python 3 not found' }
Write-Host 'Next: copy config\library.template.yaml to config\library.<yours>.yaml, point manifest.yaml at it, then ask Claude or Codex to run a full library search (or type $nature-library-search in Codex).'
