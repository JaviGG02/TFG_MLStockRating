module.exports = {
  setupFilesAfterEnv: ["proto_app/jest.setup.js"], // Asegúrate de que la ruta sea correcta
  testEnvironment: "jsdom", // Esto es esencial para simular un entorno del navegador
};
