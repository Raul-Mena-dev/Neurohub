from datetime import datetime

from sqlalchemy import UniqueConstraint

from app.extensions import db


class Sucursal(db.Model):
    __tablename__ = "caramelo_sucursales"

    id = db.Column(db.String(64), primary_key=True)
    nombre = db.Column(db.String(160), nullable=False)
    api_key_hash = db.Column(db.String(255), nullable=True)
    activa = db.Column(db.Boolean, nullable=False, default=True)
    fecha_registro = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    fecha_modificacion = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    categorias = db.relationship("Categoria", back_populates="sucursal")
    productos = db.relationship("Producto", back_populates="sucursal")
    pedidos = db.relationship("Pedido", back_populates="sucursal")


class Categoria(db.Model):
    __tablename__ = "caramelo_categorias"
    __table_args__ = (
        UniqueConstraint("sucursal_id", "id_local_pos", name="uq_categoria_sucursal_local"),
    )

    id = db.Column(db.Integer, primary_key=True)
    sucursal_id = db.Column(db.String(64), db.ForeignKey("caramelo_sucursales.id"), nullable=False)
    id_local_pos = db.Column(db.String(120), nullable=False)
    nombre = db.Column(db.String(180), nullable=False)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    fecha_modificacion_pos = db.Column(db.DateTime, nullable=True)
    fecha_sincronizacion = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    sucursal = db.relationship("Sucursal", back_populates="categorias")
    productos = db.relationship("Producto", back_populates="categoria")


class Producto(db.Model):
    __tablename__ = "caramelo_productos"
    __table_args__ = (
        UniqueConstraint("sucursal_id", "id_local_pos", name="uq_producto_sucursal_local"),
    )

    id = db.Column(db.Integer, primary_key=True)
    sucursal_id = db.Column(db.String(64), db.ForeignKey("caramelo_sucursales.id"), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey("caramelo_categorias.id"), nullable=True)
    id_local_pos = db.Column(db.String(120), nullable=False)
    sku = db.Column(db.String(120), nullable=True)
    nombre = db.Column(db.String(220), nullable=False)
    slug = db.Column(db.String(240), nullable=True)
    descripcion = db.Column(db.Text, nullable=True)
    precio = db.Column(db.Numeric(12, 2), nullable=False)
    existencia = db.Column(db.Numeric(12, 3), nullable=False, default=0)
    imagen_url = db.Column(db.String(500), nullable=True)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    visible_web = db.Column(db.Boolean, nullable=False, default=True)
    fecha_modificacion_pos = db.Column(db.DateTime, nullable=True)
    fecha_sincronizacion = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    sucursal = db.relationship("Sucursal", back_populates="productos")
    categoria = db.relationship("Categoria", back_populates="productos")
    detalles_pedido = db.relationship("PedidoDetalle", back_populates="producto")


class Pedido(db.Model):
    __tablename__ = "caramelo_pedidos"

    id = db.Column(db.Integer, primary_key=True)
    folio = db.Column(db.String(40), unique=True, nullable=True)
    sucursal_id = db.Column(db.String(64), db.ForeignKey("caramelo_sucursales.id"), nullable=False)
    cliente_nombre = db.Column(db.String(180), nullable=False)
    cliente_telefono = db.Column(db.String(40), nullable=True)
    cliente_email = db.Column(db.String(180), nullable=True)
    total = db.Column(db.Numeric(12, 2), nullable=False)
    estatus = db.Column(db.String(40), nullable=False, default="pendiente")
    notas = db.Column(db.Text, nullable=True)
    fecha_registro = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    fecha_modificacion = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    sucursal = db.relationship("Sucursal", back_populates="pedidos")
    detalles = db.relationship(
        "PedidoDetalle",
        back_populates="pedido",
        cascade="all, delete-orphan",
    )


class PedidoDetalle(db.Model):
    __tablename__ = "caramelo_pedido_detalles"

    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("caramelo_pedidos.id"), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey("caramelo_productos.id"), nullable=True)
    id_local_pos = db.Column(db.String(120), nullable=True)
    nombre_producto = db.Column(db.String(220), nullable=False)
    cantidad = db.Column(db.Numeric(12, 3), nullable=False)
    precio_unitario = db.Column(db.Numeric(12, 2), nullable=False)
    subtotal = db.Column(db.Numeric(12, 2), nullable=False)

    pedido = db.relationship("Pedido", back_populates="detalles")
    producto = db.relationship("Producto", back_populates="detalles_pedido")
