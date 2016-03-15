module.exports = (config) => {
  config.set({
    frameworks: ['assert', 'mocha', 'riot'],
    plugins: [
      'karma-babel-preprocessor',
      'karma-assert',
      'karma-mocha',
      'karma-mocha-reporter',
      'karma-chrome-launcher',
      'karma-phantomjs-launcher',
      'karma-riot',
    ],
    files: [
      'frontend/src/**/*.tag',
      'frontend/test/**/*.js',
    ],
    preprocessors: {
      'frontend/src/**/*.tag': ['riot'],
      'frontend/test/**/*.js': ['babelSourceMap'],
    },
    customPreprocessors: {
      babelSourceMap: {
        base: 'babel',
        options: {
          presets: ['es2015'],
          sourceMap: 'inline',
        },
        filename: (file) => file.originalPath.replace(/\.js$/, '.es5.js'),
        sourceFileName: (file) => file.originalPath,
      },
      // Other custom preprocessors...
    },
    browsers: [
      // 'PhantomJS',
      'Chrome',
      // Customized phantomjs is commented out, since it's only used for
      // local testing and debugging
      // 'PhantomJS_custom'
    ],
    reporters: ['mocha'],
    riotPreprocessor: {
      options: {
        type: 'babel',
      },
    },
    // you can define custom flags
    customLaunchers: {
      PhantomJS_custom: {
        base: 'PhantomJS',
        options: {
          windowName: 'my-window',
          settings: {
            webSecurityEnabled: false,
          },
        },
        flags: ['--load-images=true'],
        debug: true,
      },
    },

    // phantomjsLauncher: {
    //   // Have phantomjs exit if a ResourceError is encountered (useful
    //   // if karma exits without killing phantom)
    //   exitOnResourceError: true,
    // },
  })
}
