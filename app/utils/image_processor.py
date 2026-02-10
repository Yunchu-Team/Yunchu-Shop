import os
import base64
import uuid
import requests
from PIL import Image
from flask import current_app
from app.models import SiteSetting
from app.utils.crypto import decrypt_text

class ImageProcessor:
    def __init__(self, upload_folder):
        self.upload_folder = upload_folder
    
    def allowed_file(self, filename):
        """检查文件类型是否允许"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}
    
    def generate_thumbnail(self, image_path, output_path, size=(150, 150)):
        """生成缩略图"""
        try:
            with Image.open(image_path) as img:
                img.thumbnail(size)
                img.save(output_path)
            return True
        except Exception as e:
            print(f"生成缩略图失败: {e}")
            return False
    
    def process_uploaded_image(self, file, subfolder):
        """处理上传的图片"""
        if not self.allowed_file(file.filename):
            return None

        # 优先走 GitHub；未配置时回退到本地保存
        setting = SiteSetting.get()
        if setting.gh_repo and setting.gh_token_enc:
            token = decrypt_text(setting.gh_token_enc, current_app.config['SECRET_KEY'])
            return self._upload_to_github(file, subfolder, setting.gh_repo, setting.gh_branch or 'main', token)
        
        # 确保子文件夹存在
        folder_path = os.path.join(self.upload_folder, subfolder)
        os.makedirs(folder_path, exist_ok=True)
        
        # 生成唯一文件名
        ext = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{ext}"
        file_path = os.path.join(folder_path, unique_filename)
        
        # 保存原始图片
        file.save(file_path)
        
        # 生成缩略图
        thumb_folder = os.path.join(folder_path, 'thumbs')
        os.makedirs(thumb_folder, exist_ok=True)
        thumb_path = os.path.join(thumb_folder, unique_filename)
        self.generate_thumbnail(file_path, thumb_path)
        
        # 返回相对路径（统一使用URL分隔符）
        return os.path.join(subfolder, unique_filename).replace('\\', '/')
    
    def delete_image(self, image_path):
        """删除图片及其缩略图"""
        try:
            if image_path.startswith('http://') or image_path.startswith('https://'):
                return True
            # 删除原始图片
            full_path = os.path.join(self.upload_folder, image_path)
            if os.path.exists(full_path):
                os.remove(full_path)
            
            # 删除缩略图
            thumb_path = os.path.join(self.upload_folder, os.path.dirname(image_path), 'thumbs', os.path.basename(image_path))
            if os.path.exists(thumb_path):
                os.remove(thumb_path)
            
            return True
        except Exception as e:
            print(f"删除图片失败: {e}")
            return False

    def _upload_to_github(self, file, subfolder, repo, branch, token):
        ext = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{ext}"
        path = f"uploads/{subfolder}/{unique_filename}"

        content_bytes = file.read()
        file.seek(0)
        content_b64 = base64.b64encode(content_bytes).decode('utf-8')

        api_url = f"https://api.github.com/repos/{repo}/contents/{path}"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json"
        }
        payload = {
            "message": f"upload {path}",
            "content": content_b64,
            "branch": branch
        }

        resp = requests.put(api_url, json=payload, headers=headers, timeout=20)
        if resp.status_code not in (200, 201):
            raise RuntimeError(f"GitHub上传失败: {resp.status_code} {resp.text}")

        data = resp.json()
        return data.get('content', {}).get('download_url')
