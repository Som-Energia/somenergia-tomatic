const path = require('path')
const MiniCssExtractPlugin = require('mini-css-extract-plugin')
const rewireStylus = require('react-app-rewire-stylus-modules')
const multipleEntry = require('react-app-rewire-multiple-entry')([
        {
                entry: 'src/mithril/graella.js',
                template: 'src/mithril/tomatic.html',
                outPath: '/index.html',
                favicon: 'src/mithril/favicon.ico',
        },
        {
                entry: 'src/admin.js',
                template: 'public/index.html',
                outPath: '/admin.html',
        },
])

module.exports = {
        webpack: function (config, env) {
                console.log('NODE_ENV:', process.env.NODE_ENV)
                console.log('webpack config before', config)
                const isdev = process.env.NODE_ENV == 'development'
                config.module.rules.push({
                        test: /\.yaml$/,
                        loader: 'yaml-loader',
                })
                config.module.rules.push({
                        test: /\.styl$/,
                        use: [
                                MiniCssExtractPlugin.loader,
                                'css-loader',
                                'stylus-loader',
                        ],
                })
                multipleEntry.addMultiEntry(config)
                config.output.path = path.resolve(
                        __dirname,
                        isdev ? '../dist' : config.output.path
                )
                config.plugins.shift() // remove the first htmlplugin
                config.plugins.push(
                        new MiniCssExtractPlugin({
                                filename: 'styles-[chunkhash].css',
                        })
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
}
