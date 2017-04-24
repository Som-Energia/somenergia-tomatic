const path = require('path');
const webpack = require('webpack');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const CleanWebpackPlugin = require('clean-webpack-plugin');
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;
const ExtractTextPlugin = require('extract-text-webpack-plugin');

var config = {
	context: path.resolve(__dirname, 'tomatic/static/'),
	entry: {
		main: './graella.js',
	},
	output: {
		path: path.resolve(__dirname, 'tomatic/dist'),
		filename: '[name]-bundle-[chunkhash].js',
		chunkFilename: '[id].chunk.js',
	},
	module: {
		rules: [
			{ test: /\.yaml$/,   loader: "yaml-loader" },
			{ test: /\.css$/,    use: ExtractTextPlugin.extract({use: "css-loader"})},
			{ test: /\.less$/,   use: ExtractTextPlugin.extract({use: "css-loader!less-loader"})},
			{ test: /\.styl$/,   use: ExtractTextPlugin.extract({use: "css-loader!stylus-loader"})},
			{ test: /\.jade$/,   loader: "jade-loader?self" },
			{ test: /\.png$/,    loader: "url-loader?prefix=img/&limit=5000" },
			{ test: /\.jpg$/,    loader: "url-loader?prefix=img/&limit=5000" },
			{ test: /\.gif$/,    loader: "url-loader?prefix=img/&limit=5000" },
			{ test: /\.woff$/,   loader: "file-loader?prefix=font/&limit=5000" },
			{ test: /\.eot$/,    loader: "file-loader?prefix=font/" },
			{ test: /\.ttf$/,    loader: "file-loader?prefix=font/" },
			{ test: /\.svg$/,    loader: "file-loader?prefix=font/" },
		]
	},
	plugins:[
		// Rewrites html to insert generated css and js
		new HtmlWebpackPlugin({template: './tomatic.html',inject:'header'}),
		// Uglifies JS
//		new webpack.optimize.UglifyJsPlugin(),
		// Analyzes generated sizes
//		new BundleAnalyzerPlugin({ analyzerMode: 'static' }),
		// Split vendor stuff from project's
		new webpack.optimize.CommonsChunkPlugin({
			name: "vendor",
			minChunks: function(module, num) {
				return /node_modules/.test(module.context);
			}
		}),
		// Extract webpack common stub from vendor and project
		new webpack.optimize.CommonsChunkPlugin({ name: "manifest", }),
		// Split css included as js into a separate file again
		new ExtractTextPlugin("styles-[chunkhash].css"),
		new CleanWebpackPlugin('tomatic/dist/*'),
	]
	
};

module.exports = config;

// vim: noet ts=4 sw=4
