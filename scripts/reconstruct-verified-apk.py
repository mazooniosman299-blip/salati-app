#!/usr/bin/env python3
"""Publish an APK v2/v3 signing block without exposing the private signing key.

A local offline signer produces the exact original-key APK and exports ONLY its
public signing block. CI signs an identical unsigned archive with an ephemeral
throwaway key to normalize ZIP metadata, swaps in the verified original-key block,
and confirms the complete signed SHA-256. No secret key or password enters GitHub.
"""
import argparse,base64,hashlib,json,struct,zlib
from pathlib import Path

def split(apk):
    eocd=apk.rfind(b'PK\x05\x06')
    if eocd<0 or eocd+22>len(apk):
        raise ValueError('Missing ZIP EOCD')
    offset=struct.unpack_from('<I',apk,eocd+16)[0]
    if apk[offset-16:offset]!=b'APK Sig Block 42':
        raise ValueError('Missing APK Signing Block in temporary certificate archive')
    size=struct.unpack_from('<Q',apk,offset-24)[0]+8
    start=offset-size
    if start<0:raise ValueError('Invalid signing block')
    return start,offset,eocd

def sha(data):return hashlib.sha256(data).hexdigest()

def main():
    p=argparse.ArgumentParser()
    for x in ['unsigned','dummy','proof','manifest','output']:
        p.add_argument('--'+x,required=True)
    a=p.parse_args()
    expected=json.loads(Path(a.manifest).read_text())
    original=Path(a.unsigned).read_bytes()
    if sha(original)!=expected['unsignedSha256']:
        raise ValueError('Unsigned ZIP checksum mismatch. Refuse to attach a signature to new code.')
    dummy=Path(a.dummy).read_bytes()
    dstart,dend,deocd=split(dummy)
    compressed=base64.b64decode(Path(a.proof).read_text().strip(),validate=True)
    block=zlib.decompress(compressed)
    if sha(block)!=expected['signatureBlockSha256'] or len(block)!=expected['signatureBlockBytes']:
        raise ValueError('Original certificate signing block checksum mismatch')
    if block[-16:]!=b'APK Sig Block 42':
        raise ValueError('Invalid original-key signing block format')
    # The signed block begins at the already normalized ZIP prefix boundary.
    # apk signing digests all bytes outside the block, so matching SHA-256 of
    # the COMPLETE output is necessary in addition to apksigner verification.
    merged=bytearray(dummy[:dstart]+block+dummy[dend:])
    neweocd=deocd+len(block)-(dend-dstart)
    struct.pack_into('<I',merged,neweocd+16,dstart+len(block))
    if sha(merged)!=expected['sha256'] or len(merged)!=expected['size']:
        raise ValueError('Unsigned APK was not normalized byte-identically; no APK published')
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_bytes(merged)
    print('Public signature block restored original-key APK:',out.name,sha(merged))

if __name__=='__main__':main()
