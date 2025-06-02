from typing import List, Dict, Any, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
import os

class GoogleSearch:
    def __init__(self, api_key: str, search_engine_id: str):
        """
        Khởi tạo Google Custom Search API client
        
        Args:
            api_key (str): Google API key
            search_engine_id (str): Custom Search Engine ID
        """
        self.api_key = api_key
        self.search_engine_id = search_engine_id
        self.service = build("customsearch", "v1", developerKey=self.api_key)

    async def search(
        self, 
        query: str,
        num_results: int = 5,
        language: str = "vi",
        safe: str = "off",
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Thực hiện tìm kiếm với Google Custom Search API
        
        Args:
            query (str): Query tìm kiếm
            num_results (int): Số lượng kết quả mong muốn (max 10)
            language (str): Ngôn ngữ tìm kiếm (default: Vietnamese)
            safe (str): SafeSearch setting ("off", "medium", "high")
            **kwargs: Các tham số tìm kiếm bổ sung
            
        Returns:
            List[Dict[str, Any]]: Danh sách kết quả tìm kiếm đã được format
        """
        try:
            # Đảm bảo số lượng kết quả không vượt quá giới hạn API
            num_results = min(num_results, 10)
            
            # Thực hiện tìm kiếm
            result = self.service.cse().list(
                q=query,
                cx=self.search_engine_id,
                num=num_results,
                lr=f"lang_{language}",
                safe=safe,
                **kwargs
            ).execute()

            # Format kết quả
            if "items" in result:
                return self.format_results(result["items"])
            return []

        except HttpError as e:
            error_details = json.loads(e.content.decode())
            raise Exception(f"Google Search API error: {error_details.get('error', {}).get('message')}")
        except Exception as e:
            raise Exception(f"Error performing search: {str(e)}")

    def format_results(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format kết quả tìm kiếm
        
        Args:
            items (List[Dict[str, Any]]): Raw search results
            
        Returns:
            List[Dict[str, Any]]: Formatted search results
        """
        formatted_results = []
        
        for item in items:
            formatted_result = {
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "snippet": item.get("snippet", ""),
                "displayed_link": item.get("formattedUrl", ""),
                "type": "webpage"
            }
            
            # Add thumbnail if available
            if "pagemap" in item and "cse_thumbnail" in item["pagemap"]:
                formatted_result["thumbnail"] = item["pagemap"]["cse_thumbnail"][0].get("src")
                
            # Determine content type if possible
            if "pagemap" in item:
                if "metatags" in item["pagemap"]:
                    content_type = item["pagemap"]["metatags"][0].get("og:type")
                    if content_type:
                        formatted_result["type"] = content_type
                        
            formatted_results.append(formatted_result)
            
        return formatted_results

    async def search_news(
        self,
        query: str,
        num_results: int = 5,
        language: str = "vi"
    ) -> List[Dict[str, Any]]:
        """
        Tìm kiếm tin tức
        
        Args:
            query (str): Query tìm kiếm
            num_results (int): Số lượng kết quả mong muốn
            language (str): Ngôn ngữ tìm kiếm
            
        Returns:
            List[Dict[str, Any]]: Danh sách tin tức
        """
        # Thêm parameter tbm=nws để tìm kiếm tin tức
        return await self.search(
            query,
            num_results=num_results,
            language=language,
            tbm="nws"
        )

    async def search_images(
        self,
        query: str,
        num_results: int = 5,
        language: str = "vi"
    ) -> List[Dict[str, Any]]:
        """
        Tìm kiếm hình ảnh
        
        Args:
            query (str): Query tìm kiếm
            num_results (int): Số lượng kết quả mong muốn
            language (str): Ngôn ngữ tìm kiếm
            
        Returns:
            List[Dict[str, Any]]: Danh sách hình ảnh
        """
        # Thêm parameter tbm=isch để tìm kiếm hình ảnh
        return await self.search(
            query,
            num_results=num_results,
            language=language,
            tbm="isch"
        )

    @staticmethod
    def from_env() -> 'GoogleSearch':
        """
        Tạo instance từ environment variables
        
        Returns:
            GoogleSearch: Instance được cấu hình từ env vars
            
        Raises:
            ValueError: Nếu thiếu các required env vars
        """
        api_key = os.getenv("GOOGLE_API_KEY")
        search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
        
        if not api_key or not search_engine_id:
            raise ValueError(
                "Missing required environment variables: "
                "GOOGLE_API_KEY, GOOGLE_SEARCH_ENGINE_ID"
            )
            
        return GoogleSearch(api_key, search_engine_id)
