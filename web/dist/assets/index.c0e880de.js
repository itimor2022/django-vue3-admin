import{w as A,D as F,k as G,X as P}from"./index.acfe672b.js";import{c as z,G as K}from"./crud.4d883a09.js";import{g as M}from"./index.es.d2375c1e.js";import{a as V,r as l,w as W,l as v,ak as t,o as r,Q as b,R as o,X as e,b as q,V as _,u as p,c as w,U as H,W as R,O as J,aj as Y,ag as Z}from"./vue.5d8927be.js";import{_ as $}from"./_plugin-vue_export-helper.c27b6911.js";import"./authFunction.88002d4f.js";import"./commonCrud.a7c3bfac.js";const ee={class:"font-mono font-black text-center text-xl pb-5"},te={key:0,class:"text-center font-black font-normal"},oe={key:1,color:"var(--el-color-primary)"},ne=V({name:"user"}),ae=V({...ne,setup(le){const C=M(Y),N=l("请输入分组名称"),d=l(""),u=l(),B={children:"children",label:"name",icon:"icon"};W(d,n=>{u.value.filter(n)});const D=(n,a)=>n?Z(a).name.indexOf(n)!==-1:!0;let f=l([]);const E=`
1.分组信息;
`,T=()=>{K({}).then(n=>{const a=n.data,i=P.toArrayTree(a,{parentKey:"parent",children:"children",strict:!0});f.value=i})},L=n=>{const{id:a}=n;c.doSearch({form:{group:a}})};v(()=>{T()});const m=l(),h=l(),{crudExpose:c}=A({crudRef:m,crudBinding:h}),{crudOptions:O}=z({crudExpose:c});return F({crudExpose:c,crudOptions:O}),v(()=>{c.doRefresh()}),(n,a)=>{const i=t("QuestionFilled"),S=t("el-icon"),I=t("el-tooltip"),Q=t("el-input"),g=t("SvgIcon"),x=t("el-card"),y=t("el-col"),U=t("fs-crud"),X=t("el-row"),j=t("fs-page");return r(),b(j,null,{default:o(()=>[e(X,{class:"mx-2"},{default:o(()=>[e(y,{xs:"24",sm:8,md:6,lg:4,xl:4,class:"p-1"},{default:o(()=>[e(x,{"body-style":{height:"100%"}},{default:o(()=>[q("p",ee,[_(" 项目分组 "),e(I,{effect:"dark",content:E,placement:"right"},{default:o(()=>[e(S,null,{default:o(()=>[e(i)]),_:1})]),_:1})]),e(Q,{modelValue:d.value,"onUpdate:modelValue":a[0]||(a[0]=s=>d.value=s),placeholder:N.value},null,8,["modelValue","placeholder"]),e(p(G),{ref_key:"treeRef",ref:u,class:"font-mono font-bold leading-6 text-7xl",data:p(f),props:B,"filter-node-method":D,icon:"ArrowRightBold",indent:38,"highlight-current":"",onNodeClick:L},{default:o(({node:s,data:k})=>[e(p(C),{node:s,showLabelLine:!1,indent:32},{default:o(()=>[k.status?(r(),w("span",te,[k.parent?(r(),b(g,{key:0,name:"iconfont icon-zujian",color:"var(--el-color-primary)"})):H("",!0),_(" "+R(s.label),1)])):(r(),w("span",oe,[e(g,{name:"iconfont icon-shouye"}),_(" "+R(s.label),1)]))]),_:2},1032,["node"])]),_:1},8,["data"])]),_:1})]),_:1}),e(y,{xs:"24",sm:16,md:18,lg:20,xl:20,class:"p-1"},{default:o(()=>[e(x,{"body-style":{height:"100%"}},{default:o(()=>[e(U,J({ref_key:"crudRef",ref:m},h.value),null,16)]),_:1})]),_:1})]),_:1})]),_:1})}}});const ue=$(ae,[["__scopeId","data-v-9271904c"]]);export{ue as default};