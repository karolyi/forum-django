/* eslint global-require: "off", import/no-extraneous-dependencies: "off" */
// Include gulp
const gulp = require('gulp')
const gutil = require('gulp-util')
const webpackStream = require('webpack-stream')
const webpack = require('webpack')
const WebpackDevServer = require('webpack-dev-server')
const path = require('path')
const del = require('del')
// const htmlreplace = require('gulp-html-replace')
// const bundleHelper = require('./frontend/src/js/loader/bundlehelper')
const eslint = require('gulp-eslint')

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
gulp.task('lint', () => gulp.src(['frontend/src/**/*.js'])
  // eslint() attaches the lint output to the "eslint" property
  // of the file object so it can be used by other modules.
  .pipe(eslint())
  // eslint.format() outputs the lint results to the console.
  // Alternatively use eslint.formatEach() (see Docs).
  .pipe(eslint.format())
  // To have the process exit with an error code (1) on
  // lint error, return the stream and pipe to failAfterError last.
  .pipe(eslint.failAfterError()))

gulp.task('webpack-prod', ['lint'], () => gulp.src('')
  .pipe(webpackStream(require('./frontend/webpack/config.prod'), webpack))
  .pipe(gulp.dest('frontend/dist/assets/')))

gulp.task('webpack-dev', ['lint'], () => gulp.src('')
  .pipe(webpackStream(require('./frontend/webpack/config.dev'), webpack))
  .pipe(gulp.dest('frontend/dist/assets/')))

gulp.task('build', ['clean', 'webpack-prod'])
gulp.task('build-dev', ['clean', 'webpack-dev'])

gulp.task('webpack-dev-server', ['clean'], () => {
  const config = require('./frontend/webpack/config.dev-server')

  const compiler = webpack(config)
  const server = new WebpackDevServer(compiler, {
    hot: true,
    inline: true,
    historyApiFallback: true,
    contentBase: path.join(__dirname, 'frontend', 'src'),
    publicPath: '/static/assets/',
    stats: {
      colors: true,
    },
  })
  server.listen(3000, '0.0.0.0', (err) => {
    if (err) throw new gutil.PluginError('webpack-dev-server', err)
    // Server listening
    gutil.log('[webpack-dev-server]', 'http://localhost:3000/')
  })
})

gulp.task('default', ['clean', 'lint'], () => {
    // This will only run if the lint task is successful...
})
