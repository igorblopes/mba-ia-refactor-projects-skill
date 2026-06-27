const { BadRequestError } = require('../errors');

// Valida e normaliza o corpo do checkout na fronteira (AP-13).
// Campos obrigatórios espelham o legado (usr, eml, c_id, card); a senha é opcional.
// Mantém a mensagem "Bad Request" para preservar o contrato externo.
function validateCheckout(body = {}) {
    const { usr: name, eml: email, pwd: password, c_id: courseId, card } = body;

    if (!name || !email || !courseId || !card) {
        throw new BadRequestError('Bad Request');
    }
    if (typeof email !== 'string' || !email.includes('@')) {
        throw new BadRequestError('Bad Request');
    }

    return {
        name: String(name),
        email: String(email),
        password: password ? String(password) : null,
        courseId: Number(courseId),
        card: String(card),
    };
}

module.exports = { validateCheckout };
