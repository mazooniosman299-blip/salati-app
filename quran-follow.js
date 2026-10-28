// A cue is announced by the audio player only after its recording starts.
// Highlighting never depends on guessed durations or a wall-clock timer.
export class QuranFollow{
 constructor({find,ensure,scroll,render,canScroll=()=>true,enabled=true}){Object.assign(this,{find,ensure,scroll,render,canScroll,enabled});this.current=null;this.highlighted=null;}
 mark(element){if(this.highlighted!==element){this.highlighted?.classList.remove('is-reciting');this.highlighted?.removeAttribute('aria-current');this.highlighted=element;}if(element){element.classList.add('is-reciting');element.setAttribute('aria-current','true');}}
 show(verse,cue={}){const key=verse?verse.s+':'+verse.a:cue.intro?'intro:'+cue.surah:null;if(!key){this.clear();return;}const changed=key!==this.current?.key;this.current={key,verse,cue};this.refresh(changed);}
 refresh(move=false){if(!this.current)return;const {verse,cue}=this.current;this.render(verse,cue);const allowed=this.enabled&&this.canScroll();let element=verse?this.find(verse):null;if(verse&&allowed&&!element)element=this.ensure(verse);this.mark(element);if(move&&allowed&&element)this.scroll(element);}
 setEnabled(enabled){this.enabled=enabled;this.refresh(enabled);}
 clear(){this.current=null;this.mark(null);this.render(null,null);}
}
