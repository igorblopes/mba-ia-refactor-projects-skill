// Model de pagamentos — apenas acesso a dados.
class PaymentModel {
    constructor(db) {
        this.db = db;
    }

    create(enrollmentId, amount, status) {
        return this.db.run(
            'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
            [enrollmentId, amount, status]
        );
    }

    // Remove pagamentos de um conjunto de matrículas (usado no delete em cascata).
    deleteByEnrollmentIds(enrollmentIds) {
        if (!enrollmentIds.length) return Promise.resolve({ changes: 0 });
        const placeholders = enrollmentIds.map(() => '?').join(', ');
        return this.db.run(
            `DELETE FROM payments WHERE enrollment_id IN (${placeholders})`,
            enrollmentIds
        );
    }
}

module.exports = PaymentModel;
