module.exports = {
  plugins: [
    [
      'react-intl',
      {
        messagesDir: './front/i18n',
      },
    ],
  ],
  presets: [
    [
      '@babel/preset-env',
      {
        forceAllTransforms: true,
        useBuiltIns: 'usage',
      },
    ],
    'react',
  ],
};
