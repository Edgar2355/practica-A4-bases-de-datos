import random
from faker import Faker

# Inicializar Faker con localización de Mexico
fake = Faker('es_MX')

# Crear y abrir el archivo DML.sql en modo escritura
with open('DML.sql', 'w', encoding='utf-8') as f:
    f.write("-- DML.sql generado por seeder.py\n")
    f.write("-- ===================================\n\n")

    # Clientes (50 registros)
    f.write("-- 1. Inserción de 50 Clientes\n")
    estados_cuenta = ['activo', 'suspendido', 'inactivo']
    for _ in range(50):
        nombre = fake.name().replace("'", "''")
        correo = fake.unique.email()
        telefono = fake.phone_number()[:20]
        ciudad = fake.city().replace("'", "''")
        estado = random.choice(estados_cuenta)
        fecha_reg = fake.date_between(start_date='-3y', end_date='today')
        
        f.write(f"INSERT INTO clientes (nombre, correo, telefono, ciudad, estado, fecha_registro) "
                f"VALUES ('{nombre}', '{correo}', '{telefono}', '{ciudad}', '{estado}', '{fecha_reg}');\n")

    # Categorias (5 registros base)
    f.write("\n-- 2. Inserción de 5 Categorías\n")
    categorias = ['Smartphones', 'Laptops', 'Audio', 'Periféricos', 'Gaming']
    for cat in categorias:
        f.write(f"INSERT INTO categorias (nombre, descripcion) "
                f"VALUES ('{cat}', 'Artículos tecnológicos de la categoría {cat}');\n")

    # Productos (20 registros)
    f.write("\n-- 3. Inserción de 20 Productos\n")
    productos_precios = {} # Guardamos los precios para la congruencia en la tabla detalle
    for i in range(1, 21):
        sku = fake.unique.bothify(text='SKU-####-????').upper()
        id_categoria = random.randint(1, 5)
        nombre_prod = f"{random.choice(['Modelo', 'Gamer', 'Pro', 'Lite', 'Max'])} {fake.word().capitalize()}"
        precio = round(random.uniform(200.0, 15000.0), 2)
        existencias = random.randint(10, 150)
        
        productos_precios[i] = precio
        
        f.write(f"INSERT INTO productos (sku, id_categoria, nombre, precio_venta, existencias) "
                f"VALUES ('{sku}', {id_categoria}, '{nombre_prod}', {precio}, {existencias});\n")

    # Pedidos (40 registros)
    f.write("\n-- 4. Inserción de 40 Pedidos (Inician con total 0, se actualizará masivamente)\n")
    estados_pedido = ['pendiente', 'pagado', 'enviado', 'cancelado']
    for _ in range(40):
        id_cliente = random.randint(1, 50)
        estado_ped = random.choice(estados_pedido)
        f.write(f"INSERT INTO pedidos (id_cliente, estado) VALUES ({id_cliente}, '{estado_ped}');\n")

    # Detalle de Pedidos (70 registros, sin repetir producto por pedido)
    f.write("\n-- 5. Inserción de 70 Partidas de Detalle\n")
    detalles_generados = set()
    for _ in range(70):
        while True:
            id_pedido = random.randint(1, 40)
            id_producto = random.randint(1, 20)
            # Validar que esta combinación exacta no exista para cumplir con la regla de integridad
            if (id_pedido, id_producto) not in detalles_generados:
                detalles_generados.add((id_pedido, id_producto))
                break
        
        cantidad = random.randint(1, 5)
        precio_unit = productos_precios[id_producto] # Congruencia de precios
        f.write(f"INSERT INTO detalle_pedidos (id_pedido, id_producto, cantidad, precio_unitario) "
                f"VALUES ({id_pedido}, {id_producto}, {cantidad}, {precio_unit});\n")

    # Recalculo masivo del total de pedidos
    f.write("\n-- 6. Actualización masiva para recalcular el Total Acumulado en Pedidos\n")
    f.write("UPDATE pedidos SET total_acumulado = (\n")
    f.write("    SELECT COALESCE(SUM(cantidad * precio_unitario), 0)\n")
    f.write("    FROM detalle_pedidos WHERE detalle_pedidos.id_pedido = pedidos.id_pedido\n")
    f.write(");\n")

    # Envios (20 registros asociados a pedidos unicos)
    f.write("\n-- 7. Inserción de 20 Envíos y Logística\n")
    # Seleccionamos 20 pedidos aleatorios sin repetir para mantener la relación 1 a 1
    pedidos_con_envio = random.sample(range(1, 41), 20)
    for id_pedido in pedidos_con_envio:
        empresa = fake.company().replace("'", "''")
        guia = fake.unique.bothify(text='TRK-##########').upper()
        estado_ent = random.choice(['TRUE', 'FALSE'])
        fecha_est = fake.date_between(start_date='today', end_date='+15d')
        f.write(f"INSERT INTO envios (id_pedido, empresa_transportista, numero_guia, fecha_estimada_entrega, estado_entrega) "
                f"VALUES ({id_pedido}, '{empresa}', '{guia}', '{fecha_est}', {estado_ent});\n")

    # ANEXO: Transacciones TCL y Trigger
    f.write("\n\n-- ==========================================\n")
    f.write("-- MUTACIONES DML Y TRANSACCIONES TCL (A4_D01)\n")
    f.write("-- ==========================================\n\n")

    f.write("-- 1. Venta Atómica\n")
    f.write("BEGIN;\n")
    f.write("UPDATE productos SET existencias = existencias - 2 WHERE id_producto = 5;\n")
    f.write("INSERT INTO detalle_pedidos (id_pedido, id_producto, cantidad, precio_unitario) \n")
    f.write("VALUES (2, 5, 2, (SELECT precio_venta FROM productos WHERE id_producto = 5));\n")
    f.write("UPDATE pedidos SET total_acumulado = (SELECT COALESCE(SUM(cantidad * precio_unitario), 0) FROM detalle_pedidos WHERE id_pedido = 2) WHERE id_pedido = 2;\n")
    f.write("-- EXPLICACION ROLLBACK: Procederia ejecutar un ROLLBACK si las existencias cayeran por debajo de 0 (violando el CHECK >= 0), o si el producto 5 ya existiera en el pedido 2, violando la regla de integridad (UNIQUE).\n")
    f.write("COMMIT;\n\n")

    f.write("-- 2. Comprobación del Trigger (Auditoría)\n")
    f.write("UPDATE productos SET precio_venta = precio_venta * 1.10 WHERE id_categoria = 1;\n")
    f.write("SELECT * FROM auditoria_precios;\n")

print("Archivo DML.sql generado con éxito.")