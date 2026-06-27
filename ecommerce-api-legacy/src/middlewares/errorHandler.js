const { AppError } = require('../errors');
const logger = require('../utils/logger');

// Tratamento de erros centralizado (AP-15). Erros de domínio (AppError) viram
// resposta com o status e a mensagem corretos; o resto vira 500 genérico (sem
// vazar internals — AP-06). Mantém corpo em texto para preservar o contrato legado.
function errorHandler(err, req, res, next) { // eslint-disable-line no-unused-vars
    if (err instanceof AppError) {
        return res.status(err.status).send(err.message);
    }
    logger.error('Erro não tratado', err);
    return res.status(500).send('Erro interno');
}

// Captura 404 de rotas inexistentes de forma consistente.
function notFoundHandler(req, res) {
    res.status(404).send('Recurso não encontrado');
}

module.exports = { errorHandler, notFoundHandler };
