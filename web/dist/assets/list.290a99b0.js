import{a as _,ak as t,o,c as a,X as r,R as c,Q as l,F as v,aa as b,b as w,L as S,U as i}from"./vue.5d8927be.js";import{_ as h}from"./_plugin-vue_export-helper.c27b6911.js";const B={class:"icon-selector-warp-row"},I=_({name:"iconSelectorList"}),L=_({...I,props:{list:{type:Array,default:()=>[]},empty:{type:String,default:()=>"无相关图标"},prefix:{type:String,default:()=>""}},emits:["get-icon"],setup(e,{emit:m}){const d=e,p=m,u=s=>{p("get-icon",s)};return(s,N)=>{const f=t("SvgIcon"),g=t("el-col"),y=t("el-row"),k=t("el-empty"),x=t("el-scrollbar");return o(),a("div",B,[r(x,{ref:"selectorScrollbarRef"},{default:c(()=>[d.list.length>0?(o(),l(y,{key:0,gutter:10},{default:c(()=>[(o(!0),a(v,null,b(e.list,(n,C)=>(o(),l(g,{xs:6,sm:4,md:4,lg:4,xl:4,key:C,onClick:V=>u(n)},{default:c(()=>[w("div",{class:S(["icon-selector-warp-item",{"icon-selector-active":e.prefix===n}])},[r(f,{name:n},null,8,["name"])],2)]),_:2},1032,["onClick"]))),128))]),_:1})):i("",!0),e.list.length<=0?(o(),l(k,{key:1,"image-size":100,description:e.empty},null,8,["description"])):i("",!0)]),_:1},512)])}}});const R=h(L,[["__scopeId","data-v-2e4b32ad"]]);export{R as default};