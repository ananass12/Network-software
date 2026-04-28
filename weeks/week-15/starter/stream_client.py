import grpc
import service_pb2 as pb2
import service_pb2_grpc as pb2_grpc

channel = grpc.insecure_channel('localhost:8174')
stub = pb2_grpc.LikesServiceStub(channel)

print("Подписка на лайки...")
for update in stub.SubscribeLikes(pb2.SubscribeRequest(target="post_123")):
    print(f" Like: {update.like_id} → {update.target}")