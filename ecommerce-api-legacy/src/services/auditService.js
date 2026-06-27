const logger = require('../utils/logger');

// Efeitos colaterais de auditoria/cache isolados (AP-10). O cache é estado da
// instância, injetado — não mais uma global mutável de módulo (AP-09).
class AuditService {
    constructor(db) {
        this.db = db;
        this.cache = new Map();
    }

    // Registra a ação na tabela de auditoria. Recebe a conexão para participar de
    // uma transação em curso quando chamado pelo controller.
    record(action) {
        return this.db.run(
            "INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))",
            [action]
        );
    }

    cacheLast(key, value) {
        logger.info(`Salvando no cache: ${key}`);
        this.cache.set(key, value);
    }
}

module.exports = AuditService;
