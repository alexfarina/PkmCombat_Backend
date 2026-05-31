<h1 align="center" id="titulo">Pokemon Combat</h1>

<p align="center">
 <img width="300" height="250" alt="pokeball" src="https://github.com/user-attachments/assets/4677fe2f-1c1f-47a1-a0d6-19d7ebfee9d3" /><img width="1000" height="150" alt="pkmfont" src="https://github.com/user-attachments/assets/b2b5e499-e081-4e73-ba1a-c7e7835dab62" />

</p>

<p align="center">
  <img src="https://img.shields.io/badge/STATUS-EN%20PROCESO-yellow">
  <img src="https://img.shields.io/github/stars/alexfarina?style=social">
  <img src="https://img.shields.io/badge/release_date-junio-blue">
  <img src="https://img.shields.io/badge/platform-Android-green">
  <img src="https://img.shields.io/badge/backend-Django-092E20?logo=django">
</p>

<br>
<h2 id="indice">Índice</h2>
<ul>
  <li><a href="#titulo">Título e imagen de portada</a></li>
  <li><a href="#indice">Índice</a></li>
  <li><a href="#descripcion">Descripción del proyecto</a></li>
  <li><a href="#estado">Estado del proyecto</a></li>
  <li><a href="#caracteristicas">Características de la aplicación</a></li>
  <li><a href="#tecnologias">Tecnologías utilizadas</a></li>
  <li><a href="#instalacion">Instalación</a></li>
  <li><a href="#acceso">Acceso al proyecto</a></li>
  <li><a href="#desarrolladores">Personas Desarrolladoras del Proyecto</a></li>
  <li><a href="#licencias">Licencias</a></li>
</ul>

<hr>
<br>
<h2 id="descripcion">Descripción del proyecto</h2>
<p>
  <b>Pokémon Combat</b> es una aplicación móvil de combate Pokémon bajo una arquitectura cliente-servidor.
  Permite a los usuarios registrarse, configurar equipos Pokémon personalizados y desafiar a otros jugadores
  en batallas por turnos en tiempo real. Los datos de los Pokémon (sprites, stats y movimientos) se obtienen
  de la <b>PokeAPI</b> y se procesan en el servidor antes de enviarse al cliente.
</p>
<br>
<h2 id="estado">Estado del proyecto</h2>
<h4 align="center">
:construction: Proyecto en construcción :construction:
</h4>
<br>
<h2 id="caracteristicas">Características de la aplicación</h2>
<ul>
  <li>Registro e inicio de sesión con autenticación por token</li>
  <li>Creación y personalización de equipos Pokémon (hasta 6 miembros)</li>
  <li>Configuración de stats mediante EVs, nivel y naturaleza</li>
  <li>Asignación de movimientos a cada Pokémon</li>
  <li>Sistema de búsqueda y reto a otros jugadores</li>
  <li>Batallas por turnos en tiempo real con sistema de polling</li>
  <li>Sistema de estados y efectos de combate (quemadura, parálisis, sueño...)</li>
  <li>Log de batalla con el historial de acciones del turno</li>
  <li>Cálculo de daño con tabla de tipos, STAB y variación aleatoria</li>
</ul>
<br>
<h2 id="tecnologias">Tecnologías utilizadas</h2>
<ul>
  <li><strong>Android Studio (Java):</strong> Desarrollo del cliente móvil con navegación entre fragments y activities.</li>
  <li><strong>Volley:</strong> Librería para gestionar las peticiones HTTP desde Android.</li>
  <li><strong>Picasso:</strong> Librería para la carga de sprites desde URL.</li>
  <li><strong>Python / Django:</strong> Backend encargado de la lógica de negocio y el sistema de turnos.</li>
  <li><strong>Django ORM:</strong> Para la gestión de la base de datos.</li>
  <li><strong>bcrypt:</strong> Cifrado de contraseñas.</li>
  <li><strong>Requests:</strong> Para las peticiones a la PokeAPI desde el servidor.</li>
  <li><strong>PokeAPI:</strong> API externa de la que se obtienen sprites, stats y movimientos.</li>
  <li><strong>SQLite:</strong> Base de datos para usuarios, equipos y batallas.</li>
</ul>
<br>
<h2 id="instalacion">Instalación</h2>

<h3>🖥️ Backend (Django)</h3>
<ol>
  <li><b>Clona el repositorio</b><br>
    <code>git clone https://github.com/alexfarina/pokemon-combat-backend.git</code>
  </li><br>
  <li><b>Instala las dependencias necesarias</b><br>
    <code>pip install django bcrypt requests</code>
  </li><br>
  <li><b>Aplica las migraciones</b><br>
    <code>python manage.py migrate</code>
  </li><br>
  <li><b>Inicia el servidor</b><br>
    <code>python manage.py runserver</code>
  </li><br>
  <li>El servidor quedará disponible en <code>http://127.0.0.1:8000</code></li>
</ol>

<h3>📱 Frontend (Android)</h3>
<ol>
  <li><b>Clona el repositorio</b><br>
    <code>git clone https://github.com/alexfarina/pokemon-combat-frontend.git</code>
  </li><br>
  <li><b>Abre el proyecto en Android Studio</b><br>
    File → Open → selecciona la carpeta del proyecto.
  </li><br>
  <li><b>Asegúrate de que el backend está corriendo</b> en <code>http://10.0.2.2:8000</code> si usas el emulador de Android Studio.</li><br>
  <li><b>Compila y ejecuta</b> la aplicación desde Android Studio sobre un emulador o dispositivo físico con Android 9.0 (API 28) o superior.</li>
</ol>

<br>
<h2 id="acceso">Acceso al proyecto</h2>
<p>
  Puedes acceder al código fuente del proyecto a través de los repositorios de GitHub.<br>
  Para usar la aplicación es necesario registrarse con un nombre de usuario, email y contraseña.
</p>
<br>
<h2 id="desarrolladores">Personas Desarrolladoras del Proyecto</h2>
<p>
  Proyecto desarrollado por <b>Alexandre Fariña Caamaño</b>, encargado del diseño, desarrollo del backend en Django
  y del cliente Android.
</p>
<br>
<h2 id="licencias">Licencias</h2>
<p>
  <b>Pokémon Combat</b> es un proyecto educativo de fin de ciclo.<br>
  Los datos de los Pokémon son obtenidos de <a href="https://pokeapi.co/">PokeAPI</a>, que es de uso libre.<br>
  Pokémon y todos los nombres relacionados son marcas registradas de Nintendo / Game Freak.<br>
  Este proyecto no tiene fines comerciales.
</p>
