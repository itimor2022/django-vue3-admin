import{r as s,A as l,n as p,s as m}from"./index.acfe672b.js";import{d as h}from"./dictionary.d76d7a20.js";import{a as n}from"./authFunction.88002d4f.js";import"./vue.5d8927be.js";const o="/api/system/api_white_list/";function b(t){return s({url:o,method:"get",params:t})}function f(t){return s({url:o,method:"post",data:t})}function d(t){return s({url:o+t.id+"/",method:"put",data:t})}function w(t){return s({url:o+t+"/",method:"delete",data:{id:t}})}const O=function({crudExpose:t}){return{crudOptions:{request:{pageRequest:async e=>await b(e),addRequest:async({form:e})=>await f(e),editRequest:async({form:e,row:a})=>(e.id=a.id,await d(e)),delRequest:async({row:e})=>await w(e.id)},actionbar:{buttons:{add:{show:n("api_white_list:Create")}}},rowHandle:{fixed:"right",width:150,buttons:{view:{show:!1},edit:{iconRight:"Edit",type:"text",show:n("api_white_list:Update")},remove:{iconRight:"Delete",type:"text",show:n("api_white_list:Delete")}}},form:{col:{span:24},labelWidth:"110px",wrapper:{is:"el-dialog",width:"600px"}},columns:{_index:{title:"序号",form:{show:!1},column:{align:"center",width:"70px",columnSetDisabled:!0,formatter:e=>{let a=e.index??1,r=t.crudBinding.value.pagination;return((r.currentPage??1)-1)*r.pageSize+a+1}}},search:{title:"关键词",column:{show:!1},search:{show:!0,component:{props:{clearable:!0},placeholder:"请输入关键词"}},form:{show:!1,component:{props:{clearable:!0}}}},method:{title:"请求方式",sortable:"custom",search:{disabled:!1},type:"dict-select",dict:l({data:[{label:"GET",value:0},{label:"POST",value:1},{label:"PUT",value:2},{label:"DELETE",value:3},{label:"PATCH",value:4}]}),column:{minWidth:120},form:{rules:[{required:!0,message:"必填项"}],component:{span:12},itemProps:{class:{yxtInput:!0}}}},url:{title:"接口地址",sortable:"custom",search:{disabled:!0},type:"dict-select",dict:l({async getData(e){return s("/swagger.json").then(a=>{const r=Object.keys(a.paths),u=[];for(const c of r){const i={label:"",value:""};i.label=c,i.value=c,u.push(i)}return u})}}),column:{minWidth:200},form:{rules:[{required:!0,message:"必填项"}],component:{span:24,props:{elProps:{allowCreate:!0,filterable:!0,clearable:!0}}},itemProps:{class:{yxtInput:!0}},helper:{position:"label",tooltip:{placement:"top-start"},text:"请正确填写，以免请求时被拦截。匹配单例使用正则,例如:/api/xx/.*?/"}}},enable_datasource:{title:"数据权限认证",search:{disabled:!1},type:"dict-radio",column:{minWidth:120,component:{name:"fs-dict-switch",activeText:"",inactiveText:"",style:"--el-switch-on-color: var(--el-color-primary); --el-switch-off-color: #dcdfe6",onChange:p(e=>()=>{d(e.row).then(a=>{m(a.msg)})})}},dict:l({data:h("button_status_bool")})}}}}};export{O as createCrudOptions};