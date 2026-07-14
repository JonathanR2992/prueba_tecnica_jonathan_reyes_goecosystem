# Sistema de Gestión de Pacientes

Aplicación Full Stack desarrollada para administrar pacientes pendientes de atención médica. Permite autenticar usuarios, consultar indicadores operativos, buscar y filtrar pacientes, registrar nuevos pacientes, actualizar su información y eliminar registros.

## Tecnologías utilizadas

### Backend
- Python
- Flask
- Flask-SQLAlchemy
- Flask-JWT-Extended
- Flask-Cors
- PyMySQL
- python-dotenv
- MariaDB

### Frontend
- Angular
- Angular Material
- TypeScript
- RxJS
- Formularios reactivos
- Angular Router
- Interceptores HTTP
- Route Guards

### Base de datos y carga inicial
- MariaDB
- SQL
- Python
- Pandas
- odfpy
- PyMySQL
- Archivo `.ods`

## Funcionalidades principales

- Inicio de sesión mediante usuario y contraseña.
- Autenticación basada en JWT.
- Protección de rutas en Angular.
- Consulta del usuario autenticado.
- Dashboard con indicadores operativos.
- Listado paginado de pacientes.
- Búsqueda por nombre o documento.
- Filtros por estado, prioridad y EPS.
- Consulta de paciente por identificador.
- Registro, actualización y eliminación de pacientes.
- Consulta de catálogos.
- Validación de campos en backend y frontend.
- Interfaz responsiva con Angular Material.

## Arquitectura general

```text
Angular
   |
   | HTTP / JSON / JWT
   v
Flask API REST
   |
   | SQLAlchemy / PyMySQL
   v
MariaDB
```

## Estructura del repositorio

```text
clinica-pacientes/
├── backend/
├── frontend/
│   └── clinica-pacientes-web/
├── database/
│   ├── database.sql
│   └── carga_inicial/
│       ├── cargar_pacientes.py
│       └── pacientes.ods
├── docs/
├── .gitignore
└── README.md
```

# Base de datos

En la carpeta `database` se incluye un script SQL con:

- Creación de la base de datos.
- Creación de tablas.
- Llaves primarias y foráneas.
- Restricciones de integridad.
- Índices.
- Inserción de catálogos.
- Inserción de usuarios de demostración.
- Inserción de datos iniciales cuando corresponda.

Tablas principales:

```text
usuarios
pacientes
eps
generos
prioridades
estados
tipos_documento
```

Relaciones:

```text
tipos_documento 1 ─── N pacientes
generos         1 ─── N pacientes
eps             1 ─── N pacientes
prioridades     1 ─── N pacientes
estados         1 ─── N pacientes
```

## Carga de pacientes desde el archivo ODS

Además del SQL principal, se incluye un script independiente en Python para procesar el archivo `.ods` suministrado.

El flujo es:

1. Leer el archivo `.ods`.
2. Construir un `DataFrame` con Pandas.
3. Normalizar columnas y tipos de datos.
4. Eliminar `eps_nombre`, porque este valor está normalizado en la tabla `eps`.
5. Convertir fechas y valores numéricos.
6. Preparar los registros.
7. Insertar los pacientes en MariaDB mediante `executemany()`.

La tabla `pacientes` almacena `eps_codigo` como llave foránea. El nombre de la EPS se obtiene mediante la relación con la tabla `eps`.

Dependencias del script:

```bash
pip install pandas odfpy pymysql
```

Ejecución:

```bash
python cargar_pacientes.py
```

Validación:

```sql
SELECT COUNT(*) AS total_pacientes
FROM pacientes;
```

Resultado esperado:

```text
1000
```

Validación de duplicados:

```sql
SELECT documento, COUNT(*) AS cantidad
FROM pacientes
GROUP BY documento
HAVING COUNT(*) > 1;
```

# Ejecución del backend

## Requisitos

- Python 3.11 o superior.
- MariaDB en ejecución.
- Base de datos creada.

## Crear entorno virtual

```bash
cd backend
python -m venv venv
```

Windows PowerShell:

```powershell
venv\Scripts\Activate.ps1
```

Windows CMD:

```cmd
venv\Scripts\activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

## Instalar dependencias

```bash
pip install -r requirements.txt
```

## Variables de entorno

Crea `backend/.env` a partir de `.env.example`:

```env
FLASK_DEBUG=true
SECRET_KEY=change-this-secret
JWT_SECRET_KEY=change-this-jwt-secret

DB_HOST=localhost
DB_PORT=3306
DB_NAME=clinica_pacientes
DB_USER=root
DB_PASSWORD=your-password

