#!/usr/bin/env bash
# Builds PlutoVetVisit.dll with Mono msbuild and assembles the r2modman test zip.
# Requirements: mono + msbuild + nuget (Mono.framework), python3 + Pillow.
set -euo pipefail
cd "$(dirname "$0")"
VERSION=$(python3 -c "import json;print(json.load(open('thunderstore/manifest.json'))['version_number'])")

echo "==> regenerating art"
python3 tools/make_art.py

echo "==> restoring packages"
nuget restore packages.config -PackagesDirectory packages -ConfigFile nuget.config >/dev/null

echo "==> building"
msbuild PlutoVetVisit.csproj -p:Configuration=Release -v:m -nologo

echo "==> validating"
python3 tools/validate.py

echo "==> testing"
python3 -W error::ResourceWarning -m unittest discover -s tools/tests -q

echo "==> packaging"
rm -rf dist && mkdir -p dist/pkg/plugins
cp bin/Release/PlutoVetVisit.dll dist/pkg/plugins/
cp thunderstore/manifest.json thunderstore/README.md thunderstore/CHANGELOG.md thunderstore/icon.png dist/pkg/
[ -f vet_check.sh ] && cp vet_check.sh dist/pkg/
( cd dist/pkg && zip -qr "../Pluto_Vet_Visit-${VERSION}.zip" . )
rm -rf dist/pkg
ls -la dist/
echo "==> done: dist/Pluto_Vet_Visit-${VERSION}.zip"
