# isi-TrainerTrade
Repositorio para las practicas de Integración de los sistemas informáticos

COMO INICIAR EL SERVICIO
En una terminal dentro de la carpeta tienes que poner el comando "docker-compose up --build y si no ha ningun error se inicia el servicio en la direccion 127.0.0.1/8000. si ocurre algun error puede ocurrir por que los contenedores esten llenos por lo que habria que utilizar los comandos "docker-compose down --volumes --remove-orphans"" y "docker system prune -a -f". esto sirve para borrar el contenido de los contenedores y hay que volver a hacer el primer comando y tendría que funcionar
