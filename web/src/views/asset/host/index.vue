<template>
  <fs-page>
    <el-row class="mx-2">
      <el-col xs="24" :sm="8" :md="6" :lg="4" :xl="4" class="p-1">
        <el-card :body-style="{ height: '100%' }">
          <p class="font-mono font-black text-center text-xl pb-5">
            主机分组
            <el-tooltip effect="dark" :content="content" placement="right">
              <el-icon>
                <QuestionFilled/>
              </el-icon>
            </el-tooltip>
          </p>
          <el-input v-model="filterText" :placeholder="placeholder"/>
          <el-tree ref="treeRef" class="font-mono font-bold leading-6 text-7xl" :data="data" :props="treeProps"
                   :filter-node-method="filterNode" icon="ArrowRightBold" :indent="38" highlight-current @node-click="onTreeNodeClick">
            <template #default="{ node, data }">
              <element-tree-line :node="node" :showLabelLine="false" :indent="32">
					<span v-if="data.status" class="text-center font-black font-normal">
						<SvgIcon name="iconfont icon-shouye" color="var(--el-color-primary)"/>&nbsp;{{ node.label }}
					</span>
                <span v-else color="var(--el-color-primary)"> <SvgIcon name="iconfont icon-shouye"/>&nbsp;{{
                    node.label
                  }} </span>
              </element-tree-line>
            </template>
          </el-tree>
        </el-card>
      </el-col>
      <el-col xs="24" :sm="16" :md="18" :lg="20" :xl="20" class="p-1">
        <el-card :body-style="{ height: '100%' }">
          <fs-crud ref="crudRef" v-bind="crudBinding">

          </fs-crud>
        </el-card>
      </el-col>
    </el-row>

  </fs-page>
</template>

<script lang="ts" setup name="user">
import {useExpose, useCrud} from '@fast-crud/fast-crud';
import {createCrudOptions} from './crud';
import * as api from './api';
import {ElTree} from 'element-plus';
import {ref, onMounted, watch, toRaw, h} from 'vue';
import XEUtils from 'xe-utils';
import {getElementLabelLine} from 'element-tree-line';

const ElementTreeLine = getElementLabelLine(h);

interface Tree {
  id: number;
  name: string;
  status: boolean;
  children?: Tree[];
}

interface APIResponseData {
  code?: number;
  data: [];
  msg?: string;
}

// 引入组件
const placeholder = ref('请输入分组名称');
const filterText = ref('');
const treeRef = ref<InstanceType<typeof ElTree>>();

const treeProps = {
  children: 'children',
  label: 'name',
  icon: 'icon',
};

watch(filterText, (val) => {
  treeRef.value!.filter(val);
});

const filterNode = (value: string, data: Tree) => {
  if (!value) return true;
  return toRaw(data).name.indexOf(value) !== -1;
};

let data = ref([]);

const content = `
1.分组信息;
`;

const getData = () => {
  api.GetDept({}).then((ret: APIResponseData) => {
    const responseData = ret.data;
    const result = XEUtils.toArrayTree(responseData, {
      parentKey: 'parent',
      children: 'children',
      strict: true,
    });

    data.value = result;
  });
};

//树形点击事件
const onTreeNodeClick = (node: any) => {
  const {id} = node;
  crudExpose.doSearch({form: {group: id}});
};

// 页面打开后获取列表数据
onMounted(() => {
  getData();
});

// crud组件的ref
const crudRef = ref();
// crud 配置的ref
const crudBinding = ref();
// 暴露的方法
const {crudExpose} = useExpose({crudRef, crudBinding});
// 你的crud配置
const {crudOptions} = createCrudOptions({crudExpose});
// 初始化crud配置
const {resetCrudOptions} = useCrud({crudExpose, crudOptions});

// 页面打开后获取列表数据
onMounted(() => {
  crudExpose.doRefresh();
});
</script>

<style lang="scss" scoped>
.el-row {
  height: 100%;

  .el-col {
    height: 100%;
  }
}

.el-card {
  height: 100%;
}

.font-normal {
  font-family: Helvetica Neue, Helvetica, PingFang SC, Hiragino Sans GB, Microsoft YaHei, SimSun, sans-serif;
}
</style>
