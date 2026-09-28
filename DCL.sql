-- Control de Acceso y Seguridad
-- Limpieza previa
REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM rol_logistica CASCADE;
DROP ROLE IF EXISTS operador_almacen;
DROP ROLE IF EXISTS rol_logistica;

-- 1. Usuario y Rol
-- Crear el usuario de conexión y el rol de logística
CREATE USER operador_almacen WITH PASSWORD 'Almacen_2026';
CREATE ROLE rol_logistica;

-- 2. Concesión de Privilegios
-- Otorgar permiso de lectura al rol sobre productos, pedidos y detalle_pedidos
GRANT SELECT ON productos, pedidos, detalle_pedidos TO rol_logistica;

-- Otorgar permiso de lectura, inserción y actualización al rol sobre envíos
GRANT SELECT, INSERT, UPDATE ON envios TO rol_logistica;

-- Conceder el rol creado al usuario operador_almacen
GRANT rol_logistica TO operador_almacen;

-- 3. Revocación de Privilegios
-- Se revoca únicamente el permiso de inserción sobre la tabla envíos
REVOKE INSERT ON envios FROM rol_logistica;

-- 4. Inspección de Seguridad
-- Mostrar en pantalla los privilegios finales asignados al rol
SELECT grantee, table_catalog, table_name, privilege_type 
FROM information_schema.table_privileges 
WHERE grantee = 'rol_logistica'
ORDER BY table_name, privilege_type;