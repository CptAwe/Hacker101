!function(t){"object"==typeof exports&&"object"==typeof module?t(require("../../lib/codemirror"),require("../xml/xml"),require("../javascript/javascript"),require("../css/css")):"function"==typeof define&&define.amd?define(["../../lib/codemirror","../xml/xml","../javascript/javascript","../css/css"],t):t(CodeMirror)}(function(f){"use strict";var l={script:[["lang",/(javascript|babel)/i,"javascript"],["type",/^(?:text|application)\/(?:x-)?(?:java|ecma)script$|^module$|^$/i,"javascript"],["type",/./,"text/plain"],[null,null,"javascript"]],style:[["lang",/^css$/i,"css"],["type",/^(text\/)?(x-)?(stylesheet|css)$/i,"css"],["type",/./,"text/plain"],[null,null,"css"]]};var r={};function g(t,e){var a,n=t.match(r[a=e]||(r[a]=new RegExp("\\s+"+a+"\\s*=\\s*('|\")?([^'\"]+)('|\")?\\s*")));return n?/^\s*(.*?)\s*$/.exec(n[2])[1]:""}function h(t,e){return new RegExp((e?"^":"")+"</s*"+t+"s*>","i")}function o(t,e){for(var a in t)for(var n=e[a]||(e[a]=[]),l=t[a],r=l.length-1;0<=r;r--)n.unshift(l[r])}f.defineMode("htmlmixed",function(u,t){var m=f.getMode(u,{name:"xml",htmlMode:!0,multilineTagIndentFactor:t.multilineTagIndentFactor,multilineTagIndentPastTag:t.multilineTagIndentPastTag}),d={},e=t&&t.tags,a=t&&t.scriptTypes;if(o(l,d),e&&o(e,d),a)for(var n=a.length-1;0<=n;n--)d.script.unshift(["type",a[n].matches,a[n].mode]);function p(t,e){var a,n=m.token(t,e.htmlState),l=/\btag\b/.test(n);if(l&&!/[<>\s\/]/.test(t.current())&&(a=e.htmlState.tagName&&e.htmlState.tagName.toLowerCase())&&d.hasOwnProperty(a))e.inTag=a+" ";else if(e.inTag&&l&&/>$/.test(t.current())){var r=/^([\S]+) (.*)/.exec(e.inTag);e.inTag=null;var o=">"==t.current()&&function(t,e){for(var a=0;a<t.length;a++){var n=t[a];if(!n[0]||n[1].test(g(e,n[0])))return n[2]}}(d[r[1]],r[2]),c=f.getMode(u,o),i=h(r[1],!0),s=h(r[1],!1);e.token=function(t,e){return t.match(i,!1)?(e.token=p,e.localState=e.localMode=null,null):(a=t,n=s,l=e.localMode.token(t,e.localState),r=a.current(),-1<(o=r.search(n))?a.backUp(r.length-o):r.match(/<\/?$/)&&(a.backUp(r.length),a.match(n,!1)||a.match(r)),l);var a,n,l,r,o},e.localMode=c,e.localState=f.startState(c,m.indent(e.htmlState,""))}else e.inTag&&(e.inTag+=t.current(),t.eol()&&(e.inTag+=" "));return n}return{startState:function(){return{token:p,inTag:null,localMode:null,localState:null,htmlState:f.startState(m)}},copyState:function(t){var e;return t.localState&&(e=f.copyState(t.localMode,t.localState)),{token:t.token,inTag:t.inTag,localMode:t.localMode,localState:e,htmlState:f.copyState(m,t.htmlState)}},token:function(t,e){return e.token(t,e)},indent:function(t,e,a){return!t.localMode||/^\s*<\//.test(e)?m.indent(t.htmlState,e):t.localMode.indent?t.localMode.indent(t.localState,e,a):f.Pass},innerMode:function(t){return{state:t.localState||t.htmlState,mode:t.localMode||m}}}},"xml","javascript","css"),f.defineMIME("text/html","htmlmixed")});