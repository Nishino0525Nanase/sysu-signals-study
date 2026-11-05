#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
: "${ANDROID_BUILD_TOOLS:?Set ANDROID_BUILD_TOOLS to SDK build-tools/35.0.0}"
: "${ANDROID_JAR:?Set ANDROID_JAR to platforms/android-35/android.jar}"
: "${SIGNING_KEYSTORE:?Set a private signing keystore path}"
: "${SIGNING_PASSWORD_FILE:?Set a private signing password file path}"
mkdir -p build/classes build/gen build/dex build/assets/www
python3 - <<'PY'
from pathlib import Path
import shutil
src=Path('../dist'); dest=Path('build/assets/www')
if dest.exists(): shutil.rmtree(dest)
shutil.copytree(src,dest,ignore=shutil.ignore_patterns('*.apk','*.inspect.ndjson'))
PY
"$ANDROID_BUILD_TOOLS/aapt" package -f -M AndroidManifest.xml -I "$ANDROID_JAR" -S res -J build/gen -A build/assets -F build/base.apk
find src build/gen -name '*.java' -print > build/sources.txt
if command -v javac >/dev/null 2>&1; then
  javac -encoding UTF-8 -source 8 -target 8 -bootclasspath "$ANDROID_JAR" -d build/classes @build/sources.txt
else
  java -m jdk.compiler/com.sun.tools.javac.Main -encoding UTF-8 -source 8 -target 8 -bootclasspath "$ANDROID_JAR" -d build/classes @build/sources.txt
fi
find build/classes -name '*.class' -print > build/classes.txt
java -cp "$ANDROID_BUILD_TOOLS/lib/d8.jar" com.android.tools.r8.D8 --min-api 24 --lib "$ANDROID_JAR" --output build/dex @build/classes.txt
cp build/base.apk build/unsigned.apk
(cd build/dex && zip -q -j ../unsigned.apk classes.dex)
"$ANDROID_BUILD_TOOLS/zipalign" -f 4 build/unsigned.apk build/aligned.apk
"$ANDROID_BUILD_TOOLS/apksigner" sign --ks "$SIGNING_KEYSTORE" --ks-key-alias sysusignals --ks-pass "file:$SIGNING_PASSWORD_FILE" --out build/signed.apk build/aligned.apk
"$ANDROID_BUILD_TOOLS/apksigner" verify --verbose build/signed.apk
python3 - <<'PY'
import os, zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
version=ET.parse('AndroidManifest.xml').getroot().get('{http://schemas.android.com/apk/res/android}versionName')
with zipfile.ZipFile('build/signed.apk') as package:
    assert package.testzip() is None, 'APK archive integrity check failed'
destination=Path('build')/('sysu-signals-study-v'+version+'.apk')
os.replace('build/signed.apk',destination)
print(destination.resolve())
PY
