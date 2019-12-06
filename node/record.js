const rp = require('request-promise')
const request = require('request')
const moment = require('moment')
const sleep = require('sleep-promise')
const fs = require('fs')
const path = require('path')
const mkdirp = require('mkdirp')

const roomID = 12265
;(async () => {
  async function loop () {
    const room = await rp({
      method: 'GET',
      uri: 'https://api.live.bilibili.com/room/v1/Room/get_info',
      qs: {
        room_id: roomID
      },
      json: true,
      timeout: 5000
    })
    const open = room && room.data && room.data.live_status === 1
    const title = room && room.data && room.data.title
    if (!open) {
      console.log(`[${moment().format('YYYY-MM-DD HH:mm:ss')}]`, '等待中')
      await sleep(60000)
      return Promise.resolve()
    }
    const urls = await rp({
      method: 'GET',
      uri: 'https://api.live.bilibili.com/room/v1/Room/playUrl',
      qs: {
        cid: roomID,
        quality: 4,
        platform: 'web'
      },
      headers: {
        'cache-control': 'no-cache',
        Connection: 'keep-alive',
        Host: 'api.live.bilibili.com',
        'Cache-Control': 'no-cache',
        Accept: 'application/json',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'
      },
      json: true
    })
    const streamUri = urls.data.durl[0].url
    const filename = `${moment().format('YYYYMMDD_HHmmss')}_${title}.flv`
    let date = moment()
    if (date.hour() <= 8) {
      date = date.subtract(1, 'day')
    }
    const dir = path.resolve(__dirname, '../files', date.format('YYYYMMDD'))
    mkdirp.sync(dir)
    cleanSmallfiles(dir)
    const file = path.resolve(dir, filename)
    const writeStream = fs.createWriteStream(file)

    const readStream = request.get(streamUri, {
      headers: {
        DNT: 1,
        Origin: 'https://live.bilibili.com',
        Referer: 'https://live.bilibili.com/404',
        'Sec-Fetch-Mode': 'cors',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'
      },
      timeout: 30000
    })
    await save(readStream, writeStream)
  }
  while (true) {
    try {
      await loop()
    } catch (e) {
      console.log(e)
    }
  }
})()

function closeAll (r, w) {
  r.pause()
  w.cork()
  w.destroy()
  r.destroy()
}

function cleanSmallfiles (dir) {
  const files = fs.readdirSync(dir).filter(o => o.endsWith('.flv'))
  for (const file of files) {
    try {
      if (fs.statSync(path.resolve(dir, file)).size === 0) {
        fs.unlinkSync(path.resolve(dir, file))
      }
    } catch (e) {
      console.log(e)
    }
  }
}
async function save (readStream, writeStream) {
  console.log(`[${moment().format('YYYY-MM-DD HH:mm:ss')}]`, '录制开始')
  let downloaded = 0
  return new Promise((resolve, reject) => {
    readStream
      .on('data', function (chunk) {
        downloaded += chunk.length
        if (downloaded > 1024 * 1024 * 1024) {
          closeAll(readStream, writeStream)
          return resolve()
        }
      })
      .on('response', function (response) {
        if (response.statusCode !== 200) {
          console.log(`[${moment().format('YYYY-MM-DD HH:mm:ss')}]`, '录制状态码非200', response.statusCode)
          closeAll(readStream, writeStream)
          return resolve()
        }
      })
      .on('error', function () {
        console.log(`[${moment().format('YYYY-MM-DD HH:mm:ss')}]`, '录制结束')
        closeAll(readStream, writeStream)
        return resolve()
      })
      .pipe(writeStream)
      .on('finish', function (response) {
        closeAll(readStream, writeStream)
        console.log(`[${moment().format('YYYY-MM-DD HH:mm:ss')}]`, '录制结束')
        return resolve()
      })
      .on('error', function (err) {
        console.log('Problem writing file: ', err)
        console.log(`[${moment().format('YYYY-MM-DD HH:mm:ss')}]`, '录制写入出错')
        closeAll(readStream, writeStream)
        return resolve()
      })
  })
}

process.on('uncaughtException', function (err) {
  console.log(err)
  process.exit()
})

process.on('unhandledRejection', (reason, promise) => {
  console.log('Unhandled Rejection at:', promise, 'reason:', reason)
  process.exit()
})
