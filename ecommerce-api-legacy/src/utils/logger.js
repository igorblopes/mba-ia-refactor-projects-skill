// Logger mínimo para substituir `console.log` espalhado (AP-20).
// Centraliza a saída e nunca deve receber segredos / dados sensíveis.
const logger = {
    info: (msg, meta) => console.log(`[INFO] ${msg}`, meta ?? ''),
    warn: (msg, meta) => console.warn(`[WARN] ${msg}`, meta ?? ''),
    error: (msg, meta) => console.error(`[ERROR] ${msg}`, meta ?? ''),
};

module.exports = logger;
