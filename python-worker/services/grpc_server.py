# python-worker/services/grpc_server.py
import grpc
from concurrent import futures
import time
from protos import market_pb2_grpc
from services.price_predictor import PricePredictor
from services.anomaly_detector import AnomalyDetector
import logging

class MarketServicer(market_pb2_grpc.MarketServiceServicer):
    """GRPC server for market prediction services"""
    
    def __init__(self):
        self.predictor = PricePredictor()
        self.anomaly_detector = AnomalyDetector()
        
    def PredictPrice(self, request, context):
        """Predict price for given token pair"""
        try:
            prediction = self.predictor.predict(
                request.token_pair, 
                request.history_data
            )
            return market_pb2.PriceResponse(
                success=True,
                predicted_price=prediction['price'],
                confidence=prediction['confidence']
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return market_pb2.PriceResponse(success=False)
            
    def DetectAnomaly(self, request, context):
        """Detect anomalies in market data"""
        try:
            result = self.anomaly_detector.detect(
                request.market_data
            )
            return market_pb2.AnomalyResponse(
                success=True,
                is_anomaly=result['is_anomaly'],
                severity=result['severity']
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return market_pb2.AnomalyResponse(success=False)

def serve():
    """Start GRPC server"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    market_pb2_grpc.add_MarketServiceServicer_to_server(
        MarketServicer(), server
    )
    server.add_insecure_port('[::]:50051')
    server.start()
    logging.info("GRPC Server started on port 50051")
    
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    serve()