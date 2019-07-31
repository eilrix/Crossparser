const path = require('path');
const webpack = require('webpack');
const nodeExternals = require('webpack-node-externals');

/*
 * SplitChunksPlugin is enabled by default and replaced
 * deprecated CommonsChunkPlugin. It automatically identifies modules which
 * should be splitted of chunk by heuristics using module duplication count and
 * module category (i. e. node_modules). And splits the chunks…
 *
 * It is safe to remove "splitChunks" from the generated configuration
 * and was added as an educational example.
 *
 * https://webpack.js.org/plugins/split-chunks-plugin/
 *
 */

const HtmlWebpackPlugin = require('html-webpack-plugin');

/*
 * We've enabled HtmlWebpackPlugin for you! This generates a html
 * page for you when you compile webpack, which will make you start
 * developing and prototyping faster.
 *
 * https://github.com/jantimon/html-webpack-plugin
 *
 */

module.exports = {
	//mode: 'development',
	mode: 'production',
	entry: './src/showmore.js',
	/*entry: './src/index.js',*/

	output: {
		filename: '[name].[chunkhash].js',
		path: path.resolve(__dirname, 'dist')
	},
	//watch:true,
	/*
	target: 'node',
    externals: [nodeExternals({
		whitelist: [/\.js/]
	})],*/

	plugins: [
		new webpack.ProgressPlugin(), 
		new HtmlWebpackPlugin({
			'template': './public/index.html'
		}),
		/*
		new webpack.ProvidePlugin({
            $: "jquery",
            jQuery: "jquery"
		}),*/
		//new webpack.SourceMapDevToolPlugin({})
	],

	module: {
		rules: [
			{
				test: /.(js|jsx)$/,
				include: [path.resolve(__dirname, 'src')],
				loader: 'babel-loader',

				options: {
					plugins: ['syntax-dynamic-import'],

					presets: [
						[
							'@babel/preset-env',
							{
								modules: false
							}
						]
					]
				}
			},
			/*{
				// Exposes jQuery for use outside Webpack build
				test: require.resolve('jquery'),
				use: [{
				  loader: 'expose-loader',
				  options: 'jQuery'
				},{
				  loader: 'expose-loader',
				  options: '$'
				}]
			},*/
			{
                test: /\.html$/,
                use: [
                  {
                    loader: "html-loader"
                  }
                ]
              },
              {
                test: /\.css$/i,
                use: ['style-loader', 'css-loader'],
              },
              {
                test: /\.svg$/,
                loader: 'svg-inline-loader'
              }
		]
	},

	optimization: {
		splitChunks: {
			cacheGroups: {
				vendors: {
					priority: -10,
					test: /[\\/]node_modules[\\/]/
				}
			},

			chunks: 'async',
			minChunks: 1,
			minSize: 30000,
			name: true
		}
	},

	devServer: {
		open: true
	}
};
