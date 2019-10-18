const fs = require('fs')
const rp = require('request-promise')
const moment = require('moment')

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
    const { aid, title, created } = av
    const date = title.substring(1, 9)
    const day = moment(new Date(created * 1000)).add(8, 'hour').subtract(1, 'day').format('YYYYMMDD')
    if (day !== date) {
      process.exit()
    }

    const { data: { pages } } = await rp({
      method: 'GET',
      uri: `https://api.bilibili.com/x/web-interface/view?aid=${av.aid}`,
      json: true
    })
    const cids = {}
    for (const page of pages) {
      cids[page.page] = page.cid
    }
    console.log(cids)

    const dir = `files/${date}/`
    const files = fs.readdirSync(dir).filter(o => o.endsWith('.bak'))
    const lines = fs.readFileSync(dir + 'dm.log').toString().split('\n').filter(o => Boolean(o))
    for (const [index, name] of Object.entries(files)) {
      const stat = fs.statSync(dir + name)
      const start = moment(stat.birthtime).add(8, 'hour').unix()
      const end = moment(stat.mtime).add(8, 'hour').unix()
      for (const line of lines) {
        const time = moment(line.substring(1, 20)).unix()
        if (time >= start && time < end) {
          const dm = line.substring(21)
          let t = time - start
          if (t <= 0) {
            t = 1
          }
          const page = Number(index) + 1
          console.log([page, aid, cids[page], t, dm].join(','))
        }
      }
    }
  }
})()
