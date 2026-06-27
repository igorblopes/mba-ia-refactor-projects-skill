const { PAYMENT_STATUS } = require('../constants');

// Caso de uso do relatório financeiro. Busca linhas planas do model (uma query,
// sem N+1) e agrega em memória — a regra de cálculo de receita vive aqui (AP-07/AP-12).
class ReportController {
    constructor({ reportModel }) {
        this.reportModel = reportModel;
    }

    async financialReport() {
        const rows = await this.reportModel.getFinancialRows();

        const byCourse = new Map();
        for (const row of rows) {
            if (!byCourse.has(row.course_id)) {
                byCourse.set(row.course_id, {
                    course: row.course_title,
                    revenue: 0,
                    students: [],
                });
            }
            const courseData = byCourse.get(row.course_id);

            // Cursos sem matrícula vêm com enrollment_id nulo (LEFT JOIN) e não
            // adicionam alunos — preserva o formato do relatório legado.
            if (row.enrollment_id == null) continue;

            if (row.payment_status === PAYMENT_STATUS.PAID) {
                courseData.revenue += row.payment_amount;
            }
            courseData.students.push({
                student: row.student_name || 'Unknown',
                paid: row.payment_amount != null ? row.payment_amount : 0,
            });
        }

        return Array.from(byCourse.values());
    }
}

module.exports = ReportController;
