var path = require('path');
var webpack = require('webpack');
module.exports = {
    entry: [
        "webpack/hot/dev-server",
        path.resolve(__dirname, 'app/main.js')
    ],

    output: {
        path: path.resolve(__dirname, 'build'),
        filename: 'radio.production.min.js'
    },
    plugins: [
    new webpack.HotModuleReplacementPlugin({
        "process.env": { 
           NODE_ENV: JSON.stringify("production") 
         }
      })
    ],
    module: {
        loaders: [{
            test: /\.js$/,
            loaders: ['babel']
        }]
    }
};