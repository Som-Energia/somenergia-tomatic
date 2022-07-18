const path = require('path');
const webpack = require('webpack');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const CleanWebpackPlugin = require('clean-webpack-plugin');
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;
const MiniCssExtractPlugin = require("mini-css-extract-plugin");



var config = {
	context: path.resolve(__dirname, 'tomatic/ui/'),
	entry: {
		main: './graella.js',
	},
	resolve: {
		fallback: {
			buffer: require.resolve('buffer'),
		},
	},
	output: {
		path: path.resolve(__dirname, 'tomatic/dist'),
		filename: '[name]-bundle-[contenthash].js',
		chunkFilename: '[id].chunk.js',
	},
	optimization: {
		splitChunks: {
			cacheGroups: {
				vendor: {
					name: 'vendor',
					chunks: 'all',
					test: /[\\/]node_modules[\\/]/,
				},
			},
		},
	},
	module: {
		rules: [
			{ test: /\.js$/, use: [ {loader: 'babel-loader' }]},
			{ test: /\.yaml$/,  loader: "yaml-loader" },
			{ test: /\.css$/,   use: [MiniCssExtractPlugin.loader, "css-loader"]},
			{ test: /\.less$/,  use: [MiniCssExtractPlugin.loader, "css-loader", "less-loader"]},
			{ test: /\.styl$/,  use: [MiniCssExtractPlugin.loader, "css-loader", "stylus-loader"]},
			{ test: /\.(gif|jpg|png)$/, type: "asset", generator: {
				filename: "[name]-[hash][ext]"
			}},
			{ test: /\.(woff|eot|ttf|svg)$/, type: "asset", generator: {
				filename: "font/[name][ext]"
			}},
		]
	},
	plugins:[
		// Rewrites html to insert generated css and js
		new HtmlWebpackPlugin({
			template: './tomatic.html',
			favicon: './favicon.ico',
			inject: 'head',
		}),
		/*
		// Analyzes generated sizes
		new BundleAnalyzerPlugin({ analyzerMode: 'static' }),
		*/
		new CleanWebpackPlugin('tomatic/dist/*'),
		// Split css included as js into a separate file again
		new MiniCssExtractPlugin({
			filename: "styles-[chunkhash].css"
		}),
	]
	
};

module.exports = config;

// vim: noet ts=4 sw=4
