// Erros de domínio com status HTTP associado. Controllers/models lançam estes;
// o middleware central de erros os traduz numa resposta (AP-15).
class AppError extends Error {
    constructor(message, status = 400) {
        super(message);
        this.name = 'AppError';
        this.status = status;
    }
}

class BadRequestError extends AppError {
    constructor(message = 'Bad Request') {
        super(message, 400);
    }
}

class NotFoundError extends AppError {
    constructor(message = 'Não encontrado') {
        super(message, 404);
    }
}

class UnauthorizedError extends AppError {
    constructor(message = 'Não autorizado') {
        super(message, 401);
    }
}

module.exports = { AppError, BadRequestError, NotFoundError, UnauthorizedError };
