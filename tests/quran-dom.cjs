// Minimal DOM for checking Quran text construction without a browser or a layout engine.
class Node{
 constructor(type,tag='',text=''){this.nodeType=type;this.tagName=tag.toUpperCase();this.value=text;this.childNodes=[];this.parentNode=null;this.dataset={};this.style={};this.attributes=new Map();this.classes=new Set();this.classList={add:v=>this.classes.add(v),remove:v=>this.classes.delete(v),contains:v=>this.classes.has(v)};}
 get children(){return this.childNodes.filter(n=>n.nodeType===1);}
 get parentElement(){return this.parentNode;}get options(){return this.children;}
 get className(){return [...this.classes].join(' ');}set className(value){this.classes=new Set(value.split(/\s+/).filter(Boolean));}
 get textContent(){return this.nodeType===3?this.value:this.childNodes.map(n=>n.textContent).join('');}
 set textContent(value){if(this.nodeType===3){this.value=value;return;}this.replaceChildren();if(value)this.append(new Node(3,'',String(value)));}
 append(...nodes){for(let node of nodes){if(typeof node==='string')node=new Node(3,'',node);if(node.nodeType===11){this.append(...node.childNodes.slice());continue;}node.remove();this.childNodes.push(node);node.parentNode=this;}}
 replaceChildren(...nodes){for(const child of this.childNodes)child.parentNode=null;this.childNodes=[];this.append(...nodes);}
 insertBefore(node,before){if(!before){this.append(node);return;}const index=this.childNodes.indexOf(before);if(index<0)throw Error('Missing insertion reference');node.remove();this.childNodes.splice(index,0,node);node.parentNode=this;}
 remove(){if(this.parentNode){this.parentNode.childNodes.splice(this.parentNode.childNodes.indexOf(this),1);this.parentNode=null;}}
 replaceWith(node){const parent=this.parentNode;if(!parent)return;const index=parent.childNodes.indexOf(this);const replacements=node.nodeType===11?node.childNodes.slice():[node];this.remove();for(let i=0;i<replacements.length;i++){replacements[i].remove();parent.childNodes.splice(index+i,0,replacements[i]);replacements[i].parentNode=parent;}}
 setAttribute(key,value){this.attributes.set(key,String(value));}removeAttribute(key){this.attributes.delete(key);}
 matches(selector){if(selector==='[data-ayah]')return !!this.dataset.ayah;if(selector==='[data-reading-page]')return !!this.dataset.readingPage;if(selector.startsWith('.'))return this.classes.has(selector.slice(1));const match=selector.match(/^\[data-ayah="([\d:]+)"\]$/);return match?this.dataset.ayah===match[1]:this.tagName===selector.toUpperCase();}
 querySelectorAll(selector){return this.children.flatMap(child=>[...(child.matches(selector)?[child]:[]),...child.querySelectorAll(selector)]);}
 querySelector(selector){return this.querySelectorAll(selector)[0]||null;}
 closest(selector){for(let node=this;node;node=node.parentNode)if(node.matches(selector))return node;return null;}
 scrollIntoView(){this.scrolled=(this.scrolled||0)+1;}focus(){this.focused=true;}
 get isConnected(){return !!this.parentNode;}
 getBoundingClientRect(){return this.bounds||{top:0,bottom:0};}
}
function makeDocument(){
 const elements=new Map();return {
  elements,getElementById:id=>{if(!elements.has(id))elements.set(id,new Node(1,'div'));return elements.get(id);},
  querySelector:()=>null,createElement:tag=>new Node(1,tag),createTextNode:text=>new Node(3,'',text),createDocumentFragment:()=>new Node(11),
  createTreeWalker(root){const nodes=[];const visit=node=>{if(node.nodeType===3)nodes.push(node);else node.childNodes.forEach(visit);};visit(root);let index=-1;return {nextNode(){return nodes[++index]||null;},get currentNode(){return nodes[index];}};}
 };
}
module.exports={Node,makeDocument};
