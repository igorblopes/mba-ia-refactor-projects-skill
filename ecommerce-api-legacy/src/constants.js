// Constantes nomeadas no lugar de números/strings mágicos (AP-18).
module.exports = {
    PAYMENT_STATUS: {
        PAID: 'PAID',
        DENIED: 'DENIED',
    },
    // Regra do gateway fake: cartões que começam com "4" são aprovados.
    APPROVED_CARD_PREFIX: '4',
};
