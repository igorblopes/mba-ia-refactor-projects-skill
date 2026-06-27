const { NotFoundError, BadRequestError } = require('../errors');
const { PAYMENT_STATUS } = require('../constants');
const { hashPassword } = require('../utils/crypto');

// Caso de uso de checkout. Recebe entrada já validada (sem objetos req/res) e
// orquestra models + services. Fluxo achatado com async/await (AP-07, AP-11).
class CheckoutController {
    constructor({ db, userModel, courseModel, enrollmentModel, paymentModel, paymentService, auditService }) {
        this.db = db;
        this.userModel = userModel;
        this.courseModel = courseModel;
        this.enrollmentModel = enrollmentModel;
        this.paymentModel = paymentModel;
        this.paymentService = paymentService;
        this.auditService = auditService;
    }

    async checkout({ name, email, password, courseId, card }) {
        const course = await this.courseModel.findActiveById(courseId);
        if (!course) throw new NotFoundError('Curso não encontrado');

        // Decisão de pagamento antes de persistir qualquer coisa.
        const status = this.paymentService.charge(card, course.price);
        if (status === PAYMENT_STATUS.DENIED) {
            throw new BadRequestError('Pagamento recusado');
        }

        // Hash da senha fora da transação (operação custosa de CPU).
        const existingUser = await this.userModel.findByEmail(email);
        const passHash = existingUser ? null : await hashPassword(password || randomPassword());

        // Todas as escritas numa única transação atômica (AP-17).
        return this.db.transaction(async () => {
            const userId = existingUser
                ? existingUser.id
                : await this.userModel.create({ name, email, passHash });

            const enrollmentId = await this.enrollmentModel.create(userId, courseId);
            await this.paymentModel.create(enrollmentId, course.price, status);
            await this.auditService.record(`Checkout curso ${courseId} por ${userId}`);
            this.auditService.cacheLast(`last_checkout_${userId}`, course.title);

            return { msg: 'Sucesso', enrollment_id: enrollmentId };
        });
    }
}

// Senha aleatória quando o cliente não informa uma (substitui o default "123456").
function randomPassword() {
    return require('crypto').randomBytes(12).toString('hex');
}

module.exports = CheckoutController;