FRONTEND_URL=http://localhost:4200
```

No se debe subir `.env` al repositorio.

## Ejecutar Flask

```bash
python run.py
```

Backend:

```text
http://127.0.0.1:5000
```

Health check:

```text
GET http://127.0.0.1:5000/api/health
```

# API REST

Todos los endpoints protegidos requieren:

```http
Authorization: Bearer <JWT>
```

## Autenticación

```http
POST /api/auth/login
GET  /api/auth/me
```

Ejemplo:

```json
{
  "usuario": "admin.demo",
  "password": "Demo2026*"
}
```

## Catálogos

```http
GET /api/catalogs
```

## Dashboard

```http
GET /api/dashboard
```

## Pacientes

```http
GET    /api/patients
GET    /api/patients/<id>
POST   /api/patients
PUT    /api/patients/<id>
DELETE /api/patients/<id>
```

Filtros:

```text
page
per_page
search
status
priority
eps_codigo
```

Ejemplo:

```http
GET /api/patients?search=Ana&status=Pendiente&priority=Alta&page=1&per_page=10
```

# Ejecución del frontend

## Versiones utilizadas

```text
Node.js: v20.16.0
npm: 10.8.2
```

## Instalar Angular CLI

```bash
npm install -g @angular/cli
```

## Instalar dependencias

```bash
cd frontend/clinica-pacientes-web
npm install
```

## Configurar la API

Archivo:

```text
src/environments/environment.ts
```

```typescript
export const environment = {
  production: false,
  apiUrl: 'http://127.0.0.1:5000/api',
};
```

## Ejecutar Angular

```bash
ng serve
```

También:

```bash
npm start
```

Frontend:

```text
http://localhost:4200
```

# Orden recomendado de ejecución

1. Iniciar MariaDB.
2. Ejecutar `database/database.sql`.
3. Ejecutar la carga desde `.ods` cuando sea necesario.
4. Iniciar Flask.
5. Iniciar Angular.
6. Abrir `http://localhost:4200`.

Ejemplo de carga:

```bash
python database/carga_inicial/cargar_pacientes.py
```

Backend:

```bash
cd backend
venv\Scripts\Activate.ps1
python run.py
```

Frontend, en otra terminal:

```bash
cd frontend/clinica-pacientes-web
npm install
ng serve
```

# Credenciales de demostración

Administrador:

```text
Usuario: admin.demo
Contraseña: Demo2026*
```

Operador:

```text
Usuario: operador.demo
Contraseña: Demo2026*
```

# Consideraciones de seguridad

Para conservar fidelidad con los datos sintéticos entregados, las contraseñas de demostración se almacenan temporalmente en texto plano en `password_demo`.

En producción se debe:

- Utilizar Argon2, bcrypt o scrypt.
- Almacenar únicamente hashes.
- Usar HTTPS.
- Implementar revocación o rotación de JWT.
- Evaluar cookies `HttpOnly`, `Secure` y `SameSite`.
- Implementar protección CSRF cuando corresponda.

El frontend utiliza `sessionStorage` para el JWT por simplicidad de demostración.

# Decisiones técnicas

## Flask
Se utiliza como backend para exponer una API REST modular y conectada con MariaDB mediante SQLAlchemy.

## Angular
Se utiliza como frontend independiente, con componentes standalone, formularios reactivos, guards, interceptor JWT y Angular Material.

## JWT
Permite autenticar el frontend Angular contra la API Flask.

## MariaDB
Garantiza integridad referencial, restricciones y consultas de agregación.

## Catálogos normalizados
EPS, género, prioridad, estado y tipo de documento se almacenan en tablas separadas para evitar duplicidades.

# Uso de inteligencia artificial

Durante el desarrollo se utilizaron herramientas de inteligencia artificial como apoyo para:

- Analizar el enunciado.
- Proponer la arquitectura.
- Generar estructuras iniciales.
- Revisar y refactorizar código.
- Identificar errores de configuración.
- Documentar la solución.

Las propuestas fueron revisadas, ejecutadas, corregidas y validadas antes de incorporarlas. La responsabilidad técnica sobre las decisiones, el código y el funcionamiento permanece en el autor.

# Mejoras futuras

- Hash seguro de contraseñas.
- Eliminación lógica.
- Auditoría.
- Roles y permisos detallados.
- Pruebas automatizadas.
- Renovación de tokens.
- Swagger/OpenAPI.
- Contenedorización.
- Despliegue en nube.
- Reportes e indicadores históricos.

# Autor

Jonathan Reyes