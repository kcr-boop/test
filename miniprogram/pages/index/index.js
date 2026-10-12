Page({
  takePhoto() {
    wx.chooseMedia({ count: 1, mediaType: ['image'], sourceType: ['camera'], success: (r) => this.upload(r.tempFiles[0].tempFilePath) })
  },
  pickFromChat() {
    wx.chooseMessageFile({ count: 1, type: 'all', success: (r) => this.upload(r.tempFiles[0].path) })
  },
  pickFile() {
    wx.chooseMessageFile({ count: 1, type: 'file', extension: ['pdf', 'xml', 'musicxml', 'mxl', 'mid', 'midi'], success: (r) => this.upload(r.tempFiles[0].path) })
  },
  upload(path) {
    // TODO: 上传到云存储并创建识谱任务，轮询进度后进入识谱校对页
    wx.showToast({ title: '识谱功能开发中', icon: 'none' })
  }
})
