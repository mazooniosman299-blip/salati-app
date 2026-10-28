#!/usr/bin/env python3
"""Verify and use an existing release identity. This script never creates a key."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent

def fail(message):
    raise RuntimeError(message)

def execute(command, env):
    result = subprocess.run([str(v) for v in command], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        fail(Path(str(command[0])).name + ' failed. Check the existing key, alias and password file; credentials are never logged.')
    return result.stdout

def existing_file(variable):
    value = os.environ.get(variable)
    if not value:
        fail('Missing ' + variable + '. Restore the saved release key; a replacement will not be generated.')
    path = Path(value).expanduser().resolve()
    if not path.is_file():
        fail(variable + ' does not reference an existing file. Restore the saved release key; a replacement will not be generated.')
    if path.is_relative_to(ROOT / 'dist'):
        fail('Signing secrets must be stored outside the public dist directory.')
    if os.name != 'nt' and stat.S_IMODE(path.stat().st_mode) & 0o077:
        fail(variable + ' must have private permissions; use chmod 600 on the existing file.')
    return path

def load_identity():
    file = ROOT / 'android' / 'signing-identity.json'
    if not file.is_file():
        fail('Missing android/signing-identity.json. Restore the fixed public signing identity.')
    identity = json.loads(file.read_text(encoding='utf-8'))
    if not re.fullmatch('[0-9a-f]{64}', identity['certificate_sha256']):
        fail('Invalid fixed signing certificate fingerprint.')
    return identity

def check_key(identity):
    key = existing_file('SALATI_KEYSTORE')
    password_file = existing_file('SALATI_PASSWORD_FILE')
    password = password_file.read_text(encoding='utf-8').rstrip('\r\n')
    if not password:
        fail('The saved password file is empty.')
    env = os.environ.copy()
    env['SALATI_SIGNING_PASSWORD_INTERNAL'] = password
    java = Path(os.environ['JAVA_HOME']) / 'bin' / ('keytool.exe' if os.name == 'nt' else 'keytool') if os.environ.get('JAVA_HOME') else shutil.which('keytool')
    if not java:
        fail('Install a JDK or set JAVA_HOME to use the existing key.')
    certificate = execute([java, '-exportcert', '-alias', identity['key_alias'], '-keystore', key,
                           '-storepass:env', 'SALATI_SIGNING_PASSWORD_INTERNAL'], env)
    fingerprint = hashlib.sha256(certificate).hexdigest()
    if fingerprint != identity['certificate_sha256']:
        fail('SIGNING CERTIFICATE MISMATCH. This key is not the fixed Salati release identity; build/signing stopped.')
    return key, env

def sdk_tool(directory, name):
    candidates = [directory / name, directory / (name + '.exe'), directory / (name + '.bat')]
    found = next((p for p in candidates if p.is_file()), None)
    if not found:
        fail('Missing Android build tool: ' + name)
    return found

def manifest(apk, aapt, env):
    text = execute([aapt, 'dump', 'badging', apk], env).decode(errors='replace')
    match = re.search(r"package: name='([^']+)' versionCode='(\d+)' versionName='([^']+)'", text)
    if not match:
        fail('Could not verify APK application ID and version.')
    return {'application_id': match[1], 'version_code': int(match[2]), 'version_name': match[3]}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-key', action='store_true')
    parser.add_argument('--input', type=Path, default=ROOT / 'android/app/build/outputs/apk/release/app-release-unsigned.apk')
    parser.add_argument('--output', type=Path)
    options = parser.parse_args()
    identity = load_identity()
    key, env = check_key(identity)
    if options.check_key:
        print(json.dumps({'release_identity_verified': True, 'key_alias': identity['key_alias'], 'certificate_sha256': identity['certificate_sha256']}))
        return
    directory_value = os.environ.get('ANDROID_BUILD_TOOLS')
    if not directory_value:
        fail('Set ANDROID_BUILD_TOOLS to an installed SDK build-tools directory.')
    directory = Path(directory_value).expanduser().resolve()
    align, signer, aapt = (sdk_tool(directory, name) for name in ['zipalign', 'apksigner', 'aapt'])
    source = options.input.expanduser().resolve()
    if not source.is_file():
        fail('The unsigned APK does not exist. Build the release with the saved key configured first.')
    before = manifest(source, aapt, env)
    if before['application_id'] != identity['application_id']:
        fail('APPLICATION ID MISMATCH. Refusing to sign a different application.')
    destination = (options.output or ROOT / 'dist/downloads' / ('salati-' + before['version_name'] + '.apk')).expanduser().resolve()
    if destination == source:
        fail('Input and output APK paths must be different.')
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='salati-signing-', dir=destination.parent) as temp:
        aligned, signed = Path(temp) / 'aligned.apk', Path(temp) / 'signed.apk'
        execute([align, '-f', '-p', '4', source, aligned], env)
        execute([signer, 'sign', '--v4-signing-enabled', 'false', '--ks', key,
                 '--ks-key-alias', identity['key_alias'], '--ks-pass', 'env:SALATI_SIGNING_PASSWORD_INTERNAL',
                 '--key-pass', 'env:SALATI_SIGNING_PASSWORD_INTERNAL', '--out', signed, aligned], env)
        verification = execute([signer, 'verify', '--verbose', '--print-certs', signed], env).decode(errors='replace')
        fingerprints = re.findall(r'Signer #\d+ certificate SHA-256 digest: ([0-9a-fA-F]+)', verification)
        if fingerprints != [identity['certificate_sha256']]:
            fail('Signed APK certificate does not match the fixed release identity.')
        execute([align, '-c', '-p', '4', signed], env)
        if manifest(signed, aapt, env) != before:
            fail('APK identity or version changed during signing.')
        os.replace(signed, destination)
        destination.chmod(0o644)
    digest = hashlib.sha256(destination.read_bytes()).hexdigest()
    print(json.dumps({**before, 'signed_apk': str(destination), 'apk_sha256': digest,
                      'certificate_sha256': identity['certificate_sha256'], 'key_alias': identity['key_alias']}))

if __name__ == '__main__':
    try:
        main()
    except RuntimeError as error:
        print('ERROR: ' + str(error), file=sys.stderr)
        sys.exit(1)
    except Exception:
        print('ERROR: Signing configuration could not be read or processed. Private details are not logged.', file=sys.stderr)
        sys.exit(1)
