// Caso de uso de usuários. O delete agora cascateia matrículas e pagamentos
// numa única transação (AP-17) — chega de registros órfãos.
class UserController {
    constructor({ db, userModel, enrollmentModel, paymentModel }) {
        this.db = db;
        this.userModel = userModel;
        this.enrollmentModel = enrollmentModel;
        this.paymentModel = paymentModel;
    }

    async deleteUser(userId) {
        return this.db.transaction(async () => {
            const enrollments = await this.enrollmentModel.findIdsByUserId(userId);
            const enrollmentIds = enrollments.map((e) => e.id);

            await this.paymentModel.deleteByEnrollmentIds(enrollmentIds);
            await this.enrollmentModel.deleteByUserId(userId);
            await this.userModel.deleteById(userId);

            return { msg: 'Usuário deletado com sucesso (matrículas e pagamentos removidos).' };
        });
    }
}

module.exports = UserController;
