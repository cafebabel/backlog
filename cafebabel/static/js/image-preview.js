/* display picture file name after selection on profile edit https://tympanus.net/codrops/2015/09/15/styling-customizing-file-inputs-smart-way/ */
const fileInput = document.querySelector('.file input[type="file"]')
const outputImage = document.querySelector('.file output')
const sizeInfo = fileInput.parentElement.querySelector('.file small')
const canvasField = document.querySelector('.file canvas')

fileInput &&
  fileInput.addEventListener('change', event => {
    const image = event.target.files[0]
    const fileName = image.name
    const reader = new FileReader()
    reader.readAsDataURL(image)
    reader.addEventListener('loadend', () => {
      const maxSize = Math.round(reader.result.length / 1024) > 500
      if (!maxSize) {
        if (canvasField) canvasField.classList.add('hidden')
        // Keep quotes around img.src for jsmin.
        outputImage.innerHTML = `
    <figure>
      <img src="${reader.result}" alt="Picture preview">
      <figcaption>${fileName}</figcaption>
    </figure>
  `
      } else {
        sizeInfo.classList.add('oversized')
        fileInput.value = ''
      }
    })
  })

/* highlight file upload area on hover or dragenter */
function addListenerMulti(element, events, fn) {
  events
    .split(' ')
    .forEach(event =>
      element.addEventListener(event, fn, false)
    ) /* https://stackoverflow.com/questions/8796988/binding-multiple-events-to-a-listener-without-jquery */
}
if (canvasField) {
  addListenerMulti(fileInput, 'dragenter focus click', () => {
    canvasField.classList.add('active')
  })
  addListenerMulti(fileInput, 'dragleave blur drop', () => {
    canvasField.classList.remove('active')
  })
}
