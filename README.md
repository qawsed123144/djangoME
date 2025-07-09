# Django 後端專案 - 整合 MySQL + Elasticsearch

本專案為基於 Django 建構的後端系統，核心目標為實現資料儲存與全文檢索整合
 **MySQL** 作為關聯式資料庫 + **Elasticsearch (ES)** 作為檢索引擎。

---

## 專案架構特色

- Django ORM 管理模型、驗證、查詢與資料關聯
- 資料儲存使用 **MySQL**
- 搜尋功能整合 **Elasticsearch**
- 可透過 RESTful API 實作 JSON 查詢與索引
- 可擴充 JWT 認證、背景任務（Celery）、Redis 快取等模組

---

## 環境安裝

```bash
# 建立虛擬環境
python3 -m venv myenv
source myenv/bin/activate

# 安裝依賴
pip install -r requirements.txt

```

---

## MySQL

### 1. 建立資料庫（MySQL shell）
```sql
CREATE DATABASE myproject CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. 修改 `settings.py`
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'myproject',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 3. 安裝驅動
```bash
pip install mysqlclient
```

### 4. 建立資料表
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. 可查看對應 SQL 語法
```bash
python manage.py sqlmigrate app_name 0001
```

---

## Elasticsearch

### 1. 安裝 ES Python 客戶端
```bash
pip install elasticsearch
```

### 2. 範例 `es.py`
```python
from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")

def index_article(index, doc_id, body):
    es.index(index=index, id=doc_id, body=body)

def search_articles(index, query):
    return es.search(index=index, query={"match": {"content": query}})
```

### 3. 與 Django 整合
- 在 `views.py` 中使用 ES 函式處理 POST / GET 搜尋。
- 在 `serializer.py` 中將模型資料轉換為可索引格式。
- 可手動或在信號（signals）中同步 MySQL 與 Elasticsearch。

---

##  API 介面說明

| Method | Endpoint                           | 功能         |
|--------|------------------------------------|--------------|
| GET    | `/library/esearch/?q=企鵝`         | 搜尋文章     |
| POST   | `/library/articles/`               | 新增文章至 ES |
| GET    | `/library/articles/`               | 取得所有文章 |

---

## 測試與假資料匯入

### 建立 Superuser
```bash
python manage.py createsuperuser
```

### 匯入假資料
- 使用 [Mockaroo](https://mockaroo.com) 匯出 SQL，於 MySQL shell：
```sql
SOURCE /path/to/mock_data.sql;
```

### 測試 ES 查詢
```bash
curl -X GET "http://localhost:9200/articles/_search?q=關鍵字"
```

### 查看 mapping 結構
```bash
curl -X GET "http://localhost:9200/articles/_mapping"
```

---

## CORS 設定（供前端跨域請求）
```bash
pip install django-cors-headers
```

`settings.py` 中新增：
```python
INSTALLED_APPS = [
    ...
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    ...
]

CORS_ALLOW_ALL_ORIGINS = True  # 開發環境使用
```

---

## 🧱 技術堆疊

| 類別     | 技術           |
|----------|----------------|
| 後端框架 | Django 4.x     |
| 資料庫   | MySQL 5.7+     |
| 搜尋引擎 | Elasticsearch 7.x+ |
| API 工具 | Django REST Framework |
| 驅動     | mysqlclient、elasticsearch-py |
| 補充     | django-cors-headers（跨域） |

---

## 📁 其他說明（可選擇性擴充）

- JWT 認證（建議使用 djoser）
- Docker + Redis 快取
- Email 測試（smtp4dev）
- Celery 非同步任務
- Pytest 測試 + Locust 壓力測試

---

## 📌 備註

- 請確認本地 `Elasticsearch` 已啟動於 `localhost:9200`
- 本專案為純後端 API，前端建議搭配 Next.js/React 以實現完整全文檢索功能
- 若需支援多語或中文斷詞建議另行安裝相關 ES 分詞器（如 ik_max_word）

---

##  .gitignore 建議設定

若本專案使用 Git 進行版本控管，建議建立 `.gitignore` 檔案並加入以下排除項目：

```gitignore
# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd
*.egg
*.egg-info/
.Python
env/
venv/
myenv/
pip-log.txt
pip-delete-this-directory.txt

# Django
*.sqlite3
db.sqlite3
media/
staticfiles/
*.log

# VSCode
.vscode/

# MacOS
.DS_Store
```
