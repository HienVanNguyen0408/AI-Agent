from typing import Dict, Any, List, Optional
from pymongo import MongoClient
from datetime import datetime

class MongoDBMemory:
    def __init__(self, connection_string: str = "mongodb://localhost:27017/"):
        """
        Khởi tạo kết nối MongoDB Memory Storage
        
        Args:
            connection_string (str): MongoDB connection string
        """
        self.client = MongoClient(connection_string)
        self.db = self.client["ai_memory"]
        self.collection = self.db["memories"]
        
        # Tạo index cho các trường thường được query
        self.collection.create_index([("timestamp", -1)])
        self.collection.create_index([("type", 1)])
        self.collection.create_index([("conversation_id", 1)])

    async def store(self, data: Dict[str, Any]) -> str:
        """
        Lưu memory vào MongoDB
        
        Args:
            data (Dict[str, Any]): Data cần lưu
            
        Returns:
            str: ID của document đã lưu
        """
        # Thêm timestamp
        data["timestamp"] = datetime.utcnow()
        
        # Insert vào MongoDB
        result = self.collection.insert_one(data)
        return str(result.inserted_id)

    async def retrieve(self, query: Dict[str, Any], limit: int = 10) -> List[Dict[str, Any]]:
        """
        Truy xuất memory từ MongoDB
        
        Args:
            query (Dict[str, Any]): Query điều kiện
            limit (int): Số lượng kết quả tối đa
            
        Returns:
            List[Dict[str, Any]]: Danh sách memories tìm được
        """
        cursor = self.collection.find(query).sort("timestamp", -1).limit(limit)
        return [doc for doc in cursor]

    async def update(self, query: Dict[str, Any], data: Dict[str, Any]) -> int:
        """
        Cập nhật memory
        
        Args:
            query (Dict[str, Any]): Query điều kiện
            data (Dict[str, Any]): Data cần update
            
        Returns:
            int: Số lượng documents đã update
        """
        # Thêm updated_at timestamp
        data["updated_at"] = datetime.utcnow()
        
        result = self.collection.update_many(query, {"$set": data})
        return result.modified_count

    async def delete(self, query: Dict[str, Any]) -> int:
        """
        Xóa memory
        
        Args:
            query (Dict[str, Any]): Query điều kiện
            
        Returns:
            int: Số lượng documents đã xóa
        """
        result = self.collection.delete_many(query)
        return result.deleted_count

    async def search_by_timerange(
        self, 
        start_time: datetime, 
        end_time: datetime, 
        memory_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Tìm kiếm memory theo khoảng thời gian
        
        Args:
            start_time (datetime): Thời gian bắt đầu
            end_time (datetime): Thời gian kết thúc
            memory_type (Optional[str]): Loại memory cần tìm
            limit (int): Số lượng kết quả tối đa
            
        Returns:
            List[Dict[str, Any]]: Danh sách memories tìm được
        """
        query = {
            "timestamp": {
                "$gte": start_time,
                "$lte": end_time
            }
        }
        
        if memory_type:
            query["type"] = memory_type
            
        cursor = self.collection.find(query).sort("timestamp", -1).limit(limit)
        return [doc for doc in cursor]

    def close(self):
        """Đóng kết nối MongoDB"""
        self.client.close()
