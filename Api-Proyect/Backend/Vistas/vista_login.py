from flask import request
from sqlalchemy import or_
from ..Modelos import db, Usuario
from flask_restful import Resource
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash


class VistaLogin(Resource):
    def post(self):
        """
        Ingresar a la Pagina
        ---
        tags:
          - Login:
        security: 
          - Bearer: []
        parameters:
          - in: body
            name: login
            required: true
            schema: 
                type: object
                required:
                  - Email_Usu
                  - Contraseña_hash
                properties:
                  Email_Usu:
                    type: string
                  Contraseña_hash:
                    type: string
        responses:
          201:
            description: Login exitosamente
          500:
            description: error del servidor
        """
        Email_Usu = request.json.get("Email_Usu")
        Nombre_Usu = request.json.get("Nombre_Usu")
        Contraseña_hash = request.json.get("Contraseña_hash")

        usuario = None
        
       
        if Email_Usu:
            usuario = Usuario.query.filter_by(Email_Usu=Email_Usu).first()
        
        elif Nombre_Usu:
            usuario = Usuario.query.filter_by(Nombre_Usu=Nombre_Usu).first() 

        print(f"Email_Usu: {Email_Usu}")
        print(f"Nombre_Usu: {Nombre_Usu}")
        print(f"Usuario encontrado: {usuario}")       
        
        
        if usuario and usuario.verificar_contraseña(Contraseña_hash):
            access_token = create_access_token(identity=str(usuario.Id_Usuario))
            return {"access_token": access_token}, 200
        
        return {"error": "Credenciales inválidas"}, 401