#!/usr/bin/env python3
"""Mechanical user-requested photo crop + unchanged old mark, not image generation."""
from pathlib import Path
from PIL import Image,ImageChops,ImageStat
import base64,hashlib,json,shutil

root=Path(__file__).resolve().parents[1];reference=root/'design-references/brand-20261105'
photo=root/'design-references/mosque-20261105/fahrul-azmi-sunset.webp'
mark=reference/'mark-original.webp'
hash=lambda b:hashlib.sha256(b).hexdigest()
assert hash(photo.read_bytes())=='9b111a3f505da38e4871b069353322b4e3510c20dac7af213664a95e8c70f97e'
assert hash(mark.read_bytes())=='7ccb9017778d5bd4637dc1d33b98fc1108a16e100f2f50ff5917cf0fde4b458a'
scene=Image.open(photo).convert('RGB');assert scene.size==(960,719)
# A square photograph crop retains the mosque and real warm sky for icons.
# The wide home hero uses the complete photo and its own CSS focal crop.
crop=(180,0,899,719)
tile=scene.crop(crop).resize((512,512),Image.Resampling.LANCZOS).convert('RGBA')
tile=Image.alpha_composite(tile,Image.new('RGBA',tile.size,(0,0,0,40)))
logo=Image.open(mark).convert('RGBA');size=round(512*.64);logo=logo.resize((size,size),Image.Resampling.LANCZOS)
tile.alpha_composite(logo,((512-size)//2,(512-size)//2));tile.convert('RGB').save(reference/'composite-512.png',optimize=True)
pwa=root/'dist/icon-512.webp';tile.convert('RGB').save(pwa,format='WEBP',quality=88,method=6)
# All visible brand surfaces derive from this SAME published tile.
canonical=Image.open(pwa).convert('RGB');canonical.resize((192,192),Image.Resampling.LANCZOS).save(root/'dist/icon-192.png',optimize=True)
native=root/'android/app/src/main/res/drawable-nodpi';shutil.copyfile(pwa,native/'ic_salati_launcher.webp');shutil.copyfile(mark,native/'ic_salati_mark.webp')
encoded=base64.b64encode(pwa.read_bytes()).decode();(root/'dist/icon.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><image width="512" height="512" href="data:image/webp;base64,{encoded}"/></svg>\n')
hero=root/'dist/images/mosque-sunset-selected.webp';scene.save(hero,format='WEBP',quality=86,method=6)
error=sum(ImageStat.Stat(ImageChops.difference(scene,Image.open(hero).convert('RGB'))).mean)/3
assert error<6.5,('Photo codec export changed appearance',error)
meta={'user_scope':'Restore old selected crescent/minaret over user-selected real mosque sunset photo; same identity in app/launcher/PWA','photo_source':'https://unsplash.com/photos/4-pillar-mosque-in-front-of-rotunda-during-golden-hour-vR-Nb0bncOY','photo_author':'Fahrul Azmi','photo_license':'https://unsplash.com/license','photo_sha256':hash(photo.read_bytes()),'mark_sha256':hash(mark.read_bytes()),'square_crop':crop,'mark_fraction':.64,'photo_readability_overlay_alpha':40,'processing':'Mechanical crop, standard resize/codec export, and original alpha-mark composition only. No generated/repainted architecture or redrawn logo. Full real photo archived.','canonical_tile_sha256':hash(pwa.read_bytes()),'native_same_bytes':True,'hero_sha256':hash(hero.read_bytes()),'hero_codec_mean_error':error,'hero_bytes':hero.stat().st_size,'tile_bytes':pwa.stat().st_size,'png192_bytes':(root/'dist/icon-192.png').stat().st_size}
(reference/'SOURCES.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n');print(json.dumps(meta,ensure_ascii=False))
