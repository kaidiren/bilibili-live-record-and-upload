const { Room } = require('bilibili-live')
const moment = require('moment')
const shell = require('shelljs')
const fs = require('fs')

new Room({
  url: 404
}).connect().then(room => {
  room.on('danmaku.message', (msg) => {
    if (msg.type === 'comment') {
      const time = moment(new Date(msg.ts)).format('YYYY-MM-DD HH:mm:ss')
      const dm = '[' + time + ']' + msg.comment
      let date = moment().format('YYYYMMDD')
      if (moment().hour() <= 8) {
        date = moment().subtract(1, 'days').format('YYYYMMDD')
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
