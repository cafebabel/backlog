/* Preloader slide up when page is loaded */
var imagesArray = [
  '/static/img/preloader-A.gif',
  '/static/img/preloader-B.gif',
  '/static/img/preloader-C.gif'
]
var preloader = document.getElementById('preloader-layer')

var num = Math.floor(Math.random() * imagesArray.length)
var preloaderImg = preloader.querySelector('img')
preloaderImg.src = imagesArray[num]
setTimeout(() => {
  preloader.classList.add('slideup')
}, 1200)
/* Preloader slide down when internal link is clicked */
Array.from(document.querySelectorAll('a')).forEach(a => {
  if (a.href.search(/\w+:\/\//) === 0 && a.hostname == location.hostname) {
    a.addEventListener('click', event => {
      event.preventDefault()
      preloader.classList.remove('slideup')
      preloader.classList.remove('hidden')
      preloader.classList.add('slidedown')
      var url = a.getAttribute('href')
      setTimeout(() => {
        window.location = url
      }, 600)
    })
  }
})