const app = getApp()

Page({
  data: { placements: [], current: 0 },

  onLoad() {
    // 演示：茉莉花开头（MIDI），正式流程由识谱结果传入
    const notes = [45, 45, 48, 50, 53, 53, 50, 48].map((pitch) => ({ pitch, duration: 0.5 }))
    app.api('/api/arrange', { notes, level: 'beginner', style: 'guyun', auto_key: false })
      .then((res) => this.setData({ placements: res.placements }))
      .catch(() => wx.showToast({ title: '编配失败，请重试', icon: 'none' }))
  },

  pick(e) {
    this.setData({ current: e.currentTarget.dataset.i })
  }
})
