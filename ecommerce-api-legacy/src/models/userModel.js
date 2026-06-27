// Model de usuários — apenas acesso a dados. Recebe a conexão por injeção (AP-09).
class UserModel {
    constructor(db) {
        this.db = db;
    }

    findByEmail(email) {
        return this.db.get('SELECT * FROM users WHERE email = ?', [email]);
    }

    findById(id) {
        return this.db.get('SELECT * FROM users WHERE id = ?', [id]);
    }

    async create({ name, email, passHash }) {
        const { lastID } = await this.db.run(
            'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
            [name, email, passHash]
        );
        return lastID;
    }

    deleteById(id) {
        return this.db.run('DELETE FROM users WHERE id = ?', [id]);
    }
}

module.exports = UserModel;
