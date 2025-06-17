from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity, jwt_required
from ..Modelos import db, Venta, Producto
from datetime import datetime

from flask_restful import Resource
from flask_jwt_extended import jwt_required
from ..Modelos import db, Venta, Producto
from datetime import datetime

class VistaHistorial(Resource):
    @jwt_required()
    def get(self):
        ventas = Venta.query.all()
        productos = Producto.query.all()

        movimientos = []

        for venta in ventas:
            movimientos.append({
                "id": venta.Id_Venta,
                "fecha": venta.Fecha_Venta.isoformat() if venta.Fecha_Venta else None,
                "usuario": venta.usuario.Nombre_Usu if venta.usuario else "Desconocido",
                "total": float(venta.Total_Venta or 0),
                "movimiento": venta.movimiento.value
            })

        for producto in productos:
            movimientos.append({
                "id": producto.Id_Producto,
                "fecha": producto.Fecha_Registro_Prod.isoformat() if producto.Fecha_Registro_Prod else None,
                "usuario": producto.usuario.Nombre_Usu if producto.usuario else "Desconocido",
                "total": float(producto.Precio_Neto_Unidad_Prod or 0),
                "movimiento": producto.movimiento.value
            })

        movimientos.sort(key=lambda x: x["fecha"] or "", reverse=True)
        return movimientos, 200
