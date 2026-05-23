from decimal import Decimal


def decimal_to_float(value):
    if value is None:
        return None
    if isinstance(value, Decimal):
        return float(value)
    return value


def categoria_public_schema(categoria):
    return {
        "id": categoria.id,
        "nombre": categoria.nombre,
    }


def producto_public_schema(producto):
    return {
        "id": producto.id,
        "sucursal_id": producto.sucursal_id,
        "categoria_id": producto.categoria_id,
        "id_local_pos": producto.id_local_pos,
        "sku": producto.sku,
        "nombre": producto.nombre,
        "slug": producto.slug,
        "descripcion": producto.descripcion,
        "precio": decimal_to_float(producto.precio),
        "existencia": decimal_to_float(producto.existencia),
        "imagen_url": producto.imagen_url,
    }


def pedido_sync_schema(pedido):
    return {
        "id": pedido.id,
        "folio": pedido.folio,
        "cliente_nombre": pedido.cliente_nombre,
        "cliente_telefono": pedido.cliente_telefono,
        "cliente_email": pedido.cliente_email,
        "total": decimal_to_float(pedido.total),
        "status": pedido.estatus,
        "notas": pedido.notas,
        "items": [
            {
                "id_local_pos": detalle.id_local_pos,
                "nombre_producto": detalle.nombre_producto,
                "cantidad": decimal_to_float(detalle.cantidad),
                "precio_unitario": decimal_to_float(detalle.precio_unitario),
                "subtotal": decimal_to_float(detalle.subtotal),
            }
            for detalle in pedido.detalles
        ],
    }
