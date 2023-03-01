# Alwa

## 1- Instalación de Dspace

- Descargar respositorio de Dspace (git o descargar código): https://github.com/DSpace/dspace-angular.git
- Entrar al directorio y descargar las imagenes correspondientes al backend de Dspace:
```sh
cd dspace-angular
docker-compose -f docker/docker-compose-rest.yml pull
```
- Al descargar las imagenes levantar el servicio:
```sh
docker-compose -p d7 -f docker/docker-compose-rest.yml up
```
- Crear usuario con el que se trabajará en Dspace:
```sh
docker-compose -p d7 -f docker/cli.yml run --rm dspace-cli create-administrator -e test@test.edu -f admin -l user -p admin -c en
```

## 2- Instalación de SkyCDS

- Descargar proyecto SkyCDS
- Instalar SkyCDS con docker-compose:
```sh
cd SkyCDS
docker-compose up
```

## 3- Alwa
- Entrar a script Alwa-Flask/flask/app/init.py y configurar la IP y puerto de Dspace
- Correr archivo init.py:
```sh
python init.py
```
- Entrar a script Alwa-Flask/flask/app/init_painal.py y configurar la IP y puerto de SkyCDS
- Correr archivo init_painal.py:
```sh
python init_painal.py
```
- Entrar a archivo Alwa-Flask/app/views.py y configurar la IP's y puertos de Dspace y SkyCDS
- Levantar Alwa:
```sh
cd Alwa-Flask/app
docker-compose up
```