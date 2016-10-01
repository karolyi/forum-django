exports.insertScript = (source) => {
  const script = document.createElement('script')
  script.type = 'text/javascript'
  script.src = source
  script.charset = 'utf-8'
  script.async = true
  document.head.appendChild(script)
}

exports.insertStylesheet = (source) => {
  const stylesheet = document.createElement('link')
  stylesheet.setAttribute('rel', 'stylesheet')
  stylesheet.setAttribute('href', source)
  document.head.appendChild(stylesheet)
}

