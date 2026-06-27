const config = require('./config');
const createApp = require('./createApp');
const logger = require('./utils/logger');

// Ponto de entrada: monta a app e começa a escutar.
createApp()
    .then(({ app }) => {
        app.listen(config.port, () => {
            logger.info(`${config.appName} rodando na porta ${config.port}...`);
        });
    })
    .catch((err) => {
        logger.error('Falha ao iniciar a aplicação', err);
        process.exit(1);
    });
