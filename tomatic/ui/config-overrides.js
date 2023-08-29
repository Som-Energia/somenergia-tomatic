const path = require('path')
const paths = require('react-scripts/config/paths')
const MiniCssExtractPlugin = require('mini-css-extract-plugin')
const rewireStylus = require('react-app-rewire-stylus-modules')
const multipleEntry = require('react-app-rewire-multiple-entry')([
  {
    entry: 'tomatic/ui/src/mithril/graella.js',
    template: 'tomatic/ui/src/mithril/tomatic.html',
    outPath: '/mithril.html',
    favicon: 'tomatic/ui/public/favicon.ico',
  },
])

module.exports = {
  webpack: function (config, env) {
    console.log('NODE_ENV:', process.env.NODE_ENV)
    console.log('webpack config before', config)
    const isdev = process.env.NODE_ENV == 'development'
    // Set the context to the path of this file
    config.context = path.resolve(__dirname)

    // Loader for yaml
    config.module.rules.push({
      test: /\.yaml$/,
      loader: 'yaml-loader',
    })
    // Loader for stylus
    config.module.rules.push({
      test: /\.styl$/,
      use: [MiniCssExtractPlugin.loader, 'css-loader', 'stylus-loader'],
    })
    // Add our entries
    multipleEntry.addMultiEntry(config)
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
    paths.appIndexJs = path.resolve(__dirname, 'src/admin.js')
    return paths
  },
}
