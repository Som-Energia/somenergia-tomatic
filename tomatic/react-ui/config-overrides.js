const path = require('path')

const multipleEntry = require('react-app-rewire-multiple-entry')([
        {
                entry: 'src/admin.js',
                //template: 'public/index.html',
                outPath: '/admin.html',
        },
])

module.exports = {
        webpack: function (config, env) {
                console.log('NODE_ENV:', process.env.NODE_ENV)
                const isdev = process.env.NODE_ENV == 'development'
                multipleEntry.addMultiEntry(config)
                //console.log('pre config:', config)
                config.output.path = path.resolve(
                        __dirname,
                        isdev ? '../dist' : config.output.path
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
