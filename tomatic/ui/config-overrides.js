const path = require('path')
const paths = require('react-scripts/config/paths')
const MiniCssExtractPlugin = require('mini-css-extract-plugin')
const rewireStylus = require('react-app-rewire-stylus-modules')

module.exports = {
  webpack: function (config, env) {
    console.log('NODE_ENV:', process.env.NODE_ENV)
    console.log('webpack config before', config)
    const isdev = process.env.NODE_ENV == 'development'
    // Set the context to the path of this file
    config.context = path.resolve(__dirname)

    // Loader for yaml
    // Hack to exclude yaml from the asset/resource catchall rule
    config.module.rules[1].oneOf
      .filter((x) => x.test === undefined)
      .map((v) => {
        console.debug('RULE\n', v)
        v.exclude.push(/\.yaml/)
        console.debug('RULE\n', v)
      })
    config.module.rules.unshift({
      test: /\.yaml$/,
      loader: 'yaml-loader',
    })
    // Loader for stylus
    config.module.rules.push({
      test: /\.styl$/,
      use: [MiniCssExtractPlugin.loader, 'css-loader', 'stylus-loader'],
    })
    // Plugins per stylus
    config.plugins.push(
      new MiniCssExtractPlugin({
        filename: 'styles-[chunkhash].css',
      }),
    )
    return config
  },
  devServer: function (configFunction) {
    return function (proxy, allowedHost) {
      const config = configFunction(proxy, allowedHost)
      config.devMiddleware = {
        writeToDisk: true,
      }
      return config
    }
  },
  paths: function (paths, env) {
    paths.appPath = path.resolve(__dirname)
    paths.appSrc = path.resolve(__dirname, 'src')
    paths.appPublic = path.resolve(__dirname, 'public')
    paths.appHtml = path.resolve(__dirname, 'public/index.html')
    paths.appIndexJs = path.resolve(__dirname, 'src/index.js')
    return paths
  },
}
