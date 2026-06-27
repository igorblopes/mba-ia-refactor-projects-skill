const sqlite3 = require('sqlite3');
const config = require('./config');

// Camada de conexão + helpers promisificados (AP-11, AP-16).
// `sqlite3.verbose()` NÃO é usado em produção; só ligamos verbose se DEBUG estiver setado.
const driver = process.env.DEBUG ? sqlite3.verbose() : sqlite3;

class Database {
    constructor(path = config.db.path) {
        this.connection = new driver.Database(path);
    }

    // Promisificações do driver baseado em callback.
    run(sql, params = []) {
        return new Promise((resolve, reject) => {
            this.connection.run(sql, params, function (err) {
                if (err) return reject(err);
                // `this` traz lastID e changes (contexto do sqlite3).
                resolve({ lastID: this.lastID, changes: this.changes });
            });
        });
    }

    get(sql, params = []) {
        return new Promise((resolve, reject) => {
            this.connection.get(sql, params, (err, row) => {
                if (err) return reject(err);
                resolve(row);
            });
        });
    }

    all(sql, params = []) {
        return new Promise((resolve, reject) => {
            this.connection.all(sql, params, (err, rows) => {
                if (err) return reject(err);
                resolve(rows);
            });
        });
    }

    // Executa um conjunto de escritas dentro de uma transação atômica (AP-17).
    async transaction(work) {
        await this.run('BEGIN');
        try {
            const result = await work();
            await this.run('COMMIT');
            return result;
        } catch (err) {
            await this.run('ROLLBACK');
            throw err;
        }
    }
}

module.exports = Database;
