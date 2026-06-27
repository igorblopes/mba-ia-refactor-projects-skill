const { hashPassword } = require('../utils/crypto');

// Criação de schema e carga de seeds. Fica fora dos models (que só fazem CRUD)
// e fora das rotas. Chamado uma vez pelo composition root no boot.
async function initSchema(db) {
    await db.run(`CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT,
        pass TEXT
    )`);
    await db.run(`CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY,
        title TEXT,
        price REAL,
        active INTEGER
    )`);
    await db.run(`CREATE TABLE IF NOT EXISTS enrollments (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        course_id INTEGER
    )`);
    await db.run(`CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY,
        enrollment_id INTEGER,
        amount REAL,
        status TEXT
    )`);
    await db.run(`CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY,
        action TEXT,
        created_at DATETIME
    )`);
}

async function seed(db) {
    // Senha do seed agora passa por hash real (AP-04) em vez de texto plano.
    const seededPass = await hashPassword('123');
    await db.run('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', [
        'Leonan',
        'leonan@fullcycle.com.br',
        seededPass,
    ]);
    await db.run(
        'INSERT INTO courses (title, price, active) VALUES (?, ?, ?), (?, ?, ?)',
        ['Clean Architecture', 997.0, 1, 'Docker', 497.0, 1]
    );
    await db.run('INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)', [1, 1]);
    await db.run(
        'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
        [1, 997.0, 'PAID']
    );
}

module.exports = { initSchema, seed };
