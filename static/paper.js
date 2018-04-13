function highlight_string(string, color) {
  search = RegExp(string, 'gi')
  replace = (text) =>
    text.replace(search, m => 
      `<span style="background-color: ${color};" class="highlight">${m}</span>`)
  abstract = document.getElementById('abstract')
  abstract.innerHTML = replace(abstract.innerHTML)
  title = document.getElementById('title')
  title.innerHTML = replace(title.innerHTML)
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

  highlight_string('software', 'fuchsia')
  highlight_string('effort', 'yellow')
  highlight_string('estimat\\w+', 'chartreuse')
  highlight_string('poker', 'blueviolet')
  highlight_string('survey|mapping\\s+study|review', 'red')
})

