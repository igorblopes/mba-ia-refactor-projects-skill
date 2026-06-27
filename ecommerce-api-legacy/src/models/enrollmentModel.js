// Model de matrículas — apenas acesso a dados.
class EnrollmentModel {
    constructor(db) {
        this.db = db;
    }

    async create(userId, courseId) {
        const { lastID } = await this.db.run(
            'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
            [userId, courseId]
        );
        return lastID;
    }

    findIdsByUserId(userId) {
        return this.db.all('SELECT id FROM enrollments WHERE user_id = ?', [userId]);
    }

    deleteByUserId(userId) {
        return this.db.run('DELETE FROM enrollments WHERE user_id = ?', [userId]);
    }
}

module.exports = EnrollmentModel;
