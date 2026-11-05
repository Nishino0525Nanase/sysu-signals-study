#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
: "${ANDROID_BUILD_TOOLS:?Set ANDROID_BUILD_TOOLS to SDK build-tools/35.0.0}"
: "${ANDROID_JAR:?Set ANDROID_JAR to platforms/android-35/android.jar}"
: "${SIGNING_KEYSTORE:?Set a private signing keystore path}"
: "${SIGNING_PASSWORD_FILE:?Set a private signing password file path}"
mkdir -p build/classes build/gen build/dex build/assets/www
APK_PACKAGE_DIR="$(mktemp -d build/package.XXXXXX)"
export APK_PACKAGE_DIR
python3 - <<'PY'
from pathlib import Path
import shutil
src=Path('../dist'); dest=Path('build/assets/www')
if dest.exists(): shutil.rmtree(dest)
shutil.copytree(src,dest,ignore=shutil.ignore_patterns('*.apk','*.apk.sha256','*.inspect.ndjson','*.tmp','*.tmp.*','*.cn-tmp'))
PY
"$ANDROID_BUILD_TOOLS/aapt" package -f -M AndroidManifest.xml -I "$ANDROID_JAR" -S res -J build/gen -A build/assets -F "$APK_PACKAGE_DIR/base.apk"
find src build/gen -name '*.java' -print > build/sources.txt
if command -v javac >/dev/null 2>&1; then
  javac -encoding UTF-8 -source 8 -target 8 -bootclasspath "$ANDROID_JAR" -d build/classes @build/sources.txt
else
  java -m jdk.compiler/com.sun.tools.javac.Main -encoding UTF-8 -source 8 -target 8 -bootclasspath "$ANDROID_JAR" -d build/classes @build/sources.txt
fi
find build/classes -name '*.class' -print > build/classes.txt
java -cp "$ANDROID_BUILD_TOOLS/lib/d8.jar" com.android.tools.r8.D8 --min-api 24 --lib "$ANDROID_JAR" --output build/dex @build/classes.txt
python3 - <<'PY'
import io, os, zipfile
from pathlib import Path
package_dir=Path(os.environ['APK_PACKAGE_DIR'])
with zipfile.ZipFile(io.BytesIO((package_dir/'base.apk').read_bytes())) as base:
    assert base.testzip() is None, 'Resource archive integrity check failed'
    with zipfile.ZipFile(package_dir/'unsigned.tmp', 'w') as package:
        for entry in base.infolist():
            package.writestr(entry,base.read(entry.filename))
        package.write('build/dex/classes.dex','classes.dex',compress_type=zipfile.ZIP_DEFLATED)
os.replace(package_dir/'unsigned.tmp',package_dir/'unsigned.apk')
PY
"$ANDROID_BUILD_TOOLS/zipalign" -f 4 "$APK_PACKAGE_DIR/unsigned.apk" "$APK_PACKAGE_DIR/aligned.apk"
"$ANDROID_BUILD_TOOLS/apksigner" sign --ks "$SIGNING_KEYSTORE" --ks-key-alias sysusignals --ks-pass "file:$SIGNING_PASSWORD_FILE" --out "$APK_PACKAGE_DIR/signed.apk" "$APK_PACKAGE_DIR/aligned.apk"
"$ANDROID_BUILD_TOOLS/apksigner" verify --verbose "$APK_PACKAGE_DIR/signed.apk"
python3 - <<'PY'
import os, zipfile, io
import xml.etree.ElementTree as ET
from pathlib import Path
version=ET.parse('AndroidManifest.xml').getroot().get('{http://schemas.android.com/apk/res/android}versionName')
signed=Path(os.environ['APK_PACKAGE_DIR'])/'signed.apk';data=signed.read_bytes()
with zipfile.ZipFile(io.BytesIO(data)) as package:
    assert package.testzip() is None, 'APK archive integrity check failed'
destination=Path('build')/('sysu-signals-study-v'+version+'.apk')
temporary=Path(os.environ['APK_PACKAGE_DIR'])/'release.tmp';temporary.write_bytes(data);os.replace(temporary,destination)
assert destination.read_bytes()==data,'Final APK write failed'
print(destination.resolve())
PY
