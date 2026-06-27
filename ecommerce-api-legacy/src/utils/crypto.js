const crypto = require('crypto');

// Hash de senha real com salt usando scrypt nativo (AP-04) — substitui o
// `badCrypto` (loop de base64 truncado). Sem dependências externas.
const KEY_LENGTH = 64;

function hashPassword(password) {
    return new Promise((resolve, reject) => {
        const salt = crypto.randomBytes(16).toString('hex');
        crypto.scrypt(password, salt, KEY_LENGTH, (err, derivedKey) => {
            if (err) return reject(err);
            resolve(`${salt}:${derivedKey.toString('hex')}`);
        });
    });
}

function verifyPassword(password, stored) {
    return new Promise((resolve, reject) => {
        const [salt, key] = String(stored).split(':');
        if (!salt || !key) return resolve(false);
        crypto.scrypt(password, salt, KEY_LENGTH, (err, derivedKey) => {
            if (err) return reject(err);
            const keyBuffer = Buffer.from(key, 'hex');
            resolve(
                keyBuffer.length === derivedKey.length &&
                    crypto.timingSafeEqual(keyBuffer, derivedKey)
            );
        });
    });
}

module.exports = { hashPassword, verifyPassword };
