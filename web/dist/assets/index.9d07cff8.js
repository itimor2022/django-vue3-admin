import{u as _,L as t,e as i,_ as s}from"./index.acfe672b.js";import{a as u,aD as d,I as m,$ as c,o as f,Q as y,T as p,u as v,aA as a}from"./vue.5d8927be.js";const L=u({name:"layout"}),g=u({...L,setup(E){const l={defaults:a(()=>s(()=>import("./defaults.3de06f31.js"),["assets/defaults.3de06f31.js","assets/index.acfe672b.js","assets/vue.5d8927be.js","assets/index.5945f24a.css"])),classic:a(()=>s(()=>import("./classic.76b59f79.js"),["assets/classic.76b59f79.js","assets/index.acfe672b.js","assets/vue.5d8927be.js","assets/index.5945f24a.css"])),transverse:a(()=>s(()=>import("./transverse.1b11746e.js"),["assets/transverse.1b11746e.js","assets/index.acfe672b.js","assets/vue.5d8927be.js","assets/index.5945f24a.css"])),columns:a(()=>s(()=>import("./columns.b5f41540.js"),["assets/columns.b5f41540.js","assets/index.acfe672b.js","assets/vue.5d8927be.js","assets/index.5945f24a.css"]))},r=_(),{themeConfig:e}=d(r),n=()=>{t.get("oldLayout")||t.set("oldLayout",e.value.layout);const o=document.body.clientWidth;o<1e3?(e.value.isCollapse=!1,i.emit("layoutMobileResize",{layout:"defaults",clientWidth:o})):i.emit("layoutMobileResize",{layout:t.get("oldLayout")?t.get("oldLayout"):e.value.layout,clientWidth:o})};return m(()=>{n(),window.addEventListener("resize",n)}),c(()=>{window.removeEventListener("resize",n)}),(o,R)=>(f(),y(p(l[v(e).layout])))}});export{g as default};