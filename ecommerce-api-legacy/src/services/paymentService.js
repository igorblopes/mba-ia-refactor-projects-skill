const { PAYMENT_STATUS, APPROVED_CARD_PREFIX } = require('../constants');
const logger = require('../utils/logger');

// Gateway de pagamento isolado atrás de um service (AP-10). O número do cartão e a
// chave do gateway NUNCA são logados (AP-02/AP-10): logamos apenas os 4 últimos dígitos.
class PaymentService {
    constructor(gatewayKey) {
        this.gatewayKey = gatewayKey;
    }

    // Decide aprovação do pagamento. Regra do gateway fake: cartão começa com "4".
    charge(card, amount) {
        const last4 = String(card).slice(-4);
        logger.info(`Processando pagamento de ${amount} (cartão final ${last4})`);
        return String(card).startsWith(APPROVED_CARD_PREFIX)
            ? PAYMENT_STATUS.PAID
            : PAYMENT_STATUS.DENIED;
    }
}

module.exports = PaymentService;
