const fs = require('fs')
const moment = require('moment')
const dir = './files/20190924/'
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
      let m = time - start
      if (m <= 0) {
        m = 1
      }
      console.log(Number(index) + 1, new Date(time * 1000), new Date(start * 1000), new Date(end * 1000), name, m, dm)
    }
  }
}
