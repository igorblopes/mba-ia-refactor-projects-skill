const config = require('../config');
const { UnauthorizedError } = require('../errors');
const logger = require('../utils/logger');

// Guard para endpoints administrativos/destrutivos (AP-05).
// Em produção, defina ADMIN_TOKEN e envie o header `x-admin-token`.
// Em dev (token não configurado) o acesso é liberado, com um aviso — assim o
// contrato externo padrão é preservado, mas o controle de acesso existe.
function requireAdmin(req, res, next) {
    if (!config.adminToken) {
        logger.warn('ADMIN_TOKEN não configurado — endpoint admin sem proteção (apenas dev).');
        return next();
    }
    if (req.get('x-admin-token') !== config.adminToken) {
        return next(new UnauthorizedError('Não autorizado'));
    }
    return next();
}

module.exports = { requireAdmin };
