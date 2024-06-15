import * as api from './api';
import { UserPageQuery, AddReq, DelReq, EditReq, CreateCrudOptionsProps, CreateCrudOptionsRet, dict } from '@fast-crud/fast-crud';
import {commonCrudConfig} from "/@/utils/commonCrud";
import {auth} from "/@/utils/authFunction";

export const createCrudOptions = function ({ crudExpose }: CreateCrudOptionsProps): CreateCrudOptionsRet {
	const pageRequest = async (query: UserPageQuery) => {
		return await api.GetList(query);
	};
	const editRequest = async ({ form, row }: EditReq) => {
		form.id = row.id;
		return await api.UpdateObj(form);
	};
	const delRequest = async ({ row }: DelReq) => {
		return await api.DelObj(row.id);
	};
	const addRequest = async ({ form }: AddReq) => {
		return await api.AddObj(form);
	};
	return {
		crudOptions: {
			request: {
				pageRequest,
				addRequest,
				editRequest,
				delRequest,
			},
			rowHandle: {
				fixed:'right',
				width: 300,
				buttons: {
					view: {
						show: false,
					},
					edit: {
						iconRight: 'Edit',
						type: 'text',
						show: auth('dictionary:Update'),
					},
					remove: {
						iconRight: 'Delete',
						type: 'text',
						show: auth('dictionary:Delete'),
					},
				},
			},
			columns: {
				_index: {
					title: '序号',
					form: { show: false },
					column: {
						//type: 'index',
						align: 'center',
						width: '70px',
						columnSetDisabled: true, //禁止在列设置中选择
						formatter: (context) => {
							//计算序号,你可以自定义计算规则，此处为翻页累加
							let index = context.index ?? 1;
							let pagination = crudExpose!.crudBinding.value.pagination;
							return ((pagination!.currentPage ?? 1) - 1) * pagination!.pageSize + index + 1;
						},
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
				name: {
					title: '名称',
					search: {
						disabled: false,
					},
					type: 'input',
					column:{
						minWidth: 120,
					},
					form: {
						disabled: true,
						component: {
							placeholder: '请输入名称',
						},
					},
				},
				key: {
					title: '关联字符',
					search: {
						disabled: false,
					},
					type: 'input',
					column:{
						minWidth: 120,
					},
					form: {
						disabled: true,
						component: {
							placeholder: '请输入关联字符',
						},
					},
				},
				...commonCrudConfig({
					create_datetime: {
						search: false
					}
				})
			},
		},
	};
};
