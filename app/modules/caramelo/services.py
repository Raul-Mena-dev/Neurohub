from datetime import datetime
from decimal import Decimal, InvalidOperation

from sqlalchemy import or_

from app.extensions import db
from app.modules.caramelo.models import Categoria, Pedido, PedidoDetalle, Producto, Sucursal


def parse_datetime(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def parse_decimal(value, default=None):
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return default


def query_public_categorias(sucursal_id=None):
    query = Categoria.query.filter_by(activo=True)
    if sucursal_id:
        query = query.filter_by(sucursal_id=sucursal_id)
    return query.order_by(Categoria.nombre.asc()).all()


def query_public_productos(args):
    page = max(args.get("page", default=1, type=int), 1)
    limit = min(max(args.get("limit", default=24, type=int), 1), 100)

    query = Producto.query.filter_by(activo=True, visible_web=True)

    sucursal_id = args.get("sucursal_id")
    categoria_id = args.get("categoria_id", type=int)
    search = args.get("search")

    if sucursal_id:
        query = query.filter_by(sucursal_id=sucursal_id)
    if categoria_id:
        query = query.filter_by(categoria_id=categoria_id)
    if search:
        term = f"%{search.strip()}%"
        query = query.filter(or_(Producto.nombre.ilike(term), Producto.sku.ilike(term)))

    return query.order_by(Producto.nombre.asc()).paginate(page=page, per_page=limit, error_out=False)


def sync_categorias(payload):
    sucursal_id = payload.get("sucursal_id")
    categorias = payload.get("categorias") or []
    if not sucursal_id:
        return None, {"sucursal_id": ["Campo requerido"]}

    ensure_sucursal(sucursal_id)
    creadas = 0
    actualizadas = 0
    errores = []

    for index, item in enumerate(categorias):
        id_local = item.get("id_local")
        nombre = item.get("nombre")
        if not id_local or not nombre:
            errores.append({"index": index, "error": "id_local y nombre son requeridos"})
            continue

        categoria = Categoria.query.filter_by(sucursal_id=sucursal_id, id_local_pos=id_local).first()
        if categoria is None:
            categoria = Categoria(sucursal_id=sucursal_id, id_local_pos=id_local, nombre=nombre)
            db.session.add(categoria)
            creadas += 1
        else:
            actualizadas += 1

        categoria.nombre = nombre
        categoria.activo = bool(item.get("activo", True))
        categoria.fecha_modificacion_pos = parse_datetime(item.get("fecha_modificacion"))
        categoria.fecha_sincronizacion = datetime.utcnow()

    db.session.commit()
    return {
        "recibidas": len(categorias),
        "creadas": creadas,
        "actualizadas": actualizadas,
        "errores": errores,
    }, None


def sync_productos(payload):
    sucursal_id = payload.get("sucursal_id")
    productos = payload.get("productos") or []
    if not sucursal_id:
        return None, {"sucursal_id": ["Campo requerido"]}

    ensure_sucursal(sucursal_id)
    creados = 0
    actualizados = 0
    errores = []

    for index, item in enumerate(productos):
        id_local = item.get("id_local")
        nombre = item.get("nombre")
        precio = parse_decimal(item.get("precio"))
        existencia = parse_decimal(item.get("existencia"), Decimal("0"))

        if not id_local or not nombre or precio is None:
            errores.append({"index": index, "error": "id_local, nombre y precio son requeridos"})
            continue

        categoria = None
        categoria_id_local = item.get("categoria_id_local")
        if categoria_id_local:
            categoria = Categoria.query.filter_by(
                sucursal_id=sucursal_id,
                id_local_pos=categoria_id_local,
            ).first()

        producto = Producto.query.filter_by(sucursal_id=sucursal_id, id_local_pos=id_local).first()
        if producto is None:
            producto = Producto(sucursal_id=sucursal_id, id_local_pos=id_local, nombre=nombre, precio=precio)
            db.session.add(producto)
            creados += 1
        else:
            actualizados += 1

        producto.categoria_id = categoria.id if categoria else None
        producto.sku = item.get("sku")
        producto.nombre = nombre
        producto.slug = item.get("slug")
        producto.descripcion = item.get("descripcion")
        producto.precio = precio
        producto.existencia = existencia
        producto.imagen_url = item.get("imagen_url")
        producto.activo = bool(item.get("activo", True))
        producto.visible_web = bool(item.get("visible_web", True))
        producto.fecha_modificacion_pos = parse_datetime(item.get("fecha_modificacion"))
        producto.fecha_sincronizacion = datetime.utcnow()

    db.session.commit()
    return {
        "recibidos": len(productos),
        "creados": creados,
        "actualizados": actualizados,
        "errores": errores,
    }, None


def crear_pedido_web(payload):
    errors = {}
    sucursal_id = payload.get("sucursal_id")
    cliente_nombre = payload.get("cliente_nombre")
    items = payload.get("items") or []

    if not sucursal_id:
        errors["sucursal_id"] = ["Campo requerido"]
    if not cliente_nombre:
        errors["cliente_nombre"] = ["Campo requerido"]
    if not items:
        errors["items"] = ["Debe incluir al menos un producto"]
    if errors:
        return None, errors

    sucursal = ensure_sucursal(sucursal_id)
    pedido = Pedido(
        sucursal_id=sucursal.id,
        cliente_nombre=cliente_nombre,
        cliente_telefono=payload.get("cliente_telefono"),
        cliente_email=payload.get("cliente_email"),
        notas=payload.get("notas"),
        total=Decimal("0"),
        estatus="pendiente",
    )

    total = Decimal("0")
    item_errors = []
    for index, item in enumerate(items):
        producto_id = item.get("producto_id")
        cantidad = parse_decimal(item.get("cantidad"))
        if not producto_id or cantidad is None or cantidad <= 0:
            item_errors.append({"index": index, "error": "producto_id y cantidad mayor a cero son requeridos"})
            continue

        producto = Producto.query.filter_by(
            id=producto_id,
            sucursal_id=sucursal_id,
            activo=True,
            visible_web=True,
        ).first()
        if producto is None:
            item_errors.append({"index": index, "error": "Producto no disponible"})
            continue

        subtotal = producto.precio * cantidad
        total += subtotal
        pedido.detalles.append(
            PedidoDetalle(
                producto_id=producto.id,
                id_local_pos=producto.id_local_pos,
                nombre_producto=producto.nombre,
                cantidad=cantidad,
                precio_unitario=producto.precio,
                subtotal=subtotal,
            )
        )

    if item_errors or not pedido.detalles:
        db.session.rollback()
        return None, {"items": item_errors or ["No hay productos validos"]}

    pedido.total = total
    db.session.add(pedido)
    db.session.flush()
    pedido.folio = f"CAR-{pedido.id:06d}"
    db.session.commit()

    return {
        "pedido_id": pedido.id,
        "folio": pedido.folio,
        "status": pedido.estatus,
    }, None


def get_pedidos_pendientes(sucursal_id):
    if not sucursal_id:
        return None, {"sucursal_id": ["Campo requerido"]}

    pedidos = (
        Pedido.query.filter_by(sucursal_id=sucursal_id, estatus="pendiente")
        .order_by(Pedido.fecha_registro.asc())
        .all()
    )
    return pedidos, None


def confirmar_pedido_recibido(pedido_id, sucursal_id):
    if not sucursal_id:
        return None, {"sucursal_id": ["Campo requerido"]}

    pedido = Pedido.query.filter_by(id=pedido_id, sucursal_id=sucursal_id).first()
    if pedido is None:
        return None, {"pedido": ["Pedido no encontrado para la sucursal"]}

    pedido.estatus = "recibido_por_pos"
    pedido.fecha_modificacion = datetime.utcnow()
    db.session.commit()
    return pedido, None


def ensure_sucursal(sucursal_id):
    sucursal = Sucursal.query.get(sucursal_id)
    if sucursal is None:
        sucursal = Sucursal(id=sucursal_id, nombre=sucursal_id)
        db.session.add(sucursal)
        db.session.flush()
    return sucursal
