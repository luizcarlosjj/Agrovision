module.exports = function (api) {
  api.cache(true);
  return {
    presets: ['babel-preset-expo'],
    plugins: [
      [
        'module-resolver',
        {
          alias: {
            '@': './src',
            '@components': './src/components',
            '@screens': './src/screens',
            '@services': './src/services',
            '@hooks': './src/hooks',
            '@models': './src/models',
            '@utils': './src/utils',
            '@context': './src/context',
            '@navigation': './src/navigation',
            '@styles': './src/styles',
            '@assets': './assets',
            '@data': './src/data',
          },
        },
      ],
    ],
  };
};
