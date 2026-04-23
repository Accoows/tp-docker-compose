#!/bin/bash

ENV_FILE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/.env"

if [ -f "$ENV_FILE" ]; then
    export $(sed 's/\r$//' "$ENV_FILE" | grep -v '^#' | xargs)
fi

CONTAINER_NAME="mongo-blog"
DB_NAME="${MONGODB_INITDB_DATABASE:-blog_db}"
ROOT_USERNAME="$MONGODB_INITDB_ROOT_USERNAME"
ROOT_PASSWORD="$MONGODB_INITDB_ROOT_PASSWORD"

mongo_eval() {
    docker exec "$CONTAINER_NAME" mongosh \
        -u "$ROOT_USERNAME" \
        -p "$ROOT_PASSWORD" \
        --authenticationDatabase admin \
        --quiet --eval "$1"
}

if [ -z "$ROOT_USERNAME" ] || [ -z "$ROOT_PASSWORD" ]; then
    echo "ERREUR: Variables manquantes dans .env"
    echo "Attendu: MONGODB_INITDB_ROOT_USERNAME et MONGODB_INITDB_ROOT_PASSWORD"
    exit 1
fi

echo "--- Vérification de l'utilisateur interne ---"
USER_ID=$(docker exec $CONTAINER_NAME id -u)
if [ "$USER_ID" != "0" ]; then
    echo "SUCCÈS: Le service tourne avec l'UID: $USER_ID (Non-root)" 
else
    echo "ERREUR: Le service tourne en ROOT !" 
    exit 1
fi

echo "--- Vérification de la base $DB_NAME ---"
COUNT_QUERY="db.getSiblingDB('$DB_NAME').posts.countDocuments()"
QUERY_COUNT=$(mongo_eval "$COUNT_QUERY")

if [[ "$QUERY_COUNT" =~ ^[0-9]+$ ]] && [ "$QUERY_COUNT" -ge 5 ]; then
        echo "SUCCÈS: Base accessible, $QUERY_COUNT documents trouvés."
else
        echo "ERREUR: Accès refusé ou données manquantes (Reçu: $QUERY_COUNT)"
    exit 1
fi

echo "--- Contenu de posts ---"
POSTS_QUERY="db.getSiblingDB('$DB_NAME').posts.find().forEach(function(p){printjson(p);})"
mongo_eval "$POSTS_QUERY"