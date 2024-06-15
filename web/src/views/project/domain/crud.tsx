import * as api from './api';
import {
    dict,
    UserPageQuery,
    AddReq,
    DelReq,
    EditReq,
    compute,
    CreateCrudOptionsProps,
    CreateCrudOptionsRet
} from '@fast-crud/fast-crud';
import {request} from '/@/utils/service';
import {dictionary} from '/@/utils/dictionary';
import {successMessage} from '/@/utils/message';
import {auth} from '/@/utils/authFunction';
import {SystemConfigStore} from "/@/stores/systemConfig";
import {storeToRefs} from "pinia";
import {computed} from "vue";
import { Md5 } from 'ts-md5';
import {commonCrudConfig} from "/@/utils/commonCrud";
export const createCrudOptions = function ({crudExpose}: CreateCrudOptionsProps): CreateCrudOptionsRet {
    const pageRequest = async (query: UserPageQuery) => {
        return await api.GetList(query);
    };
    const editRequest = async ({form, row}: EditReq) => {
        form.id = row.id;
        return await api.UpdateObj(form);
    };
    const delRequest = async ({row}: DelReq) => {
        return await api.DelObj(row.id);
    };
    const addRequest = async ({form}: AddReq) => {
        return await api.AddObj(form);
    };

    const exportRequest = async (query: UserPageQuery) => {
        return await api.exportData(query)
    }

    const systemConfigStore = SystemConfigStore()
    const {systemConfig} = storeToRefs(systemConfigStore)
    const getSystemConfig = computed(() => {
        console.log(systemConfig.value)
        return systemConfig.value
    })


    // @ts-ignore
    return {
        crudOptions: {
            table: {
                remove: {
                    confirmMessage: '是否删除该域名？',
                },
            },
            request: {
                pageRequest,
                addRequest,
                editRequest,
                delRequest,
            },
            form: {
                initialForm: {
                    password: computed(() => {
                        return systemConfig.value['base.default_password']
                    }),
                }
            },
            actionbar: {
                buttons: {
                    add: {
                        show: auth('user:Create')
                    },
                    export: {
                        text: "导出",//按钮文字
                        title: "导出",//鼠标停留显示的信息
                        click() {
                            return exportRequest(crudExpose!.getSearchFormData())
                        }
                    }
                }
            },
            rowHandle: {
                //固定右侧
                fixed: 'right',
                width: 200,
                buttons: {
                    view: {
                        show: false,
                    },
                    edit: {
                        iconRight: 'Edit',
                        type: 'text',
                        show: auth('user:Update'),
                    },
                    remove: {
                        iconRight: 'Delete',
                        type: 'text',
                        show: auth('user:Delete'),
                    },
                },
            },
            columns: {
                _index: {
                    title: '序号',
                    form: {show: false},
                    column: {
                        type: 'index',
                        align: 'center',
                        width: '70px',
                        columnSetDisabled: true, //禁止在列设置中选择
                    },
                },
                search: {
					title: '关键词',
					column: {
						show: false,
					},
					search: {
						show: true,
						component: {
							props: {
								clearable: true,
							},
							placeholder: '请输入关键词',
						},
					},
					form: {
						show: false,
						component: {
							props: {
								clearable: true,
							},
						},
					},
				},
                domain: {
                    title: '域名',
                    search: {
                        show: false,
                    },
                    type: 'input',
                    column: {
                        minWidth: 100, //最小列宽
                    },
                    form: {
                        rules: [
                            // 表单校验规则
                            {
                                required: true,
                                message: '姓名必填项',
                            },
                        ],
                        component: {
                            span: 12,
                            placeholder: '请输入姓名',
                        },
                    },
                },
                group: {
                    title: '分组',
                    search: {
                        show: false,
                    },
                    type: 'dict-tree',
                    dict: dict({
                        isTree: true,
                        url: '/api/project/appgroup/',
                        value: 'id',
                        label: 'name'
                    }),
                    column: {
                        show: false,
                    },
                    form: {
                        rules: [
                            // 表单校验规则
                            {
                                required: true,
                                message: '必填项',
                            },
                        ],
                        component: {
                            filterable: true,
                            placeholder: '请选择',
                            props: {
                                checkStrictly:true,
                                props: {
                                    value: 'id',
                                    label: 'name',
                                },
                            },
                        },
                    },
                },
                type: {
                    title: '类型',
                    search: {
                        show: true,
                    },
                    type: 'dict-select',
                    dict: dict({
                        data: dictionary('domain_type'),
                    }),
                    form: {
                        value: 1,
                        component: {
                            span: 12,
                        },
                    },
                    component: {props: {color: 'auto'}}, // 自动染色
                },
                status: {
                    title: '锁定',
                    search: {
                        show: true,
                    },
                    type: 'dict-radio',
                    column: {
                        component: {
                            name: 'fs-dict-switch',
                            activeText: '',
                            inactiveText: '',
                            style: '--el-switch-on-color: var(--el-color-primary); --el-switch-off-color: #dcdfe6',
                            onChange: compute((context) => {
                                return () => {
                                    api.UpdateObj(context.row).then((res: APIResponseData) => {
                                        successMessage(res.msg as string);
                                    });
                                };
                            }),
                        },
                    },
                    dict: dict({
                        data: dictionary('button_status_bool'),
                    }),
                    form: {
                        value: true,
                        component: {
                            span: 12,
                        },
                    },
                },
                username: {
                    title: '账号',
                    search: {
                        show: false,
                    },
                    type: 'input',
                    column: {
                        show: false,
                    },
                    form: {
                        component: {
                            placeholder: '请输入账号',
                        },
                    },
                },
                password: {
                    title: '密码',
                    type: 'password',
                    column: {
                        show: false,
                    },
                    form: {
                        component: {
                            span: 12,
                            showPassword: true,
                            placeholder: '请输入密码',
                        },
                    },
                    valueResolve({form}) {
                        if (form.password) {
                            form.password = Md5.hashStr(form.password)
                        }
                    }
                },
                ...commonCrudConfig({
                })
            },
        },
    };
};
