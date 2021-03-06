/* Auto-expand textarea when typing http://jsfiddle.net/hmelenok/WM6Gq/ */
Array.from(document.querySelectorAll('textarea')).forEach(textArea => {
  function resize() {
    textArea.style.height = 0 /* textarea is NOT resized when deleting or cutting content, to hack it, we tried 'auto' but it jumps when editing and saving so we had to fallback on '0' :-( */
    textArea.style.height = `${textArea.scrollHeight}px`
  }

  /* 0-timeout to get the already changed text */
  function delayedResize() {
    window.setTimeout(resize, 0)
  }

  textArea.addEventListener('change', resize, false)
  textArea.addEventListener('cut', delayedResize, false)
  textArea.addEventListener('paste', delayedResize, false)
  textArea.addEventListener('drop', delayedResize, false)
  textArea.addEventListener('keydown', delayedResize, false)

  resize()
})
