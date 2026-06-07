import { createStore } from 'vuex'
import authService from '@/services/authService'

export default createStore({
  state: {
    user: null,
    token: localStorage.getItem('access_token') || null,
    loading: false
  },
  mutations: {
    SET_USER(state, user) {
      state.user = user
    },
    SET_TOKEN(state, token) {
      state.token = token
      if (token) {
        localStorage.setItem('access_token', token)
      } else {
        localStorage.removeItem('access_token')
      }
    },
    SET_LOADING(state, loading) {
      state.loading = loading
    }
  },
  actions: {
    login({ commit }, { token, user }) {
      commit('SET_TOKEN', token)
      commit('SET_USER', user)
    },
    logout({ commit }) {
      // 调用认证服务的登出方法
      authService.logout()
      commit('SET_TOKEN', null)
      commit('SET_USER', null)
    },
    setLoading({ commit }, loading) {
      commit('SET_LOADING', loading)
    }
  },
  getters: {
    isAuthenticated: state => !!state.token,
    user: state => state.user,
    loading: state => state.loading,
    isTeacher: state => state.user && state.user.role === 'teacher'
  }
})