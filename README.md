# canchas
Sistema para reservas de canchas deportivas. Talana

## Instrucciones para su ejecución
```bash
git clone https://github.com/overflow/canchas.git 
cd canchas
docker-compose up -d 
docker exec -i canchas python manage.py create_user EMAIL PASSWORD
```
La aplicación estará disponible en http://localhost:8080
