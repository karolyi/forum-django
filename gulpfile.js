/* eslint global-require: "off", import/no-extraneous-dependencies: "off" */
// Include gulp
const gulp = require('gulp')
const PluginError = require('plugin-error')
const fancyLog = require('fancy-log')
const webpackStream = require('webpack-stream')
const webpack = require('webpack')
const WebpackDevServer = require('webpack-dev-server')
const path = require('path')
const del = require('del')
// const htmlreplace = require('gulp-html-replace')
// const bundleHelper = require('./frontend/src/js/loader/bundlehelper')
const eslint = require('gulp-eslint')

const sourceGlob = ['frontend/src/**/*.js']

// const htmlReplaceSkeleton = () =>
//   gulp.src('frontend/src/index.html')
//     .pipe(htmlreplace({
//       loader: {
//         src: null,
//         tpl: bundleHelper.createHeader(),
//       },
//     }))
//     .pipe(gulp.dest('frontend/dist/'))

// Cleanup task
gulp.task('clean', () => del(['./frontend/dist/**/*']))

// Lint Task
if (process.argv.length < 4) {
  gulp.task('lint', () => gulp.src(sourceGlob)
    // eslint() attaches the lint output to the "eslint" property
    // of the file object so it can be used by other modules.
    .pipe(eslint())
    // eslint.format() outputs the lint results to the console.
    // Alternatively use eslint.formatEach() (see Docs).
    .pipe(eslint.format())
    // To have the process exit with an error code (1) on
    // lint error, return the stream and pipe to failAfterError last.
    .pipe(eslint.failAfterError()))
} else if (process.argv[3] === '-n') {
  const passedFiles = process.argv[4].split('\n')
  gulp.task('lint', () => gulp.src(passedFiles)
    // eslint() attaches the lint output to the "eslint" property
    // of the file object so it can be used by other modules.
    .pipe(eslint())
    // eslint.format() outputs the lint results to the console.
    // Alternatively use eslint.formatEach() (see Docs).
    .pipe(eslint.format())
    // To have the process exit with an error code (1) on
    // lint error, return the stream and pipe to failAfterError last.
    .pipe(eslint.failAfterError()))
}

gulp.task('clean-lint', gulp.parallel(['clean', 'lint']))

gulp.task('webpack-prod', gulp.series('clean-lint', (done) => {
  gulp.src(sourceGlob)
    .pipe(webpackStream(require('./frontend/webpack/config.prod'), webpack))
    .pipe(gulp.dest('frontend/dist/assets/'))
  done()
}))

gulp.task('webpack-dev', gulp.series(['clean-lint'], (done) => {
  gulp.src(sourceGlob)
    .pipe(webpackStream(require('./frontend/webpack/config.dev'), webpack))
    .pipe(gulp.dest('frontend/dist/assets/'))
  done()
}))

gulp.task('build', gulp.series(['webpack-prod']))
gulp.task('build-dev', gulp.series(['clean', 'webpack-dev']))

gulp.task('webpack-dev-server', gulp.series(['clean'], (done) => {
  const config = require('./frontend/webpack/config.dev-server')

  const compiler = webpack(config)
  const server = new WebpackDevServer(compiler, {
    hot: true,
    inline: true,
    port: 3000,
    historyApiFallback: true,
    contentBase: path.join(__dirname, 'frontend', 'src'),
    publicPath: '/static/assets/',
    stats: {
      colors: true,
    },
    // https://github.com/webpack/webpack-dev-server/issues/533#issuecomment-296438189
    // FIXME: https://github.com/webpack/webpack-dev-server/issues/533#issuecomment-298202657
    // https://github.com/webpack/webpack-dev-server/issues/533#issuecomment-465222472
    disableHostCheck: true,
    headers: {
      'Access-Control-Allow-Origin': '*',
    },
  })
  server.listen(3000, '0.0.0.0', (err) => {
    if (err) throw new PluginError('webpack-dev-server', err)
    // Server listening
    fancyLog('[webpack-dev-server]', 'http://localhost:3000/')
  })
  done()
}))

gulp.task('default', gulp.series('clean-lint'))
