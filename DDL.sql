-- Eliminacion en cascada de los objetos existentes
drop table if exists auditoria_precios cascade;
drop table if exists envios cascade;
drop table if exists detalle_pedidos cascade;
drop table if exists pedidos cascade;
drop table if exists productos cascade;
drop table if exists categorias cascade;
drop table if exists clientes cascade;

-- Clientes
create table clientes (
    id_cliente serial primary key,
    nombre varchar(50) not null,
    correo varchar(100) unique not null,
    telefono varchar(20),
    ciudad varchar(100),
    estado varchar(50) check (estado in ('activo', 'suspendido', 'inactivo')) not null,
    fecha_registro date default current_date
);

-- Categorias de Productos

create table categorias (
    id_categoria serial primary key,
    nombre varchar(100) unique not null,
    descripcion text
);


-- Catalogo de Productos
create table productos (
    id_producto serial primary key,
    sku varchar(50) unique not null,
    id_categoria int not null,
    nombre varchar(150) not null,
    precio_venta numeric(10, 2) check (precio_venta > 0) not null,
    existencias int check (existencias >= 0) not null,
    -- Impide eliminar categorias si tienen productos asociados
    constraint fk_categoria foreign key (id_categoria) references categorias(id_categoria) on delete restrict
);


-- Pedidos
create table pedidos (
    id_pedido serial primary key,
    id_cliente int not null,
    fecha_hora_compra timestamp default current_timestamp,
    total_acumulado numeric(12, 2) check (total_acumulado >= 0) default 0.00,
    estado varchar(20) check (estado in ('pendiente', 'pagado', 'enviado', 'cancelado')) not null,
    constraint fk_cliente foreign key (id_cliente) references clientes(id_cliente)
);

-- Detalle de Pedidos
create table detalle_pedidos (
    id_detalle serial primary key,
    id_pedido int not null,
    id_producto int not null,
    cantidad int check (cantidad > 0) not null,
    precio_unitario numeric(10, 2) check (precio_unitario > 0) not null,
    -- Eliminacion en cascada si se elimina el pedido
    constraint fk_pedido foreign key (id_pedido) references pedidos(id_pedido) on delete cascade,
    constraint fk_producto foreign key (id_producto) references productos(id_producto),
    -- Impide registrar el mismo producto dos veces en un pedido
    constraint unq_pedido_producto unique (id_pedido, id_producto)
);


-- Envios y Logistica
create table envios (
    id_envio serial primary key,
    id_pedido int unique not null,
    empresa_transportista varchar(100) not null,
    numero_guia varchar(100) unique not null,
    fecha_estimada_entrega date,
    estado_entrega boolean default false,
    -- Relacion uno a uno entre pedido y envio
    constraint fk_envio_pedido foreign key (id_pedido) references pedidos(id_pedido) on delete cascade
);

-- Auditoria de Precios
create table auditoria_precios (
    id_auditoria serial primary key,
    id_producto int not null,
    precio_anterior numeric(10, 2) not null,
    precio_nuevo numeric(10, 2) not null,
    usuario_db varchar(50) not null,
    marca_tiempo timestamp default current_timestamp

);

-- Funcion del Trigger para registrar historial de precios
create or replace function trg_auditoria_precio_func()
returns trigger as $$
begin
	insert into auditoria_precios (
        id_producto,
        precio_anterior,
        precio_nuevo,
        usuario_db,
        marca_tiempo
    )
    values (
        new.id_producto,
        old.precio_venta,
        new.precio_venta,
        current_user,
        current_timestamp
    );
    return new;
end;
$$ language plpgsql;

-- Trigger automatizado asignado a la tabla de productos
create trigger trg_auditoria_precio
after update of precio_venta on productos
for each row
when (old.precio_venta is distinct from new.precio_venta)
execute function trg_auditoria_precio_func();


