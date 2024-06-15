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
                    confirmMessage: '是否删除该用户？',
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
                username: {
                    title: '账号',
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
                                message: '账号必填项',
                            },
                        ],
                        component: {
                            placeholder: '请输入账号',
                        },
                    },
                },
                password: {
                    title: '密码',
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
                                message: '密码必填项',
                            },
                        ],
                        component: {
                            placeholder: '请输入密码',
                        },
                    },
                },
                isp: {
                    title: '所属厂家',
                    search: {
                        disabled: false,
                    },
                    type: 'dict-tree',
                    dict: dict({
                        isTree: true,
                        url: '/api/asset/isp/',
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
                                message: '必填项所属厂家',
                            },
                        ],
                        component: {
                            filterable: true,
                            placeholder: '请选择所属厂家',
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
                use: {
                    title: '用处',
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
                                message: '必填项用处',
                            },
                        ],
                        component: {
                            placeholder: '请输入用处',
                        },
                    },
                },
                ...commonCrudConfig({
                })
            },
        },
    };
};
