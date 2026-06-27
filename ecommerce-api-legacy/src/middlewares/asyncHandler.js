// Encapsula handlers async para que erros lançados sejam repassados ao
// middleware central de erros (Express 4 não captura rejeições automaticamente).
const asyncHandler = (fn) => (req, res, next) => Promise.resolve(fn(req, res, next)).catch(next);

module.exports = asyncHandler;
