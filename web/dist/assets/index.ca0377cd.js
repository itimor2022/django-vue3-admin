import{H as G,C as H}from"./index.acfe672b.js";import{G as I}from"./api.7d6ff680.js";import{_ as R}from"./addTabs.vue_vue_type_script_setup_true_lang.ac1e0ecb.js";import{_ as v}from"./addContent.vue_vue_type_script_setup_true_lang.1df8527a.js";import E from"./formContent.ddf8b01a.js";import{a as w,r as p,l as M,ak as o,o as r,Q as d,R as l,b as _,X as a,V as c,u,H as i,U as f,c as g,aa as Q,L as X,F as $}from"./vue.5d8927be.js";import"./associationTable.vue_vue_type_script_setup_true_lang.0a27a59b.js";import"./dictionary.d76d7a20.js";import"./_plugin-vue_export-helper.c27b6911.js";const j={class:"yxt-flex-between"},q={key:0,slot:"label"},A=w({name:"config"}),te=w({...A,setup(J){let n=p(!1),s=p(!1),m=p("base"),b=p([]);const x=()=>{I({limit:999,parent__isnull:!0}).then(y=>{let t=y.data;t.push({title:"无",icon:"el-icon-plus",key:"null"}),b.value=t})};return M(()=>{x()}),(y,t)=>{const C=o("el-tag"),V=o("el-button"),z=o("el-button-group"),T=o("el-header"),k=o("el-drawer"),B=o("el-col"),N=o("el-row"),U=o("el-tab-pane"),L=o("el-tabs"),D=o("el-card");return r(),d(D,null,{default:l(()=>[_("div",null,[a(T,null,{default:l(()=>[_("div",j,[_("div",null,[a(C,null,{default:l(()=>[c("系统配置:您可以对您的网站进行自定义配置")]),_:1})]),_("div",null,[a(z,null,{default:l(()=>[a(V,{type:"primary",size:"small",icon:u(G),onClick:t[0]||(t[0]=e=>i(n)?n.value=!0:n=!0)},{default:l(()=>[c(" 添加分组 ")]),_:1},8,["icon"]),a(V,{size:"small",type:"warning",icon:u(H),onClick:t[1]||(t[1]=e=>i(s)?s.value=!0:s=!0)},{default:l(()=>[c(" 添加内容 ")]),_:1},8,["icon"])]),_:1})])])]),_:1})]),_("div",null,[u(n)?(r(),d(k,{key:0,title:"添加分组",modelValue:u(n),"onUpdate:modelValue":t[2]||(t[2]=e=>i(n)?n.value=e:n=e),direction:"rtl",size:"30%"},{default:l(()=>[a(R)]),_:1},8,["modelValue"])):f("",!0)]),_("div",null,[u(s)?(r(),d(k,{key:0,title:"添加内容",modelValue:u(s),"onUpdate:modelValue":t[3]||(t[3]=e=>i(s)?s.value=e:s=e),direction:"rtl",size:"30%"},{default:l(()=>[a(v)]),_:1},8,["modelValue"])):f("",!0)]),a(L,{type:"border-card",modelValue:u(m),"onUpdate:modelValue":t[4]||(t[4]=e=>i(m)?m.value=e:m=e)},{default:l(()=>[(r(!0),g($,null,Q(u(b),(e,F)=>(r(),d(U,{key:F,label:e.title,name:e.key},{default:l(()=>[e.icon?(r(),g("span",q,[_("i",{class:X(e.icon),style:{"font-weight":"1000","font-size":"16px"}},null,2)])):f("",!0),e.icon?(r(),d(N,{key:1},{default:l(()=>[a(B,{offset:4,span:8},{default:l(()=>[a(v)]),_:1})]),_:1})):(r(),d(E,{key:2,options:e,editableTabsItem:e},null,8,["options","editableTabsItem"]))]),_:2},1032,["label","name"]))),128))]),_:1},8,["modelValue"])]),_:1})}}});export{te as default};