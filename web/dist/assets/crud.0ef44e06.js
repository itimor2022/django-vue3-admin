import{r as o,m as g,h as y,A as r,n as b,s as v}from"./index.acfe672b.js";import{d as l}from"./dictionary.d76d7a20.js";import{a}from"./authFunction.88002d4f.js";import{aD as x,m as u}from"./vue.5d8927be.js";import{M as _}from"./md5.b5efbca3.js";import{c as q}from"./commonCrud.a7c3bfac.js";const s="/api/system/user/";function k(t){return o({url:"/api/system/dept/dept_lazy_tree/",method:"get",params:t})}function R(t){return o({url:s,method:"get",params:t})}function S(t){return o({url:s,method:"post",data:t})}function c(t){return o({url:s+t.id+"/",method:"put",data:t})}function C(t){return o({url:s+t+"/",method:"delete",data:{id:t}})}function D(t){return g({url:s+"export_data/",params:t,method:"get"})}const O=function({crudExpose:t}){const d=async e=>await R(e),m=async({form:e,row:i})=>(e.id=i.id,await c(e)),p=async({row:e})=>await C(e.id),h=async({form:e})=>await S(e),f=async e=>await D(e),w=y(),{systemConfig:n}=x(w);return u(()=>(console.log(n.value),n.value)),{crudOptions:{table:{remove:{confirmMessage:"是否删除该用户？"}},request:{pageRequest:d,addRequest:h,editRequest:m,delRequest:p},form:{initialForm:{password:u(()=>n.value["base.default_password"])}},actionbar:{buttons:{add:{show:a("user:Create")},export:{text:"导出",title:"导出",click(){return f(t.getSearchFormData())}}}},rowHandle:{fixed:"right",width:200,buttons:{view:{show:!1},edit:{iconRight:"Edit",type:"text",show:a("user:Update")},remove:{iconRight:"Delete",type:"text",show:a("user:Delete")},custom:{text:"重设密码",type:"text",show:a("user:ResetPassword"),tooltip:{placement:"top",content:"重设密码"},click:e=>{}}}},columns:{_index:{title:"序号",form:{show:!1},column:{type:"index",align:"center",width:"70px",columnSetDisabled:!0}},username:{title:"账号",search:{show:!0},type:"input",column:{minWidth:100},form:{rules:[{required:!0,message:"账号必填项"}],component:{placeholder:"请输入账号"}}},password:{title:"密码",type:"password",column:{show:!1},editForm:{show:!1},form:{rules:[{required:!0,message:"密码必填项"}],component:{span:12,showPassword:!0,placeholder:"请输入密码"}},valueResolve({form:e}){e.password&&(e.password=_.hashStr(e.password))}},name:{title:"姓名",search:{show:!0},type:"input",column:{minWidth:100},form:{rules:[{required:!0,message:"姓名必填项"}],component:{span:12,placeholder:"请输入姓名"}}},dept:{title:"部门",search:{disabled:!0},type:"dict-tree",dict:r({isTree:!0,url:"/api/system/dept/all_dept/",value:"id",label:"name"}),column:{minWidth:150},form:{rules:[{required:!0,message:"必填项"}],component:{filterable:!0,placeholder:"请选择",props:{checkStrictly:!0,props:{value:"id",label:"name"}}}}},role:{title:"角色",search:{disabled:!0},type:"dict-select",dict:r({url:"/api/system/role/",value:"id",label:"name"}),column:{minWidth:100},form:{rules:[{required:!0,message:"必填项"}],component:{multiple:!0,filterable:!0,placeholder:"请选择角色"}}},mobile:{title:"手机号码",search:{show:!0},type:"input",column:{minWidth:120},form:{rules:[{max:20,message:"请输入正确的手机号码",trigger:"blur"},{pattern:/^1[3-9]\d{9}$/,message:"请输入正确的手机号码"}],component:{placeholder:"请输入手机号码"}}},email:{title:"邮箱",column:{width:260},form:{rules:[{type:"email",message:"请输入正确的邮箱地址",trigger:["blur","change"]}],component:{placeholder:"请输入邮箱"}}},gender:{title:"性别",type:"dict-select",dict:r({data:l("gender")}),form:{value:1,component:{span:12}},component:{props:{color:"auto"}}},user_type:{title:"用户类型",search:{show:!0},type:"dict-select",dict:r({data:l("user_type")}),column:{minWidth:100},form:{show:!1,value:0,component:{span:12}}},is_active:{title:"锁定",search:{show:!0},type:"dict-radio",column:{component:{name:"fs-dict-switch",activeText:"",inactiveText:"",style:"--el-switch-on-color: var(--el-color-primary); --el-switch-off-color: #dcdfe6",onChange:b(e=>()=>{c(e.row).then(i=>{v(i.msg)})})}},dict:r({data:l("button_status_bool")})},avatar:{title:"头像",type:"avatar-cropper",form:{show:!1},column:{minWidth:400}},...q({dept_belong_id:{form:!0,table:!0}})}}}},A=Object.freeze(Object.defineProperty({__proto__:null,createCrudOptions:O},Symbol.toStringTag,{value:"Module"}));export{k as G,A as a,O as c};