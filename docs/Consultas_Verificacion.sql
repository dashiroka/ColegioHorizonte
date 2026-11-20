-- Ejecutar en pgAdmin luego de realizar el flujo desde la aplicación.
-- Las tablas con app_label academico aparecen prefijadas por academico_.
SELECT * FROM academico_estudiante ORDER BY id DESC LIMIT 10;
SELECT * FROM academico_matricula ORDER BY id DESC LIMIT 10;
SELECT * FROM academico_obligacion ORDER BY id DESC LIMIT 15;
SELECT * FROM academico_pago ORDER BY id DESC LIMIT 10;
SELECT * FROM academico_detallepago ORDER BY id DESC LIMIT 10;
SELECT * FROM academico_auditoria ORDER BY id DESC LIMIT 20;
-- Saldos (excluye pagos anulados):
SELECT o.id, o.descripcion, o.valor,
       COALESCE(SUM(d.valor) FILTER (WHERE p.estado = 'Confirmado'),0) AS abonado,
       o.valor - COALESCE(SUM(d.valor) FILTER (WHERE p.estado = 'Confirmado'),0) AS saldo
FROM academico_obligacion o
LEFT JOIN academico_detallepago d ON d.obligacion_id=o.id
LEFT JOIN academico_pago p ON p.id=d.pago_id
GROUP BY o.id, o.descripcion, o.valor
ORDER BY o.id;
