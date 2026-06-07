import axios from 'axios';
import { ElMessage } from 'element-plus';
import type { Ref } from 'vue';
import { useRouter } from 'vue-router';

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 5000,
  withCredentials: true
});

// 获取路由实例
const router = useRouter();

// 请求拦截器：添加JWT令牌
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器：处理令牌过期
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      ElMessage.error('登录已过期，请重新登录');
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      router.push('/login');
    }
    return Promise.reject(error);
  }
);

// 封装获取数据的方法
export const fetchData = (
  url: string,
  dataRef: Ref<any>,
  errorMsg: string,
  params: any = {}
): Promise<boolean> => {
  return new Promise((resolve) => {
    api.get(url, { params })
      .then((res) => {
        dataRef.value = res.data;
        resolve(true);
      })
      .catch((err) => {
        console.error(errorMsg, err);
        ElMessage.error(errorMsg);
        resolve(false);
      });
  });
};


export const addQuestionBank = (
  url: string,
  requestData: any,
  errorMsg: string,
  refreshCallback: () => void
) => {
  api.post(url, requestData)
    .then(() => {
      ElMessage.success('题库添加成功');
      refreshCallback();
    })
    .catch((err) => {
      console.error('添加失败:', err);
      ElMessage.error(errorMsg);
    });
};

// 封装更新题目的方法（重点新增）
export const updateQuestionBank = async (
  url: string,
  dataRef: Ref<any>,
  requestData: any,
  errorMsg: string
): Promise<boolean> => {
  try {
    const response = await api.put(url, requestData);
    dataRef.value = response.data;
    ElMessage.success('数据更新成功');
    return true;
  } catch (err) {
    console.error(errorMsg, err);
    ElMessage.error(errorMsg);
    return false;
  }
};

// 封装删除方法
export const deleteData = async (url: string, errorMsg: string): Promise<boolean> => {
  try {
    await api.delete(url);
    return true;
  } catch (err) {
    console.error(errorMsg, err);
    ElMessage.error(errorMsg);
    return false;
  }
};

// 封装添加题目方法
export const addTopic = (
  url: string,
  requestData: any,
  errorMsg: string,
  refreshCallback: () => void
) => {
  api.post(url, requestData)
    .then(() => {
      ElMessage.success('题目添加成功');
      refreshCallback();
    })
    .catch((err) => {
      console.error('添加失败:', err);
      ElMessage.error(errorMsg);
    });
};

export const getTopicDetail = async (url: string, successCallback: (data: any) => void, errorCallback: (error: any) => void) => {
  try {
    const response = await api.get(url);
    successCallback(response.data);
  } catch (error) {
    console.error('获取题目详情失败:', error);
    errorCallback(error);
  }
};

export default {
  fetchData,
  updateQuestionBank,
  addQuestionBank,
  deleteData,
  addTopic,
  getTopicDetail,
};
