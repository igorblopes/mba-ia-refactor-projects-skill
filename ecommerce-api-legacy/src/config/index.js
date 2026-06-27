// Configuração centralizada — lida de variáveis de ambiente, com defaults de dev.
// Nenhum segredo real fica no código (AP-02). Forneça-os via ambiente / .env.
module.exports = {
    port: Number(process.env.PORT) || 3000,
    appName: process.env.APP_NAME || 'LMS API',

    // Banco de dados (SQLite em memória por padrão, como no boilerplate).
    db: {
        path: process.env.DB_PATH || ':memory:',
    },

    // Credenciais e segredos externos — devem vir do ambiente em produção.
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
    smtpUser: process.env.SMTP_USER || '',

    // Token para endpoints administrativos/destrutivos (AP-05). Quando vazio (dev),
    // o guard de admin libera o acesso; defina ADMIN_TOKEN em produção para exigir
    // o header `x-admin-token`.
    adminToken: process.env.ADMIN_TOKEN || '',
};
