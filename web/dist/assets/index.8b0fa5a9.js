import{a6 as A,u as P,e as d,_ as r}from"./index.acfe672b.js";import{a as C,aD as p,aC as V,a0 as O,m as f,l as F,$ as M,o as _,c as U,Q as h,u as a,U as v,X as L,aA as i}from"./vue.5d8927be.js";import{_ as w}from"./_plugin-vue_export-helper.c27b6911.js";const H={class:"layout-navbars-breadcrumb-index"},N=C({name:"layoutBreadcrumbIndex"}),$=C({...N,setup(j){const y=i(()=>r(()=>import("./breadcrumb.87575cc7.js"),["assets/breadcrumb.87575cc7.js","assets/vue.5d8927be.js","assets/index.acfe672b.js","assets/index.5945f24a.css","assets/_plugin-vue_export-helper.c27b6911.js","assets/breadcrumb.cfed0c1a.css"])),R=i(()=>r(()=>import("./user.4d255317.js"),["assets/user.4d255317.js","assets/index.acfe672b.js","assets/vue.5d8927be.js","assets/index.5945f24a.css","assets/_plugin-vue_export-helper.c27b6911.js","assets/user.bff983e8.css"])),g=i(()=>r(()=>import("./index.9af0a583.js"),["assets/index.9af0a583.js","assets/vue.5d8927be.js","assets/index.acfe672b.js","assets/index.5945f24a.css","assets/lodash.b8574b89.js","assets/_plugin-vue_export-helper.c27b6911.js","assets/index.2bf81522.css"])),x=i(()=>r(()=>import("./horizontal.a5555b0e.js"),["assets/horizontal.a5555b0e.js","assets/index.acfe672b.js","assets/vue.5d8927be.js","assets/index.5945f24a.css","assets/_plugin-vue_export-helper.c27b6911.js","assets/horizontal.46032372.css"])),E=A(),I=P(),{themeConfig:c}=p(I),{routesList:u}=p(E),S=V(),l=O({menuList:[]}),b=f(()=>{let{isShowLogo:t,layout:e}=c.value;return t&&e==="classic"||t&&e==="transverse"}),T=f(()=>{let{layout:t,isClassicSplitMenu:e}=c.value;return t==="transverse"||e&&t==="classic"}),m=()=>{let{layout:t,isClassicSplitMenu:e}=c.value;if(t==="classic"&&e){l.menuList=B(o(u.value));const s=D(S.path);d.emit("setSendClassicChildren",s)}else l.menuList=o(u.value)},B=t=>(t.map(e=>{e.children&&delete e.children}),t),o=t=>t.filter(e=>{var s;return!((s=e.meta)!=null&&s.isHide)}).map(e=>(e=Object.assign({},e),e.children&&(e.children=o(e.children)),e)),D=t=>{const e=t.split("/");let s={children:[]};return o(u.value).map((n,k)=>{n.path===`/${e[1]}`&&(n.k=k,s.item={...n},s.children=[{...n}],n.children&&(s.children=n.children))}),s};return F(()=>{m(),d.on("getBreadcrumbIndexSetFilterRoutes",()=>{m()})}),M(()=>{d.off("getBreadcrumbIndexSetFilterRoutes",()=>{})}),(t,e)=>(_(),U("div",H,[b.value?(_(),h(a(g),{key:0})):v("",!0),L(a(y)),T.value?(_(),h(a(x),{key:1,menuList:l.menuList},null,8,["menuList"])):v("",!0),L(a(R))]))}});const q=w($,[["__scopeId","data-v-df58053c"]]);export{q as default};