const express = require('express');
const config = require('./config');
const Database = require('./db');
const { initSchema, seed } = require('./database/schema');

const UserModel = require('./models/userModel');
const CourseModel = require('./models/courseModel');
const EnrollmentModel = require('./models/enrollmentModel');
const PaymentModel = require('./models/paymentModel');
const ReportModel = require('./models/reportModel');

const PaymentService = require('./services/paymentService');
const AuditService = require('./services/auditService');

const CheckoutController = require('./controllers/checkoutController');
const ReportController = require('./controllers/reportController');
const UserController = require('./controllers/userController');

const buildRouter = require('./routes');
const { errorHandler, notFoundHandler } = require('./middlewares/errorHandler');

// Composition root: conecta config -> db -> models -> services -> controllers -> rotas.
// Único lugar que conhece a fiação completa. Retorna a app pronta para escutar/testar.
async function createApp() {
    const db = new Database();
    await db.transaction(async () => {
        await initSchema(db);
        await seed(db);
    });

    // Models (recebem a conexão por injeção).
    const userModel = new UserModel(db);
    const courseModel = new CourseModel(db);
    const enrollmentModel = new EnrollmentModel(db);
    const paymentModel = new PaymentModel(db);
    const reportModel = new ReportModel(db);

    // Services.
    const paymentService = new PaymentService(config.paymentGatewayKey);
    const auditService = new AuditService(db);

    // Controllers.
    const checkoutController = new CheckoutController({
        db, userModel, courseModel, enrollmentModel, paymentModel, paymentService, auditService,
    });
    const reportController = new ReportController({ reportModel });
    const userController = new UserController({ db, userModel, enrollmentModel, paymentModel });

    const app = express();
    app.use(express.json());
    app.use(buildRouter({ checkoutController, reportController, userController }));
    app.use(notFoundHandler);
    app.use(errorHandler);

    return { app, db };
}

module.exports = createApp;
