<forum-app>

  <h3>{ test }</h3>
  <test-tag/>

  <script type="babel">
  const type = 'mothafuckin JavaScript'
  this.test = `This is ${type} !`
  this.on('mount', () => {
    console.log('index run', this.tags)
  })
  </script>

</forum-app>

