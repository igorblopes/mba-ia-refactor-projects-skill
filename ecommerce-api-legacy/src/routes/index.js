const express = require('express');
const asyncHandler = require('../middlewares/asyncHandler');
const { requireAdmin } = require('../middlewares/auth');
const { validateCheckout } = require('../validators/checkoutValidator');
const { validateUserId } = require('../validators/userValidator');

// Camada HTTP fina (views): mapeia URL+método -> controller, parseia entrada e
// molda a resposta. Sem SQL e sem regra de negócio aqui. URLs/métodos/respostas
// preservados em relação ao legado.
function buildRouter({ checkoutController, reportController, userController }) {
    const router = express.Router();

    router.post(
        '/api/checkout',
        asyncHandler(async (req, res) => {
            const input = validateCheckout(req.body);
            const result = await checkoutController.checkout(input);
            res.status(200).json(result);
        })
    );

    router.get(
        '/api/admin/financial-report',
        requireAdmin,
        asyncHandler(async (req, res) => {
            const report = await reportController.financialReport();
            res.json(report);
        })
    );

    router.delete(
        '/api/users/:id',
        requireAdmin,
        asyncHandler(async (req, res) => {
            const id = validateUserId(req.params.id);
            const result = await userController.deleteUser(id);
            res.send(result.msg);
        })
    );

    return router;
}

module.exports = buildRouter;
