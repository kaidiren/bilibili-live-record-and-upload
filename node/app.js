const rp = require('request-promise')
const sleep = require('sleep-promise')

;(async () => {
  let status = true
  while (status) {
    const data = await rp({
      method: 'GET',
      uri: 'https://space.bilibili.com/ajax/member/getSubmitVideos?mid=1859857&pagesize=1&tid=0&page=1&keyword=&order=pubdate',
      json: true
    })
    status = false
    const av = data.data.vlist[0]
    const { data: { pages } } = await rp({
      method: 'GET',
      uri: `https://api.bilibili.com/x/web-interface/view?aid=${av.aid}`,
      json: true
    })
    for (const page of pages) {
      console.log(page)
    }
  }
})()
