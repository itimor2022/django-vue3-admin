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


    return {
        crudOptions: {
            table: {
                remove: {
                    confirmMessage: '是否删除该主机？',
                },
            },
            request: {
                pageRequest,
                addRequest,
                editRequest,
                delRequest,
            },
            form: {
                initialForm: {}
            },
            actionbar: {
                buttons: {
                    add: {
                        show: auth('user:Create')
                    },
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
                hostname: {
                    title: '主机名称',
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
                                message: '主机名称必填项',
                            },
                        ],
                        component: {
                            placeholder: '请输入主机名称',
                        },
                    },
                },
                use: {
                    title: '用处',
                    search: {
                        show: false,
                    },
                    type: 'input',
                    column: {
                        minWidth: 100, //最小列宽
                    },
                },
                ip: {
                    title: '外网IP',
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
                                message: '外网IP必填项',
                            },
                        ],
                        component: {
                            placeholder: '请输入外网IP',
                        },
                    },
                },
                int_ip: {
                    title: '内网IP',
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
                                message: '内网IP必填项',
                            },
                        ],
                        component: {
                            placeholder: '请输入内网IP',
                        },
                    },
                },
                group: {
                    title: '所属分组',
                    search: {
                        disabled: false,
                    },
                    type: 'dict-tree',
                    dict: dict({
                        isTree: true,
                        url: '/api/project/appgroup/',
                        value: 'id',
                        label: 'name'
                    }),
                    column: {
                        minWidth: 150, //最小列宽
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
                account: {
                    title: '所属账号',
                    search: {
                        disabled: true,
                    },
                    type: 'dict-tree',
                    dict: dict({
                        isTree: true,
                        url: '/api/asset/account/',
                        value: 'id',
                        label: 'username'
                    }),
                    column: {
                        minWidth: 150, //最小列宽
                        show: false,
                    },
                    form: {
                        show: true,
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
                                    label: 'username',
                                },
                            },
                        },
                    },
                },
                os: {
                    title: '系统',
                    search: {
                        show: false,
                    },
                    type: 'dict-select',
                    dict: dict({
                        data: dictionary('os'),
                    }),
                    column: {
                        minWidth: 100, //最小列宽
                        show: false,
                    },
                    form: {
                        show: true,
                        value: 0,
                        component: {
                            span: 12,
                        },
                    },
                },
                status: {
                    title: '主机状态',
                    type: 'dict-select',
                    dict: dict({
                        data: dictionary('asset_status'),
                    }),
                    form: {
                        value: 0,
                        component: {
                            span: 12,
                        },
                    },
                },
                server_type: {
                    title: '类型',
                    search: {
                        show: false,
                    },
                    type: 'dict-select',
                    dict: dict({
                        data: dictionary('server_type'),
                    }),
                    column: {
                        minWidth: 100, //最小列宽
                        show: false,
                    },
                    form: {
                        show: true,
                        value: 2,
                        component: {
                            span: 12,
                        },
                    },
                },
                region: {
                    title: '区域',
                    search: {
                        show: true,
                    },
                    type: 'dict-select',
                    dict: dict({
                        data: dictionary('region'),
                    }),
                    column: {
                        minWidth: 100, //最小列宽
                    },
                    form: {
                        show: true,
                        value: 0,
                        component: {
                            span: 12,
                        },
                    },
                },
                instance_type: {
                    title: '配置',
                    search: {
                        show: false,
                    },
                    type: 'dict-select',
                    dict: dict({
                        data: dictionary('instance_type'),
                    }),
                    column: {
                        minWidth: 100, //最小列宽
                        show: false,
                    },
                    form: {
                        show: true,
                        value: 1,
                        component: {
                            span: 12,
                        },
                    },
                },
                ...commonCrudConfig({
                })
            },
        },
    };
};
