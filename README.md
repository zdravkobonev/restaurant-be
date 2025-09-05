# CloudTouchSale

TAG=$(cat VERSION)
IMAGE="ghcr.io/zdravkobonev/restaurant-be:$TAG"

# билд на новия образ
docker build -t "$IMAGE" .

# push към GHCR
docker push "$IMAGE"
sssss