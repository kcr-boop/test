// 云托管环境 ID 与服务名在部署后填写
const CLOUD_ENV = '[YOUR_CLOUD_ENV_ID]'
const API_SERVICE = 'qinyi-api'

App({
  globalData: { cloudEnv: CLOUD_ENV, apiService: API_SERVICE },

  onLaunch() {
    wx.cloud.init({ env: CLOUD_ENV })
  },

  // 调用微信云托管上的 API；返回 Promise
  api(path, data, method = 'POST') {
    return new Promise((resolve, reject) => {
      wx.cloud.callContainer({
        config: { env: this.globalData.cloudEnv },
        path,
        method,
        data,
        header: { 'X-WX-SERVICE': API_SERVICE, 'content-type': 'application/json' },
        success: (res) => (res.statusCode === 200 ? resolve(res.data) : reject(res)),
        fail: reject
      })
    })
  }
})
