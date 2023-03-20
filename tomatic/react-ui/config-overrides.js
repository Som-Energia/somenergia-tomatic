const reactAppRewireBuildDev = require('react-app-rewire-build-dev')
const path = require('path')
const multipleEntry = require('react-app-rewire-multiple-entry')([
        {
                entry: 'src/admin.js',
                //template: 'public/index.html',
                outPath: '/admin.html',
        },
])

const options = {
        outputPath: 'output' /***** required *****/,
        basename: 'deploydir', // deploy react-app in a subdirectory /***** optional *****/
        //hotReloadPort : "<port of webpack-server>" // default:3000,simply relaod the webpage on changes./***** optional *****/
}

module.exports = {
        webpack: function (config, env) {
                console.log('NODE_ENV:', process.env.NODE_ENV)
                const isdev = process.env.NODE_ENV == 'development'
                multipleEntry.addMultiEntry(config)
                //console.log('pre config:', config)
                config.output.path = path.resolve(
                        __dirname,
                        config.output.path + (isdev ? '-dev' : '')
                )
                return reactAppRewireBuildDev(config, env, options)
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
