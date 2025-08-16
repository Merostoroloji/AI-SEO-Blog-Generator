"""
WordPress REST API Service - Full Implementation
JWT ve Basic Auth destekli
"""

import requests
import json
import base64
from typing import Dict, Any, Optional, List
from datetime import datetime

class WordPressAPI:
    def __init__(self, url: str, username: str, password: str, use_jwt: bool = False):
        """
        WordPress API bağlantısı
        
        Args:
            url: WordPress site URL
            username: Admin kullanıcı adı
            password: Admin şifresi
            use_jwt: JWT kullan (default: False, Basic Auth kullanır)
        """
        self.base_url = url.rstrip('/')
        self.api_url = f"{self.base_url}/wp-json/wp/v2"
        self.username = username
        self.password = password
        self.use_jwt = use_jwt
        
        if use_jwt:
            self.token = self._get_jwt_token()
            self.headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }
        else:
            # Basic Authentication
            credentials = f"{username}:{password}"
            encoded = base64.b64encode(credentials.encode()).decode('ascii')
            self.headers = {
                'Authorization': f'Basic {encoded}',
                'Content-Type': 'application/json'
            }
    
    def _get_jwt_token(self) -> str:
        """JWT token al"""
        response = requests.post(
            f"{self.base_url}/wp-json/jwt-auth/v1/token",
            json={
                'username': self.username,
                'password': self.password
            }
        )
        if response.status_code == 200:
            return response.json()['token']
        raise Exception(f"JWT token alınamadı: {response.text}")
    
    def test_connection(self) -> bool:
        """Bağlantıyı test et"""
        try:
            response = requests.get(f"{self.api_url}/posts", headers=self.headers)
            print(f"Connection test: {response.status_code}")
            return response.status_code == 200
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def create_post(self,
                   title: str,
                   content: str,
                   status: str = 'draft',
                   excerpt: str = '',
                   categories: List[int] = None,
                   tags: List[int] = None,
                   featured_media: int = 0,
                   meta: Dict = None) -> Dict[str, Any]:
        """
        WordPress'te post oluştur
        
        Args:
            title: Başlık
            content: İçerik (HTML)
            status: draft/publish/private
            excerpt: Özet
            categories: Kategori ID'leri
            tags: Etiket ID'leri
            featured_media: Öne çıkan görsel ID
            meta: Meta veriler (Yoast SEO vs.)
        """
        
        post_data = {
            'title': title,
            'content': content,
            'status': status,
            'excerpt': excerpt,
            'categories': categories or [],
            'tags': tags or [],
            'featured_media': featured_media
        }
        
        if meta:
            post_data['meta'] = meta
        
        response = requests.post(
            f"{self.api_url}/posts",
            headers=self.headers,
            json=post_data
        )
        
        if response.status_code == 201:
            created_post = response.json()
            print(f"✅ Post created: {created_post['link']}")
            return created_post
        else:
            raise Exception(f"Post creation failed: {response.status_code} - {response.text}")
    
    def upload_media(self, file_path: str, alt_text: str = '') -> int:
        """
        Medya yükle
        
        Returns:
            Media ID
        """
        with open(file_path, 'rb') as file:
            files = {'file': file}
            headers = self.headers.copy()
            headers.pop('Content-Type')  # Let requests set this
            
            response = requests.post(
                f"{self.api_url}/media",
                headers=headers,
                files=files
            )
            
            if response.status_code == 201:
                media = response.json()
                media_id = media['id']
                
                # Alt text ekle
                if alt_text:
                    self.update_media(media_id, {'alt_text': alt_text})
                
                return media_id
            else:
                raise Exception(f"Media upload failed: {response.text}")
    
    def update_media(self, media_id: int, data: Dict) -> bool:
        """Medya güncelle"""
        response = requests.post(
            f"{self.api_url}/media/{media_id}",
            headers=self.headers,
            json=data
        )
        return response.status_code == 200
    
    def create_category(self, name: str, description: str = '') -> int:
        """Kategori oluştur"""
        response = requests.post(
            f"{self.api_url}/categories",
            headers=self.headers,
            json={'name': name, 'description': description}
        )
        if response.status_code == 201:
            return response.json()['id']
        return 0
    
    def create_tag(self, name: str) -> int:
        """Etiket oluştur"""
        response = requests.post(
            f"{self.api_url}/tags",
            headers=self.headers,
            json={'name': name}
        )
        if response.status_code == 201:
            return response.json()['id']
        return 0

# Test fonksiyonu
def test_wordpress_connection():
    """WordPress bağlantısını test et"""
    
    print("🔌 WordPress Connection Test")
    print("-" * 40)
    
    # BURAYA BİLGİLERİNİZİ GİRİN
    wp = WordPressAPI(
        url="http://localhost/wordpress",
        username="admin",
        password="2025*Ommer.",  # ← ŞİFRENİZİ GİRİN!
        use_jwt=False  # Basic Auth kullan
    )
    
    # Bağlantı testi
    if wp.test_connection():
        print("✅ Bağlantı başarılı!")
        
        # Test postu oluştur
        test_post = wp.create_post(
            title="Test Post from Python",
            content="<p>This is a <strong>test post</strong> created via REST API!</p>",
            status="draft",
            excerpt="Test excerpt"
        )
        
        print(f"✅ Test post oluşturuldu!")
        print(f"📝 Post ID: {test_post['id']}")
        print(f"🔗 Edit URL: http://localhost/wordpress/wp-admin/post.php?post={test_post['id']}&action=edit")
        
    else:
        print("❌ Bağlantı başarısız! Şifrenizi kontrol edin.")

if __name__ == "__main__":
    test_wordpress_connection()
