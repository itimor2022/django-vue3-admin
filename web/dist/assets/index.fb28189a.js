import{a as ve,r as d,w as fe,m as he,a0 as ge,l as Ve,ak as c,o as n,Q as U,R as s,X as u,b as o,V as h,W as w,c as r,aa as g,a5 as X,S as q,Y as z,u as p,F as V,U as ke,H as N,aG as ye,aH as Ce}from"./vue.5d8927be.js";import{r as R,X as be,R as we,E as xe}from"./index.acfe672b.js";import{_ as Ue}from"./_plugin-vue_export-helper.c27b6911.js";function De(_){return R({url:"/api/system/role_menu_button_permission/get_role_premission/",method:"get",params:_})}function Pe(_,B){return R({url:`/api/system/role_menu_button_permission/${_}/set_role_premission/`,method:"put",data:B})}function Se(){return R({url:"/api/system/role_menu_button_permission/data_scope/",method:"get"})}function Ne(){return R({url:"/api/system/role_menu_button_permission/role_to_dept_all/",method:"get"})}const F=_=>(ye("data-v-f4c66c88"),_=_(),Ce(),_),Re={class:"permission-com"},Be={class:"pc-collapse-title"},Me={class:"pc-collapse-main"},Ee={class:"pccm-item"},Ie=F(()=>o("p",null,"允许对这些数据有以下操作",-1)),Te={class:"btn-item"},Xe=["onClick"],qe={key:0,class:"pccm-item"},ze=F(()=>o("p",null,"对这些数据有以下字段权限",-1)),Fe={class:"columns-list"},He={class:"columns-head"},$e=F(()=>o("div",{class:"width-txt"},[o("span",null,"字段")],-1)),Ae={class:"width-txt"},Ge={class:"pc-dialog"},Ke=ve({__name:"index",props:{roleId:{type:Number,default:-1},roleName:{type:String,default:""},drawerVisible:{type:Boolean,default:!1}},emits:["update:drawerVisible"],setup(_,{emit:B}){const D=_,K=B,M=d(!1);fe(()=>D.drawerVisible,t=>{M.value=t,Y(),j()});const L=()=>{K("update:drawerVisible",!1)},Q={children:"children",label:"name",value:"id"};let P=d([]),k=d(["1"]),H=d({}),$=d(-1),y=d(!1),S=d([]);const W=he(()=>function(t){const a=S.value.find(i=>i.value===t);return(a==null?void 0:a.label)||""});let A=d([]),m=d(),C=d([]);const Y=async()=>{const t=await De({role:D.roleId});P.value=t.data},j=async()=>{try{const t=await Se();(t==null?void 0:t.code)===2e3&&(S.value=t.data)}catch{return}},J=t=>{k.value=[t]},O=(t,a)=>{H.value=t,$.value=a,y.value=!0},Z=(t,a,i)=>{for(const b of a.columns)b[i]=t},ee=async t=>{if(t===4){const a=await Ne(),i=be.toArrayTree(a.data,{parentKey:"parent",strict:!1});A.value=i}},le=()=>{if(m.value!==0&&!m.value){we("请选择");return}for(const t of P.value)if(t.id===H.value.id){for(const a of t.btns)if(a.id===$.value){const i=S.value.find(b=>b.value===m.value);a.data_range=(i==null?void 0:i.value)||0,a.data_range===4&&(a.dept=C.value)}}E()},E=()=>{y.value=!1,C.value=[],m.value=null},ae=()=>{Pe(D.roleId,P.value).then(t=>{xe({message:t.msg,type:"success"})})},G=ge({header:[{value:"is_create",label:"新增可见"},{value:"is_update",label:"编辑可见"},{value:"is_query",label:"列表可见"}]});return Ve(()=>{}),(t,a)=>{const i=c("el-tag"),b=c("el-col"),I=c("el-button"),te=c("el-row"),x=c("el-checkbox"),oe=c("Setting"),se=c("el-icon"),ne=c("el-collapse-item"),ue=c("el-collapse"),ce=c("el-option"),ie=c("el-select"),re=c("el-tree-select"),de=c("el-dialog"),_e=c("el-drawer");return n(),U(_e,{modelValue:M.value,"onUpdate:modelValue":a[4]||(a[4]=e=>M.value=e),title:"权限配置",direction:"rtl",size:"60%","close-on-click-modal":!1,"before-close":L,"destroy-on-close":!0},{header:s(()=>[u(te,null,{default:s(()=>[u(b,{span:4},{default:s(()=>[o("div",null,[h("当前授权角色: "),u(i,null,{default:s(()=>[h(w(D.roleName),1)]),_:1})])]),_:1}),u(b,{span:6},{default:s(()=>[o("div",null,[u(I,{size:"small",type:"primary",class:"pc-save-btn",onClick:ae},{default:s(()=>[h("保存菜单授权 ")]),_:1})])]),_:1})]),_:1})]),default:s(()=>[o("div",Re,[u(ue,{modelValue:p(k),"onUpdate:modelValue":a[0]||(a[0]=e=>N(k)?k.value=e:k=e),onChange:J,accordion:""},{default:s(()=>[(n(!0),r(V,null,g(p(P),(e,T)=>(n(),U(ne,{key:T,name:T,style:{"background-color":"#fafafa"}},{title:s(()=>[o("div",null,[o("div",Be,[u(x,{modelValue:e.isCheck,"onUpdate:modelValue":l=>e.isCheck=l,onClick:X(l=>null,["stop"])},{default:s(()=>[o("span",null,w(e.name),1)]),_:2},1032,["modelValue","onUpdate:modelValue"])]),q(o("div",{onClick:X(l=>null,["stop"]),style:{"text-align":"left"}},[(n(!0),r(V,null,g(e.btns,l=>(n(),U(x,{key:l.value,label:l.value,modelValue:l.isCheck,"onUpdate:modelValue":v=>l.isCheck=v},{default:s(()=>[h(w(l.name),1)]),_:2},1032,["label","modelValue","onUpdate:modelValue"]))),128))],512),[[z,!p(k).includes(T)]])])]),default:s(()=>[o("div",Me,[o("div",Ee,[Ie,(n(!0),r(V,null,g(e.btns,(l,v)=>(n(),U(x,{key:v,modelValue:l.isCheck,"onUpdate:modelValue":f=>l.isCheck=f,label:l.value},{default:s(()=>[o("div",Te,[h(w(l.data_range!==null?`${l.name}(${W.value(l.data_range)})`:l.name)+" ",1),q(o("span",{onClick:X(f=>O(e,l.id),["stop","prevent"])},[u(se,null,{default:s(()=>[u(oe)]),_:1})],8,Xe),[[z,l.isCheck]])])]),_:2},1032,["modelValue","onUpdate:modelValue","label"]))),128))]),e.columns&&e.columns.length>0?(n(),r("div",qe,[ze,o("ul",Fe,[o("li",He,[$e,(n(!0),r(V,null,g(G.header,(l,v)=>(n(),r("div",{key:v,class:"width-check"},[u(x,{label:l.value,onChange:f=>Z(f,e,l.value)},{default:s(()=>[o("span",null,w(l.label),1)]),_:2},1032,["label","onChange"])]))),128))]),(n(!0),r(V,null,g(e.columns,(l,v)=>(n(),r("li",{key:v,class:"columns-item"},[o("div",Ae,w(l.title),1),(n(!0),r(V,null,g(G.header,(f,me)=>(n(),r("div",{key:me,class:"width-check"},[u(x,{modelValue:l[f.value],"onUpdate:modelValue":pe=>l[f.value]=pe,class:"ci-checkout"},null,8,["modelValue","onUpdate:modelValue"])]))),128))]))),128))])])):ke("",!0)])]),_:2},1032,["name"]))),128))]),_:1},8,["modelValue"]),u(de,{modelValue:p(y),"onUpdate:modelValue":a[3]||(a[3]=e=>N(y)?y.value=e:y=e),title:"数据权限配置",width:"400px","close-on-click-modal":!1,"before-close":E},{footer:s(()=>[o("div",null,[u(I,{type:"primary",onClick:le},{default:s(()=>[h(" 确定")]),_:1}),u(I,{onClick:E},{default:s(()=>[h(" 取消")]),_:1})])]),default:s(()=>[o("div",Ge,[u(ie,{modelValue:p(m),"onUpdate:modelValue":a[1]||(a[1]=e=>N(m)?m.value=e:m=e),onChange:ee,class:"dialog-select",placeholder:"请选择"},{default:s(()=>[(n(!0),r(V,null,g(p(S),e=>(n(),U(ce,{key:e.value,label:e.label,value:e.value},null,8,["label","value"]))),128))]),_:1},8,["modelValue"]),q(u(re,{"node-key":"id",modelValue:p(C),"onUpdate:modelValue":a[2]||(a[2]=e=>N(C)?C.value=e:C=e),props:Q,data:p(A),multiple:"","check-strictly":"","render-after-expand":!1,"show-checkbox":"",class:"dialog-tree"},null,8,["modelValue","data"]),[[z,p(m)===4]])])]),_:1},8,["modelValue"])])]),_:1},8,["modelValue"])}}});const Ye=Ue(Ke,[["__scopeId","data-v-f4c66c88"]]);export{Ye as default};