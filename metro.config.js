const { getDefaultConfig } = require('expo/metro-config');

const config = getDefaultConfig(__dirname);

// Permite importar arquivos .bin (pesos do modelo TensorFlow.js)
config.resolver.assetExts.push('bin');

module.exports = config;
