docker network create reseau
docker build -t mysqldb -f ./docker/dockerfile.mysql .
docker build -t phpmyadmin -f ./docker/dockerfile.phpmyadmin .

docker run -d \
  --name mysql_cont \
  --network reseau \
  --env-file .env \
  -p 3306:3306 \
  -v mysql_data:/var/lib/mysql \
  mysqldb

docker run -d \
  --name phpmyadmin_cont \
  --network reseau \
  -p 8080:80 \
  phpmyadmin

docker run --env-file .env --network reseau exam_bloc2_2-ingestion
#host: (nom container) mysql_cont
docker ps
docker logs mysql_cont


# nettyer
docker stop mysql_cont phpmyadmin_cont
docker rm mysql_cont phpmyadmin_cont
docker network rm reseau
docker volume rm mysql_data 