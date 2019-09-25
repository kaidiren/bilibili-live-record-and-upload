const fs = require('fs')
const moment = require('moment')
const files = fs.readdirSync('./files/20190924').filter(o => o.endsWith('.flv')).slice(4, 5)
console.log(files)
const lines = fs.readFileSync('./files/20190924/dm.log').toString().split('\n').filter(o => Boolean(o))
for (const [index, name] of Object.entries(files)) {
  console.log(Number(index) + 1, name)
  const stat = fs.statSync(name)
  const start = moment(stat.birthtime).utcOffset(8)
  const end = moment(stat.mtime).utcOffset(8)
  for (const line of lines) {
    const time = moment(line.substring(1, 20)).utcOffset(8)
    console.log(time, start, end, time >= start, time < end)
    if (time >= start && time < end) {
      const dm = line.substring(21)
      let m = time - start
      m = Math.floor(m / 1000)
      if (!m) {
        m = 1
      }
      console.log(index, m, dm)
    }
  }
}
