const multipleEntry = require('react-app-rewire-multiple-entry')([
        {
                entry: 'src/index.js',
                template: 'public/index.html',
                outPath: '/admin.html',
        },
])

module.exports = {
        webpack: function (config, env) {
                multipleEntry.addMultiEntry(config)
                return config
        },
}
