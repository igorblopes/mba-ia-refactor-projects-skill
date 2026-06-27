const { BadRequestError } = require('../errors');

// Valida o parâmetro de rota :id antes de tocar no banco (AP-13).
function validateUserId(rawId) {
    const id = Number(rawId);
    if (!Number.isInteger(id) || id <= 0) {
        throw new BadRequestError('ID de usuário inválido');
    }
    return id;
}

module.exports = { validateUserId };
