module.exports = (config) => {
  config.set({
    frameworks: ['assert', 'mocha', 'riot'],
    // client: {
    //   useIframe: false,
    // },
    plugins: [
      'karma-babel-preprocessor',
      'karma-assert',
      'karma-coverage',
      'karma-mocha',
      'karma-mocha-reporter',
      'karma-chrome-launcher',
      'karma-phantomjs-launcher',
      'karma-riot',
    ],
    files: [
      'node_modules/babel-standalone/babel.js',
      'node_modules/riot/riot+compiler.js',
      'frontend/test/**/*.js',
      {
        pattern: 'frontend/src/**/*.tag',
        served: true,
        included: false,
      },
    ],
    preprocessors: {
      // 'frontend/src/**/*.tag': ['riot', 'coverage'],
      'frontend/test/**/*.js': ['babelSourceMap', 'coverage'],
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
    coverageReporter: {
      dir: 'coverage/',
      reporters: [
        // works correctly
        { type: 'html', subdir: 'report-html' },
        // does not work correctly -- gets its input from unprocessed
        // riot tag file
        { type: 'lcovonly', subdir: '.', file: 'lcov.info' },
      ],
    },

    browsers: [
      // 'PhantomJS',
      'Chrome',
      // Customized phantomjs is commented out, since it's only used for
      // local testing and debugging
      // 'PhantomJS_custom'
    ],
    reporters: ['mocha', 'coverage'],
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
