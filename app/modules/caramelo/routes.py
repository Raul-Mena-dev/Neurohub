from flask import Blueprint, request

from app.common.decorators import require_api_key
from app.common.responses import error_response, success_response
from app.modules.caramelo.models import Producto
from app.modules.caramelo.schemas import (
    categoria_public_schema,
    pedido_sync_schema,
    producto_public_schema,
)
from app.modules.caramelo.services import (
    confirmar_pedido_recibido,
    crear_pedido_web,
    get_pedidos_pendientes,
    query_public_categorias,
    query_public_productos,
    sync_categorias,
    sync_productos,
)

caramelo_bp = Blueprint("caramelo", __name__)


@caramelo_bp.get("/categorias")
def listar_categorias():
    categorias = query_public_categorias(request.args.get("sucursal_id"))
    return success_response(data=[categoria_public_schema(item) for item in categorias])


@caramelo_bp.get("/productos")
def listar_productos():
    pagination = query_public_productos(request.args)
    return success_response(
        data={
            "items": [producto_public_schema(item) for item in pagination.items],
            "page": pagination.page,
            "limit": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
        }
    )


@caramelo_bp.get("/productos/<int:producto_id>")
def detalle_producto(producto_id):
    producto = Producto.query.filter_by(id=producto_id, activo=True, visible_web=True).first()
    if producto is None:
        return error_response("Producto no encontrado", status_code=404)
    return success_response(data=producto_public_schema(producto))


@caramelo_bp.post("/pedidos")
def crear_pedido():
    result, errors = crear_pedido_web(request.get_json(silent=True) or {})
    if errors:
        return error_response("No se pudo registrar el pedido", errors=errors, status_code=400)
    return success_response(data=result, message="Pedido registrado", status_code=201)


@caramelo_bp.post("/sync/categorias")
@require_api_key
def sincronizar_categorias():
    result, errors = sync_categorias(request.get_json(silent=True) or {})
    if errors:
        return error_response("No se pudieron sincronizar categorias", errors=errors, status_code=400)
    return success_response(data=result, message="Categorias sincronizadas")


@caramelo_bp.post("/sync/productos")
@require_api_key
def sincronizar_productos():
    result, errors = sync_productos(request.get_json(silent=True) or {})
    if errors:
        return error_response("No se pudieron sincronizar productos", errors=errors, status_code=400)
    return success_response(data=result, message="Productos sincronizados")


@caramelo_bp.get("/sync/pedidos-pendientes")
@require_api_key
def pedidos_pendientes():
    pedidos, errors = get_pedidos_pendientes(request.args.get("sucursal_id"))
    if errors:
        return error_response("No se pudieron obtener pedidos pendientes", errors=errors, status_code=400)
    return success_response(data=[pedido_sync_schema(pedido) for pedido in pedidos])


@caramelo_bp.post("/sync/pedidos/<int:pedido_id>/confirmar-recibido")
@require_api_key
def confirmar_recibido(pedido_id):
    payload = request.get_json(silent=True) or {}
    pedido, errors = confirmar_pedido_recibido(pedido_id, payload.get("sucursal_id"))
    if errors:
        return error_response("No se pudo confirmar el pedido", errors=errors, status_code=400)
    return success_response(
        data={"pedido_id": pedido.id, "folio": pedido.folio, "status": pedido.estatus},
        message="Pedido confirmado",
    )
