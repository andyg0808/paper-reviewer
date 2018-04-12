function highlight_string(string) {
  abstract = document.getElementById('abstract')
  text = abstract.innerHTML
  abstract.innerHTML = text.replace(string, m => `<span class="highlight">${m}</span>`)
}

$(() => {
  document.addEventListener('keypress', (event) => {
    if (event.key == 'i') {
      document.getElementById('include').click()
    }
    if (event.key == 'e') {
      document.getElementById('exclude').click()
    }
    if (event.key == 'd') {
      document.getElementById('discuss').click()
    }
    if (event.key == 'f') {
      document.getElementById('freeform-text').focus()
    }
  })

  freeform_text = document.getElementById('freeform-text')
  freeform_text.addEventListener('keypress', (event) => {
    event.stopPropagation()
  })

  freeform_text.addEventListener('keydown', (event) => {
    if (event.key == 'Enter') {
      document.getElementById('freeform').click()
      event.preventDefault()
    }
  })

  highlight_string('effort')
})

