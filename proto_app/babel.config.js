module.exports = {
  presets: [
    ["@babel/preset-env", {
      targets: { node: "current" },
      modules: "commonjs"  // Asegúrate de que Babel convierte módulos ES6 a CommonJS
    }],
    '@babel/preset-react'
  ],
  plugins: [
    '@babel/plugin-syntax-jsx'
  ]
};