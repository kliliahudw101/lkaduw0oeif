import sqlite3
import os
from utils.logger import log_error, log_info

class SiteOracle:
    """System 1: Site Intelligence & Persistence (SiteOracle)"""
    def __init__(self, db_path="xsstriker/reports/site_oracle.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initializes the persistent SQLite database."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Table for URLs and their basic info
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE,
                method TEXT,
                status_code INTEGER,
                content_type TEXT,
                last_scanned TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Table for Injection Points (Parameters, Forms)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS injection_points (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url_id INTEGER,
                name TEXT,
                type TEXT, -- 'url_param', 'form_input', 'header', 'cookie'
                reflected BOOLEAN,
                sanitization_pattern TEXT,
                FOREIGN KEY (url_id) REFERENCES urls (id),
                UNIQUE(url_id, name, type)
            )
        ''')

        # Table for JS Sinks found on pages
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS js_sinks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url_id INTEGER,
                sink_type TEXT,
                source_code TEXT,
                line_number INTEGER,
                FOREIGN KEY (url_id) REFERENCES urls (id)
            )
        ''')

        conn.commit()
        conn.close()

    def save_url(self, url, method="GET", status_code=None, content_type=None):
        """Saves or updates a URL in the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO urls (url, method, status_code, content_type)
                VALUES (?, ?, ?, ?)
            ''', (url, method, status_code, content_type))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            log_error(f"SiteOracle Error (save_url): {e}")
            return None
        finally:
            conn.close()

    def save_injection_point(self, url, name, point_type, reflected=False, sanitization=None):
        """Saves an injection point linked to a URL."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            # Get URL ID
            cursor.execute('SELECT id FROM urls WHERE url = ?', (url,))
            row = cursor.fetchone()
            if not row:
                url_id = self.save_url(url)
            else:
                url_id = row[0]

            cursor.execute('''
                INSERT OR REPLACE INTO injection_points (url_id, name, type, reflected, sanitization_pattern)
                VALUES (?, ?, ?, ?, ?)
            ''', (url_id, name, point_type, reflected, sanitization))
            conn.commit()
        except Exception as e:
            log_error(f"SiteOracle Error (save_injection_point): {e}")
        finally:
            conn.close()

    def get_all_vectors(self):
        """Retrieves all stored injection points for scanning."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        vectors = []
        try:
            cursor.execute('''
                SELECT u.url, u.method, ip.name, ip.type, ip.sanitization_pattern
                FROM urls u
                JOIN injection_points ip ON u.id = ip.url_id
            ''')
            rows = cursor.fetchall()
            for row in rows:
                vectors.append({
                    "url": row[0],
                    "method": row[1],
                    "param": row[2],
                    "type": row[3],
                    "sanitization": row[4]
                })
        except Exception as e:
            log_error(f"SiteOracle Error (get_all_vectors): {e}")
        finally:
            conn.close()
        return vectors

if __name__ == "__main__":
    oracle = SiteOracle()
    oracle.save_url("http://example.com")
    oracle.save_injection_point("http://example.com", "q", "url_param")
    print(oracle.get_all_vectors())
