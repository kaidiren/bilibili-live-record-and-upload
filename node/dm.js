const { Room } = require('bilibili-live')
const moment = require('moment')
const shell = require('shelljs')
const fs = require('fs')

new Room({
  url: 404
}).connect().then(room => {
  room.on('danmaku.message', (msg) => {
    if (msg.type === 'comment') {
      const time = moment(new Date(msg.ts)).utcOffset(8).format('YYYY-MM-DD HH:mm:ss')
      const dm = '[' + time + ']' + msg.comment
      let date = moment().utcOffset(8).format('YYYYMMDD')
      if (moment().utcOffset(8).hour() <= 8) {
        date = moment().utcOffset(8).subtract(1, 'days').format('YYYYMMDD')
      }
      const dir = `files/${date}`
      const file = dir + '/dm.log'

      if (!fs.existsSync(dir)) {
        shell.mkdir('-p', dir)
      }
      shell.echo(dm).toEnd(file)
    }
  })
})
