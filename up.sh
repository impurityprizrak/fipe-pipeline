VOLUME_NAME="fipe_data"

if docker volume ls -q | grep -q "^$VOLUME_NAME$"; then
    echo "Volume $VOLUME_NAME already exists."
else
    docker volume create $VOLUME_NAME
    echo "Volume $VOLUME_NAME created"
fi

docker compose -f docker-compose.yaml up