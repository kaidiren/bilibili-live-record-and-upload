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
      console.log(`[${moment().format('YYYY-MM-DD HH:mm:ss')}]`, '未开播等待中')
      await sleep(60000)
      return loop()
    }
    const urls = await rp({
      method: 'GET',
      uri: 'https://api.live.bilibili.com/api/playurl',
      qs: {
        cid: roomID,
        otype: 'json',
        quality: 0,
        platform: 'web'
      },
      json: true
    })
    const streamUri = urls.durl[0].url
    const filename = `${moment().format('YYYYMMDD_HHmm')}_${title}.flv`
    let date = moment()
    if (date.hour() <= 8) {
      date = date.subtract(1, 'day')
    }
    const dir = path.resolve(__dirname, '../files', date.format('YYYYMMDD'))
    mkdirp.sync(dir)
    const writeStream = fs.createWriteStream(path.resolve(dir, filename))

    const readStream = request.get(streamUri, {
      headers: {
        DNT: 1,
        Origin: 'https://live.bilibili.com',
        Referer: 'https://live.bilibili.com/404',
        'Sec-Fetch-Mode': 'cors',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'
      },
      timeout: 10000
    })

    readStream
      .on('response', function (response) {
        if (response.statusCode !== 200) {
          console.log(`[${moment().format('YYYY-MM-DD HH:mm:ss')}]`, '录制状态码非200', response.statusCode)
          readStream.end()
          return loop()
        }
      })
      .on('error', function (err) {
        console.log('Problem reaching URL: ', err)
        console.log(`[${moment().format('YYYY-MM-DD HH:mm:ss')}]`, '录制读取出错')
        readStream.destroy()
        return loop()
      })
      .pipe(writeStream)
      .on('finish', function (response) {
        writeStream.end()
        console.log(`[${moment().format('YYYY-MM-DD HH:mm:ss')}]`, '录制结束')
        return loop()
      })
      .on('error', function (err) {
        console.log('Problem writing file: ', err)
        console.log(`[${moment().format('YYYY-MM-DD HH:mm:ss')}]`, '录制写入出错')
        writeStream.destroy()
        return loop()
      })
  }
  await loop()
})()
